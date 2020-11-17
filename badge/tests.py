from django.test import Client, TestCase

from location.models import Status
from badge.models import Badge
import datetime


class BadgeTestCase(TestCase):

    def test_app_badge_get_all(self):
        """
        Test: Get all locations
        Path: /v0/badges/
        """
        client = Client()

        response = client.get('/v0/badges/')
        self.assertEqual(response.status_code, 200)

    def test_app_badge_create(self):
        """
        Test: Create a new location
        Path: /v0/badges/
        """

        name = "Bom Jesus Badge"
        description = "Badge para o Bom Jesus"
        nfc_tag = "NFC_TAG"
        image = ""
        location = ""
        status = Status.APPROVE
        date_start = datetime.date.today()
        date_end = datetime.date.today()

        client = Client()

        # Sending request to create an app user
        response = client.post('/v0/badges/', {
            'name': name,
            'description': description,
            'nfc_tag': nfc_tag,
            'image': image,
            'location': location,
            'status': status,
            'date_start': date_start,
            'date_end': date_end,
        }, content_type="application/json")

        # Asserting the success of the user creation (assuming the user doesn't exist)
        self.assertEqual(response.status_code, 200)
