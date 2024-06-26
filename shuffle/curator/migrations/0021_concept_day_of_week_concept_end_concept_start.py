# Generated by Django 4.2.6 on 2024-02-29 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0020_remove_organization_last_shuffle_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='concept',
            name='day_of_week',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')], null=True),
        ),
        migrations.AddField(
            model_name='concept',
            name='end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='concept',
            name='start',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
