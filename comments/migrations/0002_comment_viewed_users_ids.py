# Generated by Django 4.2.13 on 2024-06-22 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='viewed_users_ids',
            field=models.JSONField(default=[]),
        ),
    ]
