# Generated by Django 4.2.6 on 2024-02-29 07:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0018_rename_date_concept_start_date_concept_is_recurring_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shuffle',
            old_name='chosen',
            new_name='pick',
        ),
    ]
