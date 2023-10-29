# Generated by Django 4.2.6 on 2023-10-27 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wordpress', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='content',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='password',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='status',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='tags',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='title',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='username',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
