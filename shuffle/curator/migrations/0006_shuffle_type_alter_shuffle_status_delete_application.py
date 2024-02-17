# Generated by Django 4.2.6 on 2024-02-12 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0005_alter_concept_poster'),
    ]

    operations = [
        migrations.AddField(
            model_name='shuffle',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Normal'), (1, 'Reshuffle')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='shuffle',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Started'), (1, 'In Progress'), (2, 'Complete')], default=0),
        ),
        migrations.DeleteModel(
            name='Application',
        ),
    ]
