import json
from base64 import b64encode, b64decode
from datetime import datetime
from mimetypes import guess_type, guess_extension

from django.core import serializers

from .models import Status


def decode_image_from_base64(base64_image, filename):
    try:
        # Accepted format: data:<mime_type>;base64,<encoding>
        img_format, img_str = base64_image.split(';base64,')
        _, mime_type = img_format.split(':')

        # If MIME type is not image
        if mime_type.split("/")[0] != "image":
            raise NotAValidImage()

        # Decoding image from base64
        decoded_img = b64decode(img_str)
        # Getting extension from MIME type
        file_extension = guess_extension(mime_type)
        # Storing image
        return decoded_img, f'{filename}.{file_extension}'
    except Exception as e:
        raise NotAValidImage(e)


def encode_image_to_base64(image, filename):
    # Encoding image to base64
    encoded_img = b64encode(image).decode('utf-8')
    # Sending image with Data URI format
    return f'data:{guess_type(filename)[0]};base64,{encoded_img}'


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
            # Getting image data from storage
            image_data = open(badge_fields['image'], 'rb').read()
            # Encoding it
            badge_fields['image'] = encode_image_to_base64(image_data, badge_fields.get('image'))

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


class NotAValidImage(Exception):
    pass
