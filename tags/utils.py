import json

from django.core import serializers

from locations import queries as location_queries
from users import queries as user_queries


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

    except json.JSONDecodeError:
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

    except json.JSONDecodeError:
        raise InvalidJSONData()

    return info


class InvalidJSONData(Exception):
    pass
