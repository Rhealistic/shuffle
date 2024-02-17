from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status as drf_status

from shuffle.curator.models import Concept

from .models import Artist, Opportunity
from .serializers import OpportunitySerializer

class CreateOpportunityViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test data
        self.artist = Artist.objects.create(id=1, name="Test Artist")
        self.concept = Concept.objects.create(id=1, title="Test Concept")

    def test_create_opportunity_success(self):
        # Prepare request data
        data = {
            'concept_id': self.concept.id
        }

        # Make POST request to create opportunity
        response = self.client.post(f'/v1/artists/{self.artist.id}/opportunity/create/', data, format='json')

        # Check if response status code is 201 CREATED
        self.assertEqual(response.status_code, drf_status.HTTP_201_CREATED)

        # Check if opportunity is created in the database
        self.assertTrue(Opportunity.objects.filter(concept=self.concept, artist=self.artist).exists())

        # Check if response data matches expected data
        opportunity = Opportunity.objects.get(concept=self.concept, artist=self.artist)
        expected_data = OpportunitySerializer(instance=opportunity).data
        self.assertEqual(response.data, expected_data)

    def test_create_opportunity_artist_not_found(self):
        # Prepare request data with invalid artist_id
        invalid_artist_id = 999
        data = {
            'concept_id': self.concept.id
        }

        # Make POST request to create opportunity with invalid artist_id
        response = self.client.post(f'/v1/artists/{invalid_artist_id}/opportunity/create/', data, format='json')

        # Check if response status code is 404 NOT FOUND
        self.assertEqual(response.status_code, drf_status.HTTP_404_NOT_FOUND)

    def test_create_opportunity_invalid_concept_id(self):
        # Prepare request data with invalid concept_id
        invalid_concept_id = 999
        data = {
            'concept_id': invalid_concept_id
        }

        # Make POST request to create opportunity with invalid concept_id
        response = self.client.post(f'/v1/artists/{self.artist.id}/opportunity/create/', data, format='json')

        # Check if response status code is 400 BAD REQUEST
        self.assertEqual(response.status_code, drf_status.HTTP_400_BAD_REQUEST)
