import json
from base64 import b64encode, b64decode
from mimetypes import guess_type, guess_extension

from django.core import serializers

from locations import queries as location_queries
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


def encode_rewards_to_json(rewards):
    serialized_rewards = json.loads(serializers.serialize("json",
                                                          rewards,
                                                          fields=[
                                                              'uuid',
                                                              'name', 'description',
                                                              'image',
                                                              'time_redeem',
                                                              'promoter', 'location', 'status', ]))

    tweaked_serialized_rewards = []
    for serialized in serialized_rewards:

        reward_fields = serialized['fields']

        if reward_fields.get('image'):
            # Getting image data from storage
            image_data = open(reward_fields['image'], 'rb').read()
            # Encoding it
            reward_fields['image'] = encode_image_to_base64(image_data, reward_fields.get('image'))

        if reward_fields.get('location'):
            reward_fields['location'] = location_queries.get_str_by_pk(reward_fields.get('location'))

        if reward_fields.get('promoter'):
            reward_fields['promoter'] = user_queries.get_str_by_promoter_pk(reward_fields.get('promoter'))

        tweaked_serialized_rewards.append(reward_fields)

    return tweaked_serialized_rewards


def decode_redeem_info_from_json(data):
    try:
        json_data = json.loads(data)
        redeem_info = {
            'reward_code': json_data.get('reward_code')
        }
    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return redeem_info


def decode_reward_from_json(data, admin):
    try:
        json_data = json.loads(data)
        reward = {
            'name': json_data.get('name'),
            'description': json_data.get('description'),
            'location': json_data.get('location'),
            'status': json_data.get("status") if admin else Status.PENDING,  # Only admin can change status
        }

        if 'image' in json_data:
            reward['image'] = json_data.get('image'),
        if 'time_redeem' in json_data:
            reward['time_redeem'] = int(json_data.get('time_redeem')) if json_data.get('time_redeem') else None

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return reward


class InvalidJSONData(Exception):
    pass


class NotAValidImage(Exception):
    pass
