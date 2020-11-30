import json
from base64 import b64decode
from datetime import datetime

from django.core import serializers
from django.core.files.base import ContentFile

from locations.models import Location
from .models import Badge, Status


def create_badge(badge, promoter):
    # Creating badge
    badge_created = Badge()

    badge_created.name = badge.get('name')
    badge_created.description = badge.get('description')

    if "start_date" in badge:
        badge_created.start_date = badge.get('start_date')

    if "end_date" in badge:
        if badge.get('end_date') > badge_created.start_date:  # End must be after the start
            badge_created.end_date = badge.get('end_date')
        else:
            raise EndDateNotAfterStartDate()

    badge_created.status = badge.get("status")

    if badge.get("image"):
        try:
            img_format, img_str = badge.get("image").split(';base64,')
            ext = img_format.split('/')[-1]
            badge_created.image = ContentFile(b64decode(img_str), name=str(badge_created.uuid) + '.' + ext)
        except Exception:
            raise NotAValidImage()

    try:
        badge_created.location = Location.objects.get(uuid=badge.get('location'))
    except Location.DoesNotExist:
        raise NotAValidLocation()

    badge_created.promoter = promoter
    badge_created.save()

    return badge_created


def get_badge():
    return Badge.objects.all()


def get_badge_by_uuid(badge_uuid):
    return Badge.objects.get(uuid=badge_uuid)


def delete_badge_by_uuid(badge_uuid):
    return Badge.objects.get(uuid=badge_uuid).delete()


def patch_badge_by_uuid(badge_update, badge):
    if badge.get('name'):
        badge_update.name = badge.get('name')
    if badge.get('description'):
        badge_update.description = badge.get('description')
    if badge.get('start_date'):
        badge_update.start_date = badge.get('start_date')
    if badge.get('end_date'):
        if badge.get('end_date') > badge_update.start_date:  # End must be after the start
            badge_update.end_date = badge.get('end_date')
        else:
            raise EndDateNotAfterStartDate()
    if badge.get('status'):
        badge_update.status = badge.get('status')
    if badge.get('location'):
        try:
            badge_update.location = Location.objects.get(uuid=badge.get('location'))
        except Location.DoesNotExist:
            raise NotAValidLocation()

    if badge.get("image"):
        try:
            image_name = badge_update.name
            image_data = b64decode(badge.get("image"))
            badge_update.image = ContentFile(image_data, image_name)
        except Exception:
            raise NotAValidImage()

    badge_update.save()

    return badge_update


def encode_badge(badge):
    return json.loads(serializers.serialize("json",
                                            badge,
                                            fields=[
                                                'uuid', 'name',
                                                'description', 'image',
                                                'start_date', 'end_date',
                                                'location', 'status']))


def decode_badge(data, admin):
    json_data = json.loads(data)
    badge = {
        'name': json_data.get("name"),
        'description': json_data.get("description"),
        'location': json_data.get("location"),
        'image': json_data.get("image"),
        'status': json_data.get("status") if admin else Status.PENDING  # Only admin can change status
    }

    # Setting start date
    if "start_date" in json_data:
        try:
            date = datetime.fromisoformat(json_data.get("start_date"))
            badge["start_date"] = date
        except Exception:
            raise NotAValidStartDate()

    # Setting end date
    if "end_date" in json_data:
        try:
            date = datetime.fromisoformat(json_data.get("end_date"))
            badge["end_date"] = date
        except Exception:
            raise NotAValidEndDate()

    return badge


class NotAValidLocation(Exception):
    pass


class NotAValidImage(Exception):
    pass


class NotAValidStartDate(Exception):
    pass


class NotAValidEndDate(Exception):
    pass


class EndDateNotAfterStartDate(Exception):
    pass


class ErrorUpdate(Exception):
    pass
