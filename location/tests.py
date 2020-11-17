from django.test import Client, TestCase

from location.queries import delete_location_by_uuid
from location.models import Status, Location, SocialMedia


class LocationTestCase(TestCase):

    def test_app_location_get_all(self):
        """
        Test: Get all locations 
        Path: /v0/locations/
        """
        client = Client()

        response = client.get('/v1/locations/')
        self.assertEqual(response.status_code, 200)

    def test_app_location_create(self):
        """
        Test: Create a new location
        Path: /v0/locations/
        """
        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        website = "bomjesus.pt"
        latitude = "-13.2521"
        longitude = "-43.4172"
        image = ""
        social_media = ""
        status = Status.APPROVE

        client = Client()

        # Sending request to create an app user
        response = client.post('/v1/locations/', {
            'name': name,
            'description': description,
            'latitude': latitude,
            'longitude': longitude,
            'social_media': social_media,
            'website': website,
            'image': image,
            'status': status
        }, content_type="application/json")

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 200)
