# Generated by Django 4.2.6 on 2024-03-05 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0032_alter_opportunity_reject_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='shuffle_id',
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
    ]
