import json
from datetime import datetime, timedelta

from django.test import Client, TestCase

from locations.tests import LocationTestCase
from users.tests import UsersTestCase


class BadgeTestCase(TestCase):

    def test_app_badge_get_all(self):
        """
        Test: Get all badges
        Path: /v0/badges/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = client.get('/v0/badges/')
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out(email="promoter@test.com")

    @staticmethod
    def __create_badge__(client):
        locations = LocationTestCase()

        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        image = ""
        start_date = datetime.utcnow()
        end_date = datetime.utcnow() + timedelta(days=30)
        location = locations.get_location()

        # Sending request to create a Badge
        return client.post('/v0/badges/', {
            'name': name,
            'description': description,
            'image': image,
            'start_date': start_date,
            'end_date': end_date,
            'location': location
        }, content_type="application/json")

    def test_app_badge_create(self):
        """
        Test: Create a new badge
        Path: /v0/badges/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_badge__(client)

        # Asserting the success of the badge creation
        self.assertEqual(response.status_code, 201)

        # Logging out
        users.log_out(email="promoter@test.com")

    def test_app_badge_get_with_uuid(self):
        """
        Test: Get a badge with UUID
        Path: /v0/badges/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_badge__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.get(f'/v0/badges/{uuid}')

        # Asserting the success of retrieving a badge
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out(email="promoter@test.com")

    def test_app_badge_patch_with_uuid(self):
        """
        Test: Patch a badge with uuid
        Path: /v0/badges/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_badge__(client)

        # Sending request to update a Badge
        uuid = json.loads(response.content)['uuid']
        response = client.patch(f'/v0/badges/{uuid}', {
            'name': "New name",
            'description': "New description",
            'latitude': 1,
            'longitude': 2,
            'website': "www.google.com",
        }, content_type="application/json")

        # Asserting the success of the badge update
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out(email="promoter@test.com")

    def test_app_badge_delete_with_uuid(self):
        """
        Test: Delete a badge with uuid
        Path: /v0/badges/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_badge__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.delete(f'/v0/badges/{uuid}')

        # Asserting the success of the deleting a badge
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out(email="promoter@test.com")
