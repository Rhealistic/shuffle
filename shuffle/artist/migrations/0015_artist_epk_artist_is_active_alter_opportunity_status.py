# Generated by Django 4.2.6 on 2024-02-19 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0014_artist_acceptance_count_artist_expired_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='epk',
            field=models.URLField(blank=True, help_text='Link to EPK + Tech rider', null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='is_active',
            field=models.BooleanField(default=True, null=True),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Potential'), (1, 'Waiting Approval'), (2, 'Next Performing'), (3, 'Performed'), (5, 'Skip'), (6, 'Expired')], default=1, null=True),
        ),
    ]
