# Generated by Django 4.2.6 on 2024-02-27 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar', '0003_remove_event_artist_remove_event_concept_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_date',
            new_name='start',
        ),
        migrations.RemoveField(
            model_name='event',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='end_type',
        ),
        migrations.RemoveField(
            model_name='event',
            name='frequency',
        ),
        migrations.RemoveField(
            model_name='event',
            name='is_recurring',
        ),
        migrations.RemoveField(
            model_name='event',
            name='recurrence_type',
        ),
        migrations.AddField(
            model_name='event',
            name='end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1, 'Sent'), (2, 'Cancelled'), (3, 'Rescheduled'), (4, 'Failed')], null=True),
        ),
    ]
