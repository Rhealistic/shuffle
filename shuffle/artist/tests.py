# import random
# from datetime import datetime, timedelta
# from django.utils import timezone

# from .models import Artist, Opportunity, Subscriber

# from ..calendar.models import Event
# from ..curator.models import Concept, Curator, Organization, Shuffle

# def generate_dynamic_test_data():
#     num_entries = random.randint(25, 50)  # Generate a random number of entries between 25 and 50

#     organizations = []
#     curators = []
#     concepts = []
#     artists = []
#     subscribers = []
#     shuffles = []
#     events = []
#     opportunities = []

#     # Create organizations and curators
#     for _ in range(num_entries // 10):  # Splitting the number of entries into 10% for organizations and curators
#         organization = Organization.objects.create(
#             name=f"Test Organization {random.randint(1000, 9999)}",
#             email=f"test{random.randint(1000, 9999)}@example.com",
#             phone=f"{random.randint(1000000000, 9999999999)}"
#         )
#         organizations.append(organization)

#         curator = Curator.objects.create(
#             name=f"Test Curator {random.randint(1000, 9999)}",
#             email=f"curator{random.randint(1000, 9999)}@test.com",
#             phone=f"{random.randint(1000000000, 9999999999)}",
#             organization=organization
#         )
#         curators.append(curator)

#     # Create concepts and artists
#     for _ in range(num_entries // 5):  # Splitting the number of entries into 20% for concepts and artists
#         curator = random.choice(curators)

#         concept = Concept.objects.create(
#             curator=curator,
#             title=f"Test Concept {random.randint(1000, 9999)}",
#             description=f"This is a test concept {random.randint(1000, 9999)}"
#         )
#         concepts.append(concept)

#         artist = Artist.objects.create(
#             name=f"Test Artist {random.randint(1000, 9999)}",
#             bio=f"Test bio for the artist {random.randint(1000, 9999)}",
#             email=f"artist{random.randint(1000, 9999)}@test.com",
#             phone=f"{random.randint(1000000000, 9999999999)}",
#             country="USA"
#         )
#         artists.append(artist)

#     # Create subscribers
#     for _ in range(num_entries // 2):  # Splitting the number of entries into 50% for subscribers
#         concept = random.choice(concepts)
#         artist = random.choice(artists)

#         subscriber = Subscriber.objects.create(
#             concept=concept,
#             artist=artist,
#             status=random.choice([status[0] for status in Subscriber.Status.choices]),
#             is_subscribed=True
#         )
#         subscribers.append(subscriber)

#     # Create shuffles
#     for _ in range(num_entries // 10):  # Splitting the number of entries into 10% for shuffles
#         concept = random.choice(concepts)

#         shuffle = Shuffle.objects.create(
#             concept=concept,
#             status=random.choice([status[0] for status in Shuffle.Status.choices])
#         )
#         shuffles.append(shuffle)

#     # Create events and opportunities
#     for _ in range(num_entries):  # All remaining entries will be events and opportunities
#         subscriber = random.choice(subscribers)
#         concept = random.choice(concepts)

#         event = Event.objects.create(
#             start=generate_random_datetime(),
#             status=random.choice([status[0] for status in Event.Status.choices])
#         )
#         events.append(event)

#         opportunity = Opportunity.objects.create(
#             subscriber=subscriber,
#             event=event,
#             status=random.choice([status[0] for status in Opportunity.Status.choices])
#         )
#         opportunities.append(opportunity)

#     return {
#         'organizations': organizations,
#         'curators': curators,
#         'concepts': concepts,
#         'artists': artists,
#         'subscribers': subscribers,
#         'shuffles': shuffles,
#         'events': events,
#         'opportunities': opportunities
#     }

# def generate_random_datetime():
#     start_date = timezone.now() - timedelta(days=365)  # One year ago
#     end_date = timezone.now() + timedelta(days=365)  # One year in the future
#     return start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))

import csv, os
from shuffle.artist.models import Artist

def insert_artists_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            artist = Artist(
                name=row['name'],
                bio=row['bio'],
                email=row['email'],
                phone=row['phone'],
                country=row['country'],
                photo=row['photo'],
                mixcloud=row['mixcloud'],
                soundcloud=row['soundcloud'],
                epk=row['epk'],
                instagram=row['instagram']
            )
            artist.save()

# Example usage:
csv_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artists.csv')
insert_artists_from_csv(csv_file_path)
