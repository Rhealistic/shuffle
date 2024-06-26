# Generated by Django 4.2.6 on 2024-03-07 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0043_alter_concept_concept_id_alter_config_config_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='concept',
            name='recurrence_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Daily'), (1, 'Weekly'), (2, 'Bieekly'), (3, 'Monthly'), (4, 'Quarterly')], null=True),
        ),
    ]
