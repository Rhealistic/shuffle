# Generated by Django 4.2.6 on 2024-03-08 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0045_organization_bio_alter_concept_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shuffle',
            old_name='start_date',
            new_name='start_time',
        ),
        migrations.AlterField(
            model_name='organization',
            name='bio',
            field=models.TextField(max_length=1000, null=True),
        ),
    ]
