# Generated by Django 4.2.6 on 2024-02-13 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0012_remove_artist_invite_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opportunity',
            name='invite_status',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='opportunity_status',
        ),
        migrations.AddField(
            model_name='artist',
            name='selection_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='accepted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='expired_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='skipped_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Potential'), (1, 'Waiting Approval'), (2, 'Next Performing'), (3, 'Performed'), (4, 'Next Cycle'), (5, 'Skip'), (6, 'Expired')], default=1, null=True),
        ),
    ]