# Generated by Django 4.2.6 on 2024-03-07 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0044_alter_concept_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='bio',
            field=models.TextField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='concept',
            name='description',
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name='concept',
            name='slug',
            field=models.SlugField(max_length=75, unique=True),
        ),
        migrations.AlterField(
            model_name='concept',
            name='times_per_month',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='concept',
            name='times_per_week',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
    ]