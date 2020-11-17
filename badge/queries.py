from badge.models import Badge
from location.models import Status
from base64 import b64decode
from django.core.files.base import ContentFile


def create_badge(badge):

    try:
        badge_created = Badge()

        badge_created.name = badge['name']
        badge_created.description = badge['description']
        badge_created.nfc_tag = badge['nfc_tag']
        badge_created.image = badge['abc']
        badge_created.location = badge['location']
        badge_created.status = badge['status']
        badge_created.date_start = badge['date_start']
        badge_created.date_end = badge['date_end']

        if badge["image"]:
            image_name = badge_created.name + ".jpg"
            image_data = b64decode(badge["image"])
            badge_created.image = ContentFile(image_data, image_name)
        else:
            badge_created.image = None

        badge_created.save()

        return badge_created

    except:

        raise ErrorCreate('Error creating')


def get_badge():

    return Badge.objects.all()


def get_badge_by_uuid(badge_uuid):

    return Badge.objects.get(uuid=badge_uuid)


def delete_badge_by_uuid(badge_uuid):

    return Badge.objects.filter(uuid=badge_uuid).delete()


def update_badge_by_uuid(badge_uuid, badge):

    try:

        badge_update = Badge.objects.get(uuid=badge_uuid)

        if badge['name']:
            badge_update.name = badge['name']
        if badge['description']:
            badge_update.description = badge['description']
        if badge['nfc_tag']:
            badge_update.nfc_tag = badge['nfc_tag']
        if badge['location']:
            badge_update.location = badge['location']
        if badge['status']:
            badge_update.status = badge['status']
        if badge['date_start']:
            badge_update.date_start = badge['date_start']
        if badge['date_end']:
            badge_update.date_end = badge['date_end']

        if badge["image"]:
            image_name = badge_update.name + ".jpg"
            image_data = b64decode(badge["image"])
            badge_update.image = ContentFile(image_data, image_name)

        badge_update.save()

        return badge_update

    except:

        raise ErrorUpdate('Error updating')


class ErrorCreate (Exception):
    pass


class ErrorUpdate (Exception):
    pass

