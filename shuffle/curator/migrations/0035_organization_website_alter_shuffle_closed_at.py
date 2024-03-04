# Generated by Django 4.2.6 on 2024-03-04 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0034_alter_config_config_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='website',
            field=models.URLField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='shuffle',
            name='closed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]