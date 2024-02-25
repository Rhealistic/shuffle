# Generated by Django 4.2.6 on 2024-02-24 18:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0016_alter_shuffle_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concept',
            name='poster',
        ),
        migrations.AlterField(
            model_name='curator',
            name='curator_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='organization_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='shuffle',
            name='shuffle_id',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
