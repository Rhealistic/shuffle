# Generated by Django 4.2.6 on 2024-02-29 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0019_rename_chosen_shuffle_pick'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='last_shuffle',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='next_shuffle',
        ),
        migrations.AddField(
            model_name='curator',
            name='last_shuffle',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='curator',
            name='next_shuffle',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]