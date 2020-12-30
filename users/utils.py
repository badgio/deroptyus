import json
from datetime import date

from django.core import serializers

from users.models import AdminUser, ManagerUser, PromoterUser, AppUser


def encode_user_to_json(users):
    serialized_user = {}

    # Iterating every user type (e.g AppUser)
    for user in users:

        if isinstance(user, AdminUser):
            serialized_user["admin_info"] = encode_admin_to_json(user)
            if "email" not in serialized_user:
                serialized_user["email"] = serialized_user["admin_info"]["email"]
            del serialized_user["admin_info"]["email"]
        elif isinstance(user, ManagerUser):
            serialized_user["manager_info"] = encode_manager_to_json(user)
            if "email" not in serialized_user:
                serialized_user["email"] = serialized_user["manager_info"]["email"]
            del serialized_user["manager_info"]["email"]
        elif isinstance(user, PromoterUser):
            serialized_user["promoter_info"] = encode_promoter_to_json(user)
            if "email" not in serialized_user:
                serialized_user["email"] = serialized_user["promoter_info"]["email"]
            del serialized_user["promoter_info"]["email"]
        elif isinstance(user, AppUser):
            serialized_user["mobile_info"] = encode_apper_to_json(user)
            if "email" not in serialized_user:
                serialized_user["email"] = serialized_user["mobile_info"]["email"]
            del serialized_user["mobile_info"]["email"]

    return serialized_user


def decode_user_from_json(data):

    try:

        json_data = json.loads(data)
        user = {}

        if "email" in json_data:
            user["email"] = json_data.get("email")
        if "password" in json_data:
            user["password"] = json_data.get("password")

        if "manager_info" in json_data:
            user["manager_info"] = decode_manager_from_json(json.dumps(json_data.get("manager_info")))
            del user["manager_info"]["email"]
            del user["manager_info"]["password"]
        else:
            user["manager_info"] = {}

        if "promoter_info" in json_data:
            user["promoter_info"] = decode_promoter_from_json(json.dumps(json_data.get("promoter_info")))
            del user["promoter_info"]["email"]
            del user["promoter_info"]["password"]
        else:
            user["promoter_info"] = {}

        if "mobile_info" in json_data:
            user["mobile_info"] = decode_apper_from_json(json.dumps(json_data.get("mobile_info")))
            del user["mobile_info"]["email"]
            del user["mobile_info"]["password"]
        else:
            user["mobile_info"] = {}

        if "admin_info" in json_data:
            user["admin_info"] = decode_admin_from_json(json.dumps(json_data.get("admin_info")))
            del user["admin_info"]["email"]
            del user["admin_info"]["password"]
        else:
            user["admin_info"] = {}

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return user


def encode_apper_to_json(apper):
    serialized_user = json.loads(serializers.serialize('json',
                                                       [apper],
                                                       fields=(
                                                           'email', 'name',
                                                           'date_birth', 'country', 'city', 'gender',
                                                           'date_joined')))[0]

    return serialized_user["fields"]


def decode_apper_from_json(data):
    try:
        # Loading from JSON
        json_data = json.loads(data)
        # Building App User dict
        apper = {
            "email": json_data.get("email"),
            "password": json_data.get("password")
        }
        if "name" in json_data:
            apper["name"] = json_data.get("name")
        if "country" in json_data:
            apper["country"] = json_data.get("country")
        if "city" in json_data:
            apper["city"] = json_data.get("city")
        if "gender" in json_data:
            apper["gender"] = json_data.get("gender")
        # Validating date of birth
        if "date_birth" in json_data:
            try:
                apper["date_birth"] = date.fromisoformat(json_data.get("date_birth"))
            except Exception:
                raise NotAValidDateOfBirth()

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return apper


def encode_manager_to_json(manager):
    serialized_user = json.loads(serializers.serialize('json',
                                                       [manager],
                                                       fields=(
                                                           'email',
                                                           'date_joined')))[0]
    return serialized_user["fields"]


def decode_manager_from_json(data):
    try:
        # Loading from JSON
        json_data = json.loads(data)
        # Building App User dict
        manager = {
            "email": json_data.get("email"),
            "password": json_data.get("password"),
        }
    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return manager


def encode_promoter_to_json(promoter):
    serialized_user = json.loads(serializers.serialize('json',
                                                       [promoter],
                                                       fields=(
                                                           'email',
                                                           'date_joined')))[0]
    return serialized_user["fields"]


def decode_promoter_from_json(data):
    try:
        # Loading from JSON
        json_data = json.loads(data)
        # Building App User dict
        manager = {
            "email": json_data.get("email"),
            "password": json_data.get("password"),
        }
    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return manager


def encode_admin_to_json(admin):
    serialized_user = json.loads(serializers.serialize('json',
                                                       [admin],
                                                       fields=(
                                                           'email',
                                                           'date_joined')))[0]
    return serialized_user["fields"]


def decode_admin_from_json(data):
    try:
        # Loading from JSON
        json_data = json.loads(data)
        # Building App User dict
        admin = {
            "email": json_data.get("email"),
            "password": json_data.get("password"),
        }
    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return admin


class NotAValidDateOfBirth(Exception):
    pass


class InvalidJSONData(Exception):
    pass
