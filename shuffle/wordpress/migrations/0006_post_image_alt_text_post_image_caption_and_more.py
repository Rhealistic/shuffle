# Generated by Django 4.2.6 on 2023-10-28 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0005_site_wp_site_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image_alt_text',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='image_caption',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='image_description',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='wp_post_id',
            field=models.IntegerField(null=True),
        ),
    ]