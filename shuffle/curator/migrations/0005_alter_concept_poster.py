# Generated by Django 4.2.6 on 2023-12-20 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0004_curator_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='poster',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
