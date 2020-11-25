import json

import pyrebase
from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase

from location.models import Status


class LocationTestCase(TestCase):

    def login_manager(self):
        # Making sure the DB has the correct permission groups
        call_command('validatepermissions')

        email = "manager@test.com"
        password = "test_password"

        client = Client()

        # Sending request to create an app user
        response = client.post('/v0/users/managers', {
            'email': email,
            'password': password
        }, content_type="application/json")

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 201)

        # Logging the user in the Firebase Console and returning the token for authentication
        app = pyrebase.initialize_app(settings.PYREBASE_API_KEY)
        return app.auth().sign_in_with_email_and_password(email=email, password=password)["idToken"]

    def test_app_location_get_all(self):
        """
        Test: Get all locations
        Path: /v0/locations/
        """
        client = Client(HTTP_AUTHORIZATION=self.login_manager())

        response = client.get('/v0/locations/')
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

        client = Client(HTTP_AUTHORIZATION=self.login_manager())

        # Sending request to create a Location
        response = client.post('/v0/locations/', {
            'name': name,
            'description': description,
            'latitude': latitude,
            'longitude': longitude,
            'social_media': social_media,
            'website': website,
            'image': image,
            'status': status
        }, content_type="application/json")

        # Asserting the success of the location creation
        self.assertEqual(response.status_code, 200)

    def test_app_location_get_with_uuid(self):
        """
        Test: Get a location with UUID
        Path: /v0/locations/uuid
        """
        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        website = "bomjesus.pt"
        latitude = "-13.2521"
        longitude = "-43.4172"
        image = ""
        social_media = ""
        status = Status.APPROVE

        client = Client(HTTP_AUTHORIZATION=self.login_manager())

        # Sending request to create a Location
        response = client.post('/v0/locations/', {
            'name': name,
            'description': description,
            'latitude': latitude,
            'longitude': longitude,
            'social_media': social_media,
            'website': website,
            'image': image,
            'status': status
        }, content_type="application/json")

        a = json.loads(response.content)['uuid']
        response = client.get(f'/v0/locations/{a}')

        # Asserting the success of retrieving a location
        self.assertEqual(response.status_code, 200)

    def test_app_location_patch_with_uuid(self):
        """
        Test: Patch a location with uuid
        Path: /v0/locations/uuid
        """
        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        website = "bomjesus.pt"
        latitude = "-13.2521"
        longitude = "-43.4172"
        image = ""
        social_media = ""
        status = Status.APPROVE

        client = Client(HTTP_AUTHORIZATION=self.login_manager())

        # Sending request to create a Location
        response = client.post('/v0/locations/', {
            'name': name,
            'description': description,
            'latitude': latitude,
            'longitude': longitude,
            'social_media': social_media,
            'website': website,
            'image': image,
            'status': status
        }, content_type="application/json")

        # Sending request to update a Location
        a = json.loads(response.content)['uuid']
        response = client.patch(f'/v0/locations/{a}', {
            'name': "New name",
            'description': "New description",
            'latitude': 1,
            'longitude': 2,
            'website': "www.google.com",
            'status': Status.REJECT
        }, content_type="application/json")

        # Asserting the success of the location update
        self.assertEqual(response.status_code, 200)

    def test_app_location_delete_with_uuid(self):
        """
        Test: Delete a location with uuid
        Path: /v0/locations/uuid
        """
        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        website = "bomjesus.pt"
        latitude = "-13.2521"
        longitude = "-43.4172"
        image = ""
        social_media = ""
        status = Status.APPROVE

        client = Client(HTTP_AUTHORIZATION=self.login_manager())

        # Sending request to create a Location
        response = client.post('/v0/locations/', {
            'name': name,
            'description': description,
            'latitude': latitude,
            'longitude': longitude,
            'social_media': social_media,
            'website': website,
            'image': image,
            'status': status
        }, content_type="application/json")

        a = json.loads(response.content)['uuid']
        response = client.delete(f'/v0/locations/{a}')

        # Asserting the success of the deleting a location
        self.assertEqual(response.status_code, 200)
