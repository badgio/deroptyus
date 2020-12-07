import json
from base64 import b64encode
from datetime import datetime
from mimetypes import guess_type

from django.core import serializers

from .models import Status


def encode_badge_to_json(badges):
    serialized_badges = json.loads(serializers.serialize("json",
                                                         badges,
                                                         fields=[
                                                             'uuid', 'name',
                                                             'description',
                                                             'start_date', 'end_date',
                                                             'location', 'status', 'image', ]))

    image_serialized_badges = []
    for serialized in serialized_badges:

        badge_fields = serialized["fields"]

        if badge_fields.get('image'):
            # Encoding image to base64
            decoded_img = b64encode(open(badge_fields['image'], 'rb').read()).decode('utf-8')
            # Sending image with Data URI format
            badge_fields['image'] = f'data:{guess_type(badge_fields["image"])[0]};base64,{decoded_img}'

        image_serialized_badges.append(badge_fields)

    return image_serialized_badges


def decode_badge_from_json(data, admin):
    try:
        json_data = json.loads(data)
        badge = {
            'name': json_data.get("name"),
            'description': json_data.get("description"),
            'location': json_data.get("location"),
            'image': json_data.get("image"),
            'status': json_data.get("status") if admin else Status.PENDING,  # Only admin can change status
        }

        # Setting start date
        if "start_date" in json_data:
            try:
                badge["start_date"] = datetime.fromisoformat(json_data.get("start_date"))
            except Exception:
                raise NotAValidStartDate()

        # Setting end date
        if "end_date" in json_data:
            try:
                badge["end_date"] = datetime.fromisoformat(json_data.get("end_date"))
            except Exception:
                raise NotAValidEndDate()

    except json.JSONDecodeError:
        raise InvalidJSONData()

    return badge


class NotAValidStartDate(Exception):
    pass


class NotAValidEndDate(Exception):
    pass


class InvalidJSONData(Exception):
    pass
