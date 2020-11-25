import json
from base64 import b64decode

from django.core import serializers
from django.core.files.base import ContentFile

from .models import Location, SocialMedia, ManagerLocation


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

        if location["image"]:
            format, imgstr = location["image"].split(';base64,')
            ext = format.split('/')[-1]
            location_created.image = ContentFile(b64decode(imgstr), name=str(location_created.uuid) + '.' + ext)
        else:
            location_created.image = None

        location_created.save()

        # Linking the Location to a User
        manager_location = ManagerLocation(manager=manager, location=location_created)
        manager_location.save()

        # Creating Social Media for a Location

        if location['social_media']:
            for i in location['social_media']:
                social_media_created = SocialMedia()
                social_media_created.location_id = location_created.id
                social_media_created.social_media = i
                social_media_created.link = location['social_media'][i]
                social_media_created.save()

        return location_created

    except Exception as e:

        raise ErrorCreate(f'Error creating: {e}')


def get_location():
    return Location.objects.all()


def get_location_by_uuid(location_uuid):
    return Location.objects.get(uuid=location_uuid)


def delete_location_by_uuid(location_uuid):
    location = Location.objects.get(uuid=location_uuid)

    ManagerLocation.objects.get(location=location).delete()

    return location.delete()


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

        if location["image"]:
            image_name = location_update.name
            image_data = b64decode(location["image"])
            location_update.image = ContentFile(image_data, image_name)

        location_update.save()

        if location['social_media']:
            for i in location['social_media']:
                social_media_update = SocialMedia.objects.filter(
                    location_id=location_update.id, social_media=i)
                if social_media_update:
                    social_media_update = SocialMedia.objects.get(
                        location_id=location_update.id, social_media=i)
                    social_media_update.social_media = i
                    social_media_update.link = location['social_media'][i]
                    social_media_update.save()
                else:
                    social_media_created = SocialMedia()
                    social_media_created.location_id = location_update.id
                    social_media_created.social_media = i
                    social_media_created.link = location['social_media'][i]
                    social_media_created.save()

        return location_update

    except Exception as e:

        raise ErrorCreate('Error Updating:' + e)


def get_social_media_by_id(id):
    return SocialMedia.objects.filter(location_id=id)


def serialize_json_location(location):
    return json.loads(serializers.serialize("json",
                                            location,
                                            fields=[
                                                'uuid', 'name',
                                                'description', 'website',
                                                'latitude', 'longitude',
                                                'image',
                                                'status']))


def serialize_social_media(social_media):
    if not social_media:
        return None

    social_media_serialize = json.loads(serializers.serialize("json",
                                                              social_media,
                                                              fields=['social_media',
                                                                      'link']))
    a = {}
    for i in range(len(social_media_serialize)):
        a[social_media_serialize[i]["fields"]["social_media"]] = social_media_serialize[i]["fields"]["link"]

    return a


class ErrorCreate(Exception):
    pass


class ErrorUpdate(Exception):
    pass
