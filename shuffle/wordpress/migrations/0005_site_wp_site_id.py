# Generated by Django 4.2.6 on 2023-10-27 21:04

from django.db import migrations, models
import shuffle.wordpress.models


class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0004_alter_post_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='wp_site_id',
            field=models.CharField(default=shuffle.wordpress.models.alpha, max_length=32),
        ),
    ]
