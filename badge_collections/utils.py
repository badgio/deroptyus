import json
from base64 import b64decode
from datetime import datetime
from mimetypes import guess_extension

from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rewards import queries as reward_queries
from rewards import utils as reward_utils
from users import queries as user_queries
from . import queries
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


def encode_collection_to_json(collections):
    serialized_collections = json.loads(serializers.serialize("json",
                                                              collections,
                                                              fields=[
                                                                  'uuid', 'name',
                                                                  'description',
                                                                  'start_date', 'end_date',
                                                                  'promoter', 'reward', 'status', 'image', ]))

    image_serialized_collections = []
    for serialized in serialized_collections:

        collection_fields = serialized["fields"]

        if collection_fields.get('promoter'):
            collection_fields['promoter'] = user_queries.get_str_by_promoter_pk(collection_fields.get('promoter'))

        if collection_fields.get('reward'):
            collection_fields['reward'] = reward_queries.get_str_by_pk(collection_fields.get('reward'))

        collection_fields['badges'] = \
            queries.get_collection_badges_uuids_by_collection_uuid(collection_fields.get('uuid'))

        image_serialized_collections.append(collection_fields)

    return image_serialized_collections


def decode_collection_from_json(data, admin):
    try:
        json_data = json.loads(data)
        collection = {
            'name': json_data.get("name"),
            'description': json_data.get("description"),
            'status': json_data.get("status") if admin else Status.PENDING,  # Only admin can change status
        }

        # Setting start date
        if "start_date" in json_data:
            try:
                collection["start_date"] = datetime.fromisoformat(json_data.get("start_date"))
            except Exception:
                raise NotAValidStartDate()

        # Setting end date
        if "end_date" in json_data:
            try:
                collection["end_date"] = datetime.fromisoformat(json_data.get("end_date"))
            except Exception:
                raise NotAValidEndDate()

        # Setting nullable fields
        if 'image' in json_data:
            collection['image'] = json_data.get("image")
        if 'reward' in json_data:
            collection['reward'] = json_data.get("reward")
        if 'badges' in json_data:
            collection['badges'] = json_data.get('badges')

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return collection


def encode_collection_status(collected_badges, collection_status, reward):
    if not reward:
        return {
            'collection_status': collection_status,
            'collected_badges': collected_badges
        }

    serialized_reward = json.loads(serializers.serialize("json",
                                                         [reward],
                                                         fields=[
                                                             'reward_code', 'time_awarded',
                                                             'reward']))[0]

    raise Exception()
    reward_fields = serialized_reward['fields']
    if reward_fields.get('collection'):
        reward_fields['collection'] = reward_queries.get_str_by_pk(reward_fields.get('collection'))

    if reward_fields.get('reward'):
        reward = reward_queries.get_reward_by_pk(reward_fields.get("reward"))
        reward_fields['reward'] = reward_utils.encode_rewards_to_json([reward])[0]

    reward_fields['collection_status'] = collection_status
    reward_fields['collected_badges'] = collected_badges

    return reward_fields


def paginator(request, f):
    page_size = request.GET.get('page_size')
    f = f.order_by('status')
    pager = Paginator(f, page_size) if page_size else Paginator(f, 50)

    page = request.GET.get('page')
    try:
        response = pager.page(page)
    except PageNotAnInteger:
        response = pager.page(1)
    except EmptyPage:
        response = pager.page(pager.num_pages)

    return response


class NotAValidStartDate(Exception):
    pass


class NotAValidEndDate(Exception):
    pass


class InvalidJSONData(Exception):
    pass


class NotAValidImage(Exception):
    pass
