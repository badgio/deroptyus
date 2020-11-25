from .models import Location, SocialMedia
from base64 import b64decode
from django.core.files.base import ContentFile


def create_location(location):

    try:
        location_created = Location()

        location_created.name = location['name']
        location_created.description = location['description']
        location_created.latitude = location['latitude']
        location_created.longitude = location['longitude']
        location_created.website = location["website"]
        location_created.status = location["status"]

        if location["image"]:
            image_name = location_created.uuid
            image_data = b64decode(location["image"])
            location_created.image = ContentFile(image_data, image_name)
        else:
            location_created.image = None

        location_created.save()

        for i in location['social_media']:
            social_media_created = SocialMedia()
            social_media_created.location_id = location_created.id
            social_media_created.social_media = i
            social_media_created.link = location['social_media'][i]
            social_media_created.save()

        return location_created

    except Exception:

        raise ErrorCreate('Error creating:' + Exception)


def get_location():

    return Location.objects.all()


def get_location_by_uuid(location_uuid):

    return Location.objects.get(uuid=location_uuid)


def delete_location_by_uuid(location_uuid):

    return Location.objects.filter(uuid=location_uuid).delete()


def patch_location_by_uuid(location_uuid, location):

    try:

        location_update = Location.objects.get(uuid=location_uuid)

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

    except Exception:

        raise ErrorCreate('Error Updating:' + Exception)


def get_social_media_by_id(id):

    return SocialMedia.objects.filter(location_id=id)


class ErrorCreate (Exception):
    pass


class ErrorUpdate (Exception):
    pass
