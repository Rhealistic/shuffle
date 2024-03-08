# Generated by Django 4.2.6 on 2024-03-08 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0036_alter_artist_bio_alter_opportunity_notes_to_curator'),
        ('curator', '0046_rename_start_date_shuffle_start_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shuffle',
            name='pick',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='artist.subscriber'),
        ),
    ]
