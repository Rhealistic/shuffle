# Generated by Django 4.2.6 on 2024-02-28 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendar', '0004_rename_event_date_event_start_remove_event_end_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
        migrations.RemoveField(
            model_name='event',
            name='poster',
        ),
        migrations.RemoveField(
            model_name='event',
            name='title',
        ),
    ]
