# Generated by Django 4.2.6 on 2024-02-29 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calendar', '0005_remove_event_description_remove_event_poster_and_more'),
        ('artist', '0026_rename_invite_closed_at_opportunity_closed_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opportunity',
            old_name='invite_status',
            new_name='status',
        ),
        migrations.AlterField(
            model_name='opportunity',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='concept_opportunities', related_query_name='concept_opportunity', to='calendar.event'),
        ),
    ]