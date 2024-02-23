# Generated by Django 4.2.6 on 2024-02-23 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0019_remove_artist_acceptance_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='artist.artist'),
        ),
    ]
