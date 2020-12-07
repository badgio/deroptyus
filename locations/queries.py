from base64 import b64decode
from mimetypes import guess_extension

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from users.models import ManagerUser
from .models import Location


def create_location(location, user_id):
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
            # Accepted format: data:<mime_type>;base64,<encoding>
            img_format, img_str = location.get("image").split(';base64,')
            _, mime_type = img_format.split(':')

            # If MIME type is not image
            if mime_type.split("/")[0] != "image":
                raise NotAValidImage()

            # Decoding image from base64
            decoded_img = b64decode(img_str)
            # Getting extension from MIME type
            file_extension = guess_extension(mime_type)
            # Storing image
            location_created.image = ContentFile(decoded_img, name=str(location_created.uuid) + '.' + file_extension)
        except Exception as e:
            raise NotAValidImage(e)

    location_created.manager = ManagerUser.objects.get(user_id=user_id)
    location_created.save()

    return location_created


def get_locations():
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
            # Accepted format: data:<mime_type>;base64,<encoding>
            img_format, img_str = location.get("image").split(';base64,')
            _, mime_type = img_format.split(':')

            # If MIME type is not image
            if mime_type.split("/")[0] != "image":
                raise NotAValidImage()

            # Decoding image from base64
            decoded_img = b64decode(img_str)

            # Deleting previous image from storage
            default_storage.delete(location_update.image.path)

            # Getting extension from MIME type
            file_extension = guess_extension(mime_type)
            # Storing image
            location_update.image = ContentFile(decoded_img, name=str(location_update.uuid) + '.' + file_extension)

        except Exception as e:
            raise NotAValidImage(e)

    location_update.save()

    return location_update


class NotAValidImage(Exception):
    pass
