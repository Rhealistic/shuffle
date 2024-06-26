# Generated by Django 4.2.6 on 2024-02-12 12:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0011_opportunity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='invite_status',
        ),
        migrations.RemoveField(
            model_name='artist',
            name='opportunity_status',
        ),
        migrations.AddField(
            model_name='opportunity',
            name='invite_status',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Accepted'), (2, 'Rejected'), (3, 'Unavailable')], null=True),
        ),
        migrations.AddField(
            model_name='opportunity',
            name='opportunity_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Potential'), (1, 'Waiting Approval'), (2, 'Next Performing'), (3, 'Performed'), (4, 'Next Cycle'), (5, 'Skip')], default=1, null=True),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='artists', to='artist.artist'),
        ),
    ]
