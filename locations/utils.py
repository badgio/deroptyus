import json
from base64 import b64encode
from mimetypes import guess_type

from django.core import serializers

from .models import Status


def encode_location_to_json(locations):
    serialized_locations = json.loads(serializers.serialize("json",
                                                            locations,
                                                            fields=[
                                                                'uuid', 'name',
                                                                'description', 'website',
                                                                'latitude', 'longitude',
                                                                'facebook', 'instagram',
                                                                'status', 'image', ]))

    image_serialized_locations = []
    for serialized in serialized_locations:

        location_fields = serialized["fields"]

        if location_fields.get('image'):
            # Encoding image to base64
            decoded_img = b64encode(open(location_fields['image'], 'rb').read()).decode('utf-8')
            # Sending image with Data URI format
            location_fields['image'] = f'data:{guess_type(location_fields["image"])[0]};base64,{decoded_img}'

        image_serialized_locations.append(location_fields)

    return image_serialized_locations


def decode_location_from_json(data, admin):
    try:
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
            'status': json_data.get("status") if admin else Status.PENDING,  # Only admin can change status
        }
    except json.JSONDecodeError:
        raise InvalidJSONData()

    return location


class InvalidJSONData(Exception):
    pass
