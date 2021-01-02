import json
from base64 import b64encode, b64decode
from mimetypes import guess_type, guess_extension

from django.core import serializers

from users import queries as user_queries
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


def encode_location_to_json(locations):
    serialized_locations = json.loads(serializers.serialize("json",
                                                            locations,
                                                            fields=[
                                                                'uuid', 'name',
                                                                'description', 'website',
                                                                'latitude', 'longitude',
                                                                'facebook', 'instagram', 'twitter',
                                                                'status', 'image', 'manager']))

    image_serialized_locations = []
    for serialized in serialized_locations:

        location_fields = serialized["fields"]

        if location_fields.get('image'):
            # Getting image data from storage
            image_data = open(location_fields['image'], 'rb').read()
            # Encoding it
            location_fields['image'] = encode_image_to_base64(image_data, location_fields.get('image'))

        if location_fields.get('manager'):
            location_fields['manager'] = user_queries.get_str_by_manager_pk(location_fields.get('manager'))

        image_serialized_locations.append(location_fields)

    return image_serialized_locations


def decode_location_from_json(data, admin):
    try:
        json_data = json.loads(data)
        location = {
            'name': json_data.get("name"),
            'description': json_data.get("description"),
            'status': json_data.get("status") if admin else Status.PENDING,  # Only admin can change status
        }

        if 'latitude' in json_data:
            location["latitude"] = json_data.get("latitude")
        if 'longitude' in json_data:
            location["longitude"] = json_data.get("longitude")
        if 'website' in json_data:
            location["website"] = json_data.get("website")
        if 'image' in json_data:
            location["image"] = json_data.get("image")
        if 'facebook' in json_data:
            location["facebook"] = json_data.get("facebook")
        if 'instagram' in json_data:
            location["instagram"] = json_data.get("instagram")
        if 'twitter' in json_data:
            location["twitter"] = json_data.get("twitter")

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return location

class InvalidJSONData(Exception):
    pass


class NotAValidImage(Exception):
    pass
