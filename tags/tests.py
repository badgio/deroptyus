import json

from django.test import Client, TestCase

from locations.tests import LocationTestCase
from users.tests import UsersTestCase


class TagTestCase(TestCase):

    def test_app_tag_get_all(self):
        """
        Test: Get all tags
        Path: /v0/tags/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in_admin(email="admin@test.com",
                                                              password="test_password"))

        response = client.get('/v0/tags/')
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    @staticmethod
    def __create_tag__(client, location=None):
        locations = LocationTestCase()

        uid = "04626f222a6208"
        app_key = "0b94831c5ecce72367dc70706a9bdec3"  # Do not alter, it's used in test_badge_redeem
        counter = "0x000000"

        # Sending request to create a Tag
        return client.post('/v0/tags/', {
            'uid': uid,
            'app_key': app_key,
            'counter': counter,
            'location': location if location else locations.get_location(),
        }, content_type="application/json")

    def get_tag(self, location=None):
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in_admin(email="admin@test.com", password="test_password"))

        response = self.__create_tag__(client, location)

        return json.loads(response.content)["uid"]

    def test_app_tag_create(self):
        """
        Test: Create a new tag
        Path: /v0/tags/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in_admin(email="admin@test.com",
                                                              password="test_password"))

        response = self.__create_tag__(client)

        # Asserting the success of the tag creation
        self.assertEqual(response.status_code, 201)

        # Logging out
        users.log_out()

    def test_app_tag_get_with_uuid(self):
        """
        Test: Get a tag with uid
        Path: /v0/tags/uid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in_admin(email="admin@test.com",
                                                              password="test_password"))

        response = self.__create_tag__(client)

        uid = json.loads(response.content)['uid']
        response = client.get(f'/v0/tags/{uid}')

        # Asserting the success of retrieving a tag
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_app_tag_patch_with_uuid(self):
        """
        Test: Patch a tag with uid
        Path: /v0/tags/uid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in_admin(email="admin@test.com",
                                                              password="test_password"))

        response = self.__create_tag__(client)

        # Sending request to update a Tag
        uid = json.loads(response.content)['uid']
        response = client.patch(f'/v0/tags/{uid}', {
            'app_key': "616d2a2c78995fa84e031e8ec1e4cadb",
        }, content_type="application/json")

        # Asserting the success of the tag update
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_app_tag_delete_with_uuid(self):
        """
        Test: Delete a tag with uid
        Path: /v0/tags/uid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in_admin(email="admin@test.com",
                                                              password="test_password"))

        response = self.__create_tag__(client)

        uid = json.loads(response.content)['uid']
        response = client.delete(f'/v0/tags/{uid}')

        # Asserting the success of the deleting a tag
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()
