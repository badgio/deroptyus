import json
from base64 import b64decode

from django.core import serializers
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .models import Location, Status


def create_location(location, manager):
    # Creating Location
    location_created = Location()

    location_created.name = location.get('name')
    location_created.description = location.get('description')
    location_created.latitude = location.get('latitude')
    location_created.longitude = location.get('longitude')
    location_created.website = location.get("website")
    location_created.status = location.get("status")
    location_created.facebook = location.get('facebook')
    location_created.instagram = location.get('instagram')

    if location.get("image"):
        try:
            img_format, img_str = location.get("image").split(';base64,')
            ext = img_format.split('/')[-1]
            location_created.image = ContentFile(b64decode(img_str), name=str(location_created.uuid) + '.' + ext)
        except Exception as e:
            raise NotAValidImage(e)

    location_created.manager = manager
    location_created.save()

    return location_created


def get_location():
    return Location.objects.all()


def get_location_by_uuid(location_uuid):
    return Location.objects.get(uuid=location_uuid)


def delete_location_by_uuid(location_uuid):
    location = get_location_by_uuid(location_uuid)
    # Deleting previous image from storage
    if location.image:
        default_storage.delete(location.image.path)
    return location.delete()


def patch_location_by_uuid(location_uuid, location):
    # Getting location to update
    location_update = get_location_by_uuid(location_uuid)
    # Updating provided fields
    if location.get('name'):
        location_update.name = location.get('name')
    if location.get('description'):
        location_update.description = location.get('description')
    if location.get('latitude'):
        location_update.latitude = location.get('latitude')
    if location.get('longitude'):
        location_update.longitude = location.get('longitude')
    if location.get('website'):
        location_update.website = location.get('website')
    if location.get('status'):
        location_update.status = location.get('status')
    if location.get('facebook'):
        location_update.facebook = location.get('facebook')
    if location.get('instagram'):
        location_update.instagram = location.get('instagram')
    if location.get("image"):
        try:
            # Deleting previous image from storage
            default_storage.delete(location_update.image.path)
            # Decoding and storing new image
            img_format, img_str = location.get("image").split(';base64,')
            ext = img_format.split('/')[-1]
            location_update.image = ContentFile(b64decode(img_str), name=str(location_update.uuid) + '.' + ext)
        except Exception as e:
            raise NotAValidImage(e)

    location_update.save()

    return location_update


def encode_location(location):
    return json.loads(serializers.serialize("json",
                                            location,
                                            fields=[
                                                'uuid', 'name',
                                                'description', 'website',
                                                'latitude', 'longitude',
                                                'image', 'facebook', 'instagram',
                                                'status']))


def decode_location(data, admin):
    json_data = json.loads(data)
    location = {
        'name': json_data.get("name"),
        'description': json_data.get("description"),
        'latitude': json_data.get("latitude"),
        'longitude': json_data.get("longitude"),
        'website': json_data.get("website"),
        'image': json_data.get("image"),
        'facebook': json_data.get("facebook"),
        'instagram': json_data.get("instagram"),
        'status': json_data.get("status") if admin else Status.PENDING  # Only admin can change status
    }
    return location


class NotAValidImage(Exception):
    pass
