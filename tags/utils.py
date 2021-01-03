import json

from django.core import serializers

from locations import queries as location_queries
from users import queries as user_queries
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def encode_tag_to_json(tags):
    serialized_tags = json.loads(serializers.serialize("json",
                                                       tags,
                                                       fields=[
                                                           'uid', 'last_counter',
                                                           'location', ]))

    tweaked_serialized_tags = []
    for serialized in serialized_tags:

        reward_fields = serialized['fields']

        if reward_fields.get('location'):
            reward_fields['location'] = location_queries.get_str_by_pk(reward_fields.get('location'))

        if reward_fields.get('admin'):
            reward_fields['admin'] = user_queries.get_str_by_admin_pk(reward_fields.get('admin'))

        tweaked_serialized_tags.append(reward_fields)

    return tweaked_serialized_tags


def decode_tag_from_json(data):
    try:
        json_data = json.loads(data)
        tag = {
            'uid': json_data.get("uid"),
            'counter': json_data.get("counter"),
            'app_key': json_data.get("app_key"),
            'location': json_data.get("location"),
        }

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return tag


def decode_redeem_info_from_json(data):
    try:
        json_data = json.loads(data)
        info = {
            'uid': json_data.get("uid"),
            'counter': json_data.get("counter"),
            'cmac': json_data.get("cmac"),
        }

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return info


def paginator(request, f):
    page_size = request.GET.get('page_size')
    f = f.order_by('uid')
    pager = Paginator(f, page_size) if page_size else Paginator(f, 50)

    page = request.GET.get('page')
    try:
        response = pager.page(page)
    except PageNotAnInteger:
        response = pager.page(1)
    except EmptyPage:
        response = pager.page(pager.num_pages)

    return response


class InvalidJSONData(Exception):
    pass
