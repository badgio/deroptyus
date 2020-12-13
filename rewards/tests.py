import json

from django.test import Client, TestCase

from locations.tests import LocationTestCase
from users.tests import UsersTestCase


class BadgeTestCase(TestCase):

    def test_reward_get_all(self):
        """
        Test: Get all rewards
        Path: /v0/rewards/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = client.get('/v0/rewards/')
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    @staticmethod
    def __create_reward__(client, location=None):
        locations = LocationTestCase()

        description = "Oferta da Nata na compra do Café"
        time_redeem = 30 * 60

        # Sending request to create a Badge
        return client.post('/v0/rewards/', {
            'description': description,
            'time_redeem': time_redeem,
            'location': location if location else locations.get_location()
        }, content_type="application/json")

    def test_reward_create(self):
        """
        Test: Create a new reward
        Path: /v0/rewards/
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_reward__(client)

        # Asserting the success of the reward creation
        self.assertEqual(response.status_code, 201)

    def test_reward_get_with_uuid(self):
        """
        Test: Get a reward with UUID
        Path: /v0/rewards/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_reward__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.get(f'/v0/rewards/{uuid}')

        # Asserting the success of retrieving a reward
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_reward_patch_with_uuid(self):
        """
        Test: Patch a reward with uuid
        Path: /v0/rewards/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_reward__(client)

        # Sending request to update a Badge
        uuid = json.loads(response.content)['uuid']
        response = client.patch(f'/v0/rewards/{uuid}', {
            'description': "New description",
        }, content_type="application/json")

        # Asserting the success of the reward update
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_reward_delete_with_uuid(self):
        """
        Test: Delete a reward with uuid
        Path: /v0/rewards/uuid
        """
        # Logging in
        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type="promoters",
                                                        email="promoter@test.com",
                                                        password="test_password"))

        response = self.__create_reward__(client)

        uuid = json.loads(response.content)['uuid']
        response = client.delete(f'/v0/rewards/{uuid}')

        # Asserting the success of the deleting a reward
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()
