import json

from django.core import serializers


def encode_tag_to_json(tags):
    serialized_tags = json.loads(serializers.serialize("json",
                                                       tags,
                                                       fields=[
                                                           'uid', 'last_counter',
                                                           'location', ]))

    return [serialized["fields"] for serialized in serialized_tags]


def decode_tag_from_json(data):
    try:
        json_data = json.loads(data)
        tag = {
            'uid': json_data.get("uid"),
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
            'counter': int(json_data.get("counter"), 16),
            'cmac': json_data.get("cmac"),
        }

    except json.JSONDecodeError:
        raise InvalidJSONData()

    return info


class InvalidJSONData(Exception):
    pass
