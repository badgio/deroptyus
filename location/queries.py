import json
from django.core import serializers
from django.core.files.base import ContentFile

from .models import Location, Status


def create_location(location, manager):
    try:
        # Creating Location
        location_created = Location()

        location_created.name = location['name']
        location_created.description = location['description']
        location_created.latitude = location['latitude']
        location_created.longitude = location['longitude']
        location_created.website = location["website"]
        location_created.status = location["status"]
        location_update.facebook = location['facebook']
        location_update.instagram = location['instagram']

        if location["image"]:
            format, imgstr = location["image"].split(';base64,')
            ext = format.split('/')[-1]
            location_created.image = ContentFile(b64decode(imgstr), name=str(location_created.uuid) + '.' + ext)
        else:
            location_created.image = None

        location_created.manager = manager
        location_created.save()

        return location_created

    except Exception as e:

        raise ErrorCreate(f'Error creating: {e}')


def get_location():
    return Location.objects.all()


def get_location_by_uuid(location_uuid):
    return Location.objects.get(uuid=location_uuid)


def delete_location_by_uuid(location_uuid):
    return Location.objects.get(uuid=location_uuid).delete()


def patch_location_by_uuid(location_update, location):
    try:

        if location['name']:
            location_update.name = location['name']
        if location['description']:
            location_update.description = location['description']
        if location['latitude']:
            location_update.latitude = location['latitude']
        if location['longitude']:
            location_update.longitude = location['longitude']
        if location['website']:
            location_update.website = location['website']
        if location['status']:
            location_update.status = location['status']
        if location['facebook']:
            location_update.facebook = location['facebook']
        if location['instagram']:
            location_update.instagram = location['instagram']

        if location["image"]:
            image_name = location_update.name
            image_data = b64decode(location["image"])
            location_update.image = ContentFile(image_data, image_name)

        location_update.save()

        return location_update

    except Exception as e:

        raise ErrorCreate(f'Error Updating: {e}')


def serialize_json_location(location):
    return json.loads(serializers.serialize("json",
                                            location,
                                            fields=[
                                                'uuid', 'name',
                                                'description', 'website',
                                                'latitude', 'longitude',
                                                'image',
                                                'status']))


def decodeLocation(data):
    location = {
        'name': data.get("name"),
        'description': data.get("description"),
        'latitude': data.get("latitude"),
        'longitude': data.get("longitude"),
        'website': data.get("website"),
        'image': data.get("image"),
        'facebook': data.get("facebook"),
        'instagram': data.get("instagram"),
    }
    return location


class ErrorCreate(Exception):
    pass


class ErrorUpdate(Exception):
    pass
