"""
Author: Ananthu Krishnan
Date: 16 June 2024
"""
import logging
import time
import io
import sys
import shlex
from itertools import chain

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)


class ScriptStatus:
    SUCCESS = 1
    FAILED = 0


class Command(BaseCommand):
    help = "Running all one-time scripts of a release in master & clients."

    def add_arguments(self, parser):
        parser.add_argument("--release", nargs="?", type=str, default=None)

    def _run_script(self, script_name):
        """
        Runs a single script.
        """

        original_stdout = sys.stdout
        # To prevent unwanted print statements from printing to terminal.
        sys.stdout = io.TextIOWrapper(io.BytesIO(), sys.stdout.encoding)

        # Parse the command, and make it a list.
        lexer = shlex.shlex(script_name, posix=True)
        lexer.whitespace_split = True
        command = list(lexer)
        command_name = command[0]
        command_args = command[1:]
        try:
            script_out = call_command(command_name, *command_args)
        except Exception as error:
            script_out = "failed"
            logger.exception(error)

        # Captures all the std outs.
        sys.stdout.seek(0)
        standard_out = sys.stdout.read()
        # Reset stdout to original.
        sys.stdout = original_stdout
        # Log the captured stdout.
        logger.info(standard_out)
        return script_out

    def run_script(self, script_name, instance_name, script_index, no_of_scripts):
        """
        Prepares a script for running, and captures the time taken to run the script.
        """

        script_name_length = len(script_name)

        # If the script name is small then show the full name.
        if script_name_length < 85:
            script_name_to_show = script_name
        else:
            # Determine the no of characters to show if script name is long.
            no_of_chars_to_show = 50 if script_name_length > 110 else 40
            script_name_to_show = (
                f"{script_name[:no_of_chars_to_show]}..."
                f"{script_name[-no_of_chars_to_show:]}"
            )

        self.stdout.write(
            f"  {self.style.MIGRATE_HEADING('Running : ')} "
            f"{script_name_to_show}...",
            ending="\r",
        )

        # Clearing the content-type cache.
        ContentType.objects.clear_cache()

        start_time = time.time()
        script_out = self._run_script(script_name)
        end_time = time.time()
        script_out = str(script_out)

        # Clearing the content-type cache.
        ContentType.objects.clear_cache()

        # The below line will clear out the previous output line in terminal.
        self.stdout.write("", ending="\x1b[2K")

        percentage = (script_index / no_of_scripts) * 100
        self.stdout.write(self.style.MIGRATE_LABEL(f"{percentage:06.2f}%  "), ending="")

        # Time taken to run this script.
        time_diff = end_time - start_time
        if time_diff > 10.0:
            style_func = self.style.ERROR  # RED
        elif time_diff > 5.0:
            style_func = self.style.WARNING  # YELLOW
        else:
            style_func = self.style.MIGRATE_LABEL  # WHITE
        self.stdout.write(style_func(f"({time_diff :07.3f} sec)  "), ending="")
        self.stdout.write(f"{script_name_to_show}... ", ending="")

        script_status = ScriptStatus.FAILED
        if (
            script_out.lower() in ("success", "done")
            or "success" in str(script_out).lower()
        ):
            self.stdout.write(self.style.SUCCESS("OK"))
            script_status = ScriptStatus.SUCCESS
        elif script_out in ("", "-", "None", None):
            self.stdout.write(self.style.WARNING("No-Output"))
            script_status = ScriptStatus.SUCCESS
        elif (
            script_out.lower() in ("failed", "error")
            or "failed" in str(script_out).lower()
        ):
            self.stdout.write(self.style.ERROR("FAIL"))
            script_status = ScriptStatus.FAILED
        else:
            self.stdout.write(self.style.WARNING(str(script_out)[:20]))
            script_status = ScriptStatus.SUCCESS
        return (script_out, script_status)

    def handle(self, *args, **options):
        filename = options.get("release")
        script_begin_time = time.time()

        # Appends the master database to the same list
        databases = [
            {
                "name": "Master DB",
                "instance_name": settings.DATABASES["default"]["NAME"],
            }
        ]

        # Read the scripts file and fetch the scripts.
        scripts = []
        with open(
            "scripts/" + filename + ".txt", "r", encoding="utf-8"
        ) as script_file:
            # strip each script's name.
            scripts = filter(bool, map(str.strip, script_file.readlines()))
            # Get the name of this script.
            _this_script = __file__.replace(".py", "").split("/")[-1]
            # And remove it from the scripts. This is to prevent race conditions.
            scripts = list(filter(lambda item: _this_script not in item, scripts))


        no_of_scripts = len(scripts) * len(databases)

        self.stdout.write(
            f"{no_of_scripts} scripts in total.",
            ending="\n",
        )

        failed_scripts = {}

        _script_start_index = 1
        for instance_no, database in enumerate(databases, start=1):

            self.stdout.write(
                f"\nRunning {self.style.MIGRATE_LABEL(filename)}... in "
                f"{self.style.MIGRATE_LABEL(database['instance_name'])}"
                f"  ({self.style.MIGRATE_HEADING(database['name'])}) "
                f"[{instance_no} of {len(databases)}]",
                ending="\n\n",
            )

            # Running each script in loop.
            for _index, script_name in enumerate(scripts, start=_script_start_index):
                if not script_name:
                    continue

                _script_start_index += 1

                # Running script.
                out, status = self.run_script(
                    script_name=script_name,
                    instance_name=database["instance_name"],
                    script_index=_index,
                    no_of_scripts=no_of_scripts,
                )
                # Handle failed scripts.
                if status == ScriptStatus.FAILED:
                    failed_scripts.setdefault(database["instance_name"], []).append(
                        {
                            "script": script_name,
                            "instance": database["instance_name"],
                            "name": database["name"],
                            "out": out,
                        }
                    )

                # Let the RDS breathe.
                time.sleep(0.01)  # 10ms

            # End of scripts loop.
        # End of instance loop.

        if failed_scripts:
            self.stdout.write(
                self.style.ERROR(
                    f"\nFailed scripts : {len(list(chain(*failed_scripts.values())))}"
                )
            )
            script_index = 1
            for instance_name, scripts in failed_scripts.items():
                if not scripts:
                    continue
                self.stdout.write(
                    f"\n{instance_name} ", self.style.MIGRATE_LABEL, ending="\n"
                )
                for script in scripts:
                    self.stdout.write(
                        "  " + str(script_index), self.style.MIGRATE_LABEL, ending=""
                    )
                    self.stdout.write(f") {script['script']} ", ending="\n")
                    script_index += 1
            logger.info(failed_scripts)
        else:
            self.stdout.write(self.style.SUCCESS("\nNo scripts failed."))
        self.stdout.write("\n\n")
        time_diff = time.time() - script_begin_time
        hours = int(time_diff // 3600)
        minutes = int((time_diff % 3600) // 60)
        seconds = int(time_diff % 60)
        self.stdout.write(
            f"Elapsed time : {hours} hours {minutes} minutes {seconds} seconds."
            f"({no_of_scripts} scripts)",
            self.style.MIGRATE_HEADING,
            ending="\n\n\n",
        )
        self.stdout.write("All done \N{winking face} \n")
