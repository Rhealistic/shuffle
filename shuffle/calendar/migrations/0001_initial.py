# Generated by Django 4.2.6 on 2024-02-24 18:03

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artist', '0022_opportunity_closed_at_opportunity_outcome_status_and_more'),
        ('venue', '0001_initial'),
        ('curator', '0017_remove_concept_poster_alter_curator_curator_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('title', models.CharField(max_length=150)),
                ('description', models.CharField(max_length=500)),
                ('poster', models.URLField(blank=True, max_length=500, null=True)),
                ('event_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('concept', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='curator.concept')),
                ('opportunity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='artist.opportunity')),
                ('venue', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='venues', to='venue.venue')),
            ],
        ),
    ]