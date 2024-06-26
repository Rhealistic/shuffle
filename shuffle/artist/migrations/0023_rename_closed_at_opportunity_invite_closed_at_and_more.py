# Generated by Django 4.2.6 on 2024-02-25 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curator', '0017_remove_concept_poster_alter_curator_curator_id_and_more'),
        ('calendar', '0003_remove_event_artist_remove_event_concept_and_more'),
        ('artist', '0022_opportunity_closed_at_opportunity_outcome_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='opportunity',
            old_name='closed_at',
            new_name='invite_closed_at',
        ),
        migrations.RenameField(
            model_name='opportunity',
            old_name='accepted_at',
            new_name='opportunity_closed_at',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='expired_at',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='previous_opportunity_id',
        ),
        migrations.RemoveField(
            model_name='opportunity',
            name='skipped_at',
        ),
        migrations.AddField(
            model_name='opportunity',
            name='event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='calendar.event'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='concept',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='concept_subscriptions', to='curator.concept'),
        ),
    ]
