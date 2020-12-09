import json
from datetime import date

from django.core import serializers


def encode_apper_to_json(appers):
    serialized_users = json.loads(serializers.serialize('json',
                                                        appers,
                                                        fields=(
                                                            'email', 'name',
                                                            'date_birth', 'country', 'city', 'gender',
                                                            'date_joined')))
    return [serialized["fields"] for serialized in serialized_users]


def decode_apper_from_json(data):
    try:
        # Loading from JSON
        json_data = json.loads(data)
        # Building App User dict
        apper = {
            "email": json_data.get("email"),
            "password": json_data.get("password"),
            "name": json_data.get("name"),
            "country": json_data.get("country"),
            "city": json_data.get("city"),
            "gender": json_data.get("gender"),
        }
        # Validating date of birth
        if "date_birth" in json_data:
            try:
                apper["date_birth"] = date.fromisoformat(json_data.get("date_birth"))
            except Exception:
                raise NotAValidDateOfBirth()

    except json.JSONDecodeError:
        raise InvalidJSONData()

    return apper


def encode_manager_to_json(managers):
    serialized_users = json.loads(serializers.serialize('json',
                                                        managers,
                                                        fields=(
                                                            'email',
                                                            'date_joined')))
    return [serialized["fields"] for serialized in serialized_users]


def decode_manager_from_json(data):
    try:
        # Loading from JSON
        json_data = json.loads(data)
        # Building App User dict
        manager = {
            "email": json_data.get("email"),
            "password": json_data.get("password"),
        }
    except json.JSONDecodeError:
        raise InvalidJSONData()

    return manager


def encode_promoter_to_json(promoters):
    serialized_users = json.loads(serializers.serialize('json',
                                                        promoters,
                                                        fields=(
                                                            'email',
                                                            'date_joined')))
    return [serialized["fields"] for serialized in serialized_users]


def decode_promoter_from_json(data):
    try:
        # Loading from JSON
        json_data = json.loads(data)
        # Building App User dict
        manager = {
            "email": json_data.get("email"),
            "password": json_data.get("password"),
        }
    except json.JSONDecodeError:
        raise InvalidJSONData()

    return manager


class NotAValidDateOfBirth(Exception):
    pass


class InvalidJSONData(Exception):
    pass
