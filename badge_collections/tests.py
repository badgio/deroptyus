import json
from datetime import datetime, timedelta

from django.test import Client, TestCase

from badges.tests import BadgeTestCase
from users.tests import UsersTestCase


class CollectionTestCase(TestCase):

    def test_collection_get_all(self):
        """
        Test: Get all collections
        Path: /v0/collections/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = client.get('/v0/collections/')
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    @staticmethod
    def __create_collection__(client, badges=None):
        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        start_date = datetime.utcnow()
        end_date = datetime.utcnow() + timedelta(days=30)

        # Sending request to create a Collection
        return client.post('/v0/collections/', {
            'name': name,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'badges': badges if badges else [BadgeTestCase().get_badge() for _ in range(3)]
        }, content_type="application/json")

    def test_collection_create(self):
        """
        Test: Create a new collection
        Path: /v0/collections/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_collection__(client)

        # Asserting the success of the collection creation
        self.assertEqual(response.status_code, 201)

    def test_collection_get_with_uuid(self):
        """
        Test: Get a collection with UUID
        Path: /v0/collections/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_collection__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.get(f'/v0/collections/{uuid}')

        # Asserting the success of retrieving a collection
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_collection_patch_with_uuid(self):
        """
        Test: Patch a collection with uuid
        Path: /v0/collections/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_collection__(client)

        # Sending request to update a Collection
        uuid = json.loads(response.content)['uuid']
        response = client.patch(f'/v0/collections/{uuid}', {
            'name': "New name",
            'description': "New description",
        }, content_type="application/json")

        # Asserting the success of the collection update
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_collection_delete_with_uuid(self):
        """
        Test: Delete a collection with uuid
        Path: /v0/collections/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_collection__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.delete(f'/v0/collections/{uuid}')

        # Asserting the success of the deleting a collection
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()
