import binascii
import json
from datetime import datetime, timedelta

from django.test import Client, TestCase

from locations.tests import LocationTestCase
from tags import crypto
from tags.tests import TagTestCase
from users.tests import UsersTestCase


class BadgeTestCase(TestCase):

    def test_badge_get_all(self):
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
        users.log_out()

    @staticmethod
    def __create_badge__(client, location=None):
        locations = LocationTestCase()

        name = "Bom Jesus"
        description = "Santuário do Bom Jesus do Monte"
        start_date = datetime.utcnow()
        end_date = datetime.utcnow() + timedelta(days=30)

        # Sending request to create a Badge
        return client.post('/v0/badges/', {
            'name': name,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'location': location if location else locations.get_location()
        }, content_type="application/json")

    def get_badge(self):
        # Logging in
        users = UsersTestCase()
        auth_token = users.log_in(type="promoters", email="promoter@test.com", password="test_password")
        client = Client(HTTP_AUTHORIZATION=auth_token)

        response = self.__create_badge__(client)

        return json.loads(response.content)["uuid"]

    def test_badge_create(self):
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

    def test_badge_get_with_uuid(self):
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
        users.log_out()

    def test_badge_patch_with_uuid(self):
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
        }, content_type="application/json")

        # Asserting the success of the badge update
        self.assertEqual(response.status_code, 200)

        # Logging out
        users.log_out()

    def test_badge_delete_with_uuid(self):
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
        users.log_out()

    def test_badge_redeem(self):
        """
        Test: Reedeem a badge with UID, Counter and CMAC
        Path: /v0/badges/redeem
        """
        locations = LocationTestCase()
        location_uuid = locations.get_location()

        tags = TagTestCase()
        tag_uid = tags.get_tag(location_uuid)

        users = UsersTestCase()
        client = Client(HTTP_AUTHORIZATION=users.log_in(type='mobile',
                                                        email="apper@test.com",
                                                        password="test_password"))

        # Sending Redeem Request with the UID of the recently created tag and a Counter at 0
        response = client.post('/v0/badges/redeem', {
            'uid': tag_uid,
            'cmac': binascii.hexlify(
                crypto.calculate_cmac(tag_uid, "0b94831c5ecce72367dc70706a9bdec3", "0x000001")).decode("utf-8"),
            'counter': "0x000001"
        }, content_type="application/json")

        # Asserting that the request returns an empty array of badges (because there's no badge associated with the tag)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

        promoter_client = Client(HTTP_AUTHORIZATION=users.log_in(type='promoters',
                                                                 email="promoter@test.com",
                                                                 password="test_password"))

        badge_uuid = json.loads(self.__create_badge__(promoter_client, location_uuid).content)["uuid"]

        admin_client = Client(HTTP_AUTHORIZATION=users.log_in_admin(email="admin@test.com",
                                                                    password="test_password"))

        # Approving Badge as an Admin
        response = admin_client.patch(f'/v0/badges/{badge_uuid}', {
            'status': "APPROVED"
        }, content_type="application/json")

        self.assertEqual(response.status_code, 200)

        # Re-sending Redeem Request with the same UID and Counter
        response = client.post('/v0/badges/redeem', {
            'uid': tag_uid,
            'cmac': binascii.hexlify(
                crypto.calculate_cmac(tag_uid, "0b94831c5ecce72367dc70706a9bdec3", "0x000000")).decode("utf-8"),
            'counter': "0x000000"
        }, content_type="application/json")

        # Asserting that the request fails (because the counter 0 has already been redeemed)
        self.assertEqual(response.status_code, 410)

        # Re-sending Redeem Request with the same UID but an updated Counter
        response = client.post('/v0/badges/redeem', {
            'uid': tag_uid,
            'cmac': binascii.hexlify(
                crypto.calculate_cmac(tag_uid, "0b94831c5ecce72367dc70706a9bdec3", "0x000002")).decode("utf-8"),
            'counter': "0x000002"
        }, content_type="application/json")

        # Asserting that the request succeeds
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)[0]['uuid'], badge_uuid)

        # Logging out
        users.log_out()
