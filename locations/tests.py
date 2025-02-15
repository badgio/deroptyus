import json

from django.test import Client, TestCase

from users.tests import UsersTestCase


class LocationTestCase(TestCase):

    def test_location_get_all(self):
        """
        Test: Get all locations
        Path: /v0/locations/
        """
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="managers", email="manager@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = client.get('/v0/locations/')
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    @staticmethod
    def __create_location__(client):
        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        website = "bomjesus.pt"
        latitude = "-13.2521"
        longitude = "-43.4172"
        facebook = "www.facebook.com"
        instagram = "www.instagram.com"
        twitter = "www.twitter.com"

        # Sending request to create a Location
        return client.post('/v0/locations/', {
            'name': name,
            'description': description,
            'latitude': latitude,
            'longitude': longitude,
            'facebook': facebook,
            'instagram': instagram,
            'twitter': twitter,
            'website': website,
        }, content_type="application/json")

    def get_location(self):
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="managers", email="manager@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = self.__create_location__(client)

        return json.loads(response.content)["uuid"]

    def test_location_create(self):
        """
        Test: Create a new location
        Path: /v0/locations/
        """
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="managers", email="manager@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = self.__create_location__(client)

        # Asserting the success of the location creation
        self.assertEqual(response.status_code, 201)

        # Logging out
        users.log_out()

    def test_location_get_with_uuid(self):
        """
        Test: Get a location with UUID
        Path: /v0/locations/uuid
        """
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="managers", email="manager@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = self.__create_location__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.get(f'/v0/locations/{uuid}')

        # Asserting the success of retrieving a location
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_location_statistics(self):
        """
        Test: Get a statistics with location UUID
        Path: /v0/locations/uuid/statistics
        """
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="managers", email="manager@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = self.__create_location__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.get(f'/v0/locations/{uuid}/statistics')

        # Asserting the success of retrieving a location
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data[1]['Total_visitors'], 0)

        # Logging out
        users.log_out()

    def test_location_patch_with_uuid(self):
        """
        Test: Patch a location with uuid
        Path: /v0/locations/uuid
        """
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="managers", email="manager@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = self.__create_location__(client)

        # Sending request to update a Location
        uuid = json.loads(response.content)['uuid']
        response = client.patch(f'/v0/locations/{uuid}', {
            'name': "New name",
            'description': "New description",
            'latitude': 1,
            'longitude': 2,
            'website': "www.google.com",
        }, content_type="application/json")

        # Asserting the success of the location update
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_location_delete_with_uuid(self):
        """
        Test: Delete a location with uuid
        Path: /v0/locations/uuid
        """
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="managers", email="manager@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = self.__create_location__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.delete(f'/v0/locations/{uuid}')

        # Asserting the success of the deleting a location
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()
