# Generated by Django 4.2.6 on 2024-02-26 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0023_rename_closed_at_opportunity_invite_closed_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunity',
            name='invite_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='invite_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1, 'Sent'), (2, 'Awaiting Acceptance'), (3, 'Accepted'), (4, 'Skipped'), (5, 'Expired')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='outcome_status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1, 'Sent'), (2, 'Cancelled'), (3, 'Postponed'), (4, 'Failed')], null=True),
        ),
    ]