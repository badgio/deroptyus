from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from users.models import ManagerUser
from . import utils
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
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(location.get("image"), str(location_created.uuid))
        # Storing image
        location_created.image = ContentFile(decoded_img, name=filename)

    location_created.manager = ManagerUser.objects.get(user_id=user_id)
    location_created.save()

    return location_created


def get_locations():
    return Location.objects.all()


def get_location_by_uuid(location_uuid):
    return Location.objects.get(uuid=location_uuid)


def get_str_by_pk(pk):
    return str(Location.objects.get(pk=pk))


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
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(location.get("image"), str(location_update.uuid))
        # Deleting previous image from storage
        default_storage.delete(location_update.image.path)
        # Storing image
        location_update.image = ContentFile(decoded_img, name=filename)

    location_update.save()

    return location_update
