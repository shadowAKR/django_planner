# Generated by Django 4.2.13 on 2024-06-16 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='planned_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='planned_start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
