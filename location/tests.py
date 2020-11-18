from django.test import Client, TestCase
from location.models import Status, Location, SocialMedia
import json


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

    def test_app_location_get_with_uuid(self):
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
        a = json.loads(response.content)['uuid']
        response = client.get(f'/v1/locations/{a}')
        self.assertEqual(response.status_code, 200)

    def test_app_location_update_with_uuid(self):
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
        a = json.loads(response.content)['uuid']
        response = client.put(f'/v1/locations/{a}', {
            'name': "New name",
            'description': "New description",
            'latitude': 1,
            'longitude': 2,
            'website': "www.google.com",
            'status': Status.REJECT
        }, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_app_location_delete_with_uuid(self):
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
        a = json.loads(response.content)['uuid']
        response = client.delete(f'/v1/locations/{a}')
        self.assertEqual(response.status_code, 200)
