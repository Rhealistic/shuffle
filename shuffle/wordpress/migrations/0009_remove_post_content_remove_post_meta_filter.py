# Generated by Django 4.2.6 on 2023-10-29 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0008_post_post_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='content',
        ),
        migrations.RemoveField(
            model_name='post',
            name='meta_filter',
        ),
    ]
