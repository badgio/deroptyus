import json
from django.core import serializers
from django.core.files.base import ContentFile
from base64 import b64decode
from .models import Badge


def create_badge(badge, promoter):
    try:
        # Creating badge
        badge_created = badge()

        badge_created.name = badge['name']
        badge_created.description = badge['description']
        badge_created.status = badge["status"]

        if badge["image"]:
            format, imgstr = badge["image"].split(';base64,')
            ext = format.split('/')[-1]
            badge_created.image = ContentFile(b64decode(imgstr), name=str(badge_created.uuid) + '.' + ext)
        else:
            badge_created.image = None

        badge_created.location = badge['location']
        badge_created.manager = promoter
        badge_created.save()

        return badge_created

    except Exception as e:

        raise ErrorCreate(f'Error creating: {e}')


def get_badge():
    return Badge.objects.all()


def get_badge_by_uuid(badge_uuid):
    return Badge.objects.get(uuid=badge_uuid)


def delete_badge_by_uuid(badge_uuid):
    return Badge.objects.get(uuid=badge_uuid).delete()


def patch_badge_by_uuid(badge_update, badge):
    try:

        if badge['name']:
            badge_update.name = badge['name']
        if badge['description']:
            badge_update.description = badge['description']
        if badge['status']:
            badge_update.status = badge['status']
        if badge['location']:
            badge_update.location = badge['location']

        if badge["image"]:
            image_name = badge_update.name
            image_data = b64decode(badge["image"])
            badge_update.image = ContentFile(image_data, image_name)

        badge_update.save()

        return badge_update

    except Exception as e:

        raise ErrorCreate(f'Error Updating: {e}')


def encode_badge(badge):
    return json.loads(serializers.serialize("json",
                                            badge,
                                            fields=[
                                                'uuid', 'name',
                                                'description', 'image',
                                                'location', 'status']))


def decode_badge(data):
    json_data = json.loads(data)
    badge = {
        'name': json_data.get("name"),
        'description': json_data.get("description"),
        'location': json_data.get("location"),
        'image': json_data.get("image"),
        'status': json_data.get('status')
    }
    return badge


class ErrorCreate(Exception):
    pass


class ErrorUpdate(Exception):
    pass
