# Generated by Django 4.2.6 on 2024-03-06 14:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0042_alter_shuffle_shuffle_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concept',
            name='concept_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='config_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='curator',
            name='curator_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='organization_id',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
        ),
    ]
