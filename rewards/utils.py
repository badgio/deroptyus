import json

from django.core import serializers

from locations import queries as location_queries
from users import queries as user_queries
from .models import Status


def encode_reward_to_json(rewards):
    serialized_rewards = json.loads(serializers.serialize("json",
                                                          rewards,
                                                          fields=[
                                                              'uuid',
                                                              'description',
                                                              'time_redeem',
                                                              'promoter', 'location', 'status', ]))

    tweaked_serialized_rewards = []
    for serialized in serialized_rewards:

        reward_fields = serialized['fields']

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
    except json.JSONDecodeError:
        raise InvalidJSONData()

    return redeem_info


def decode_reward_from_json(data, admin):
    try:
        json_data = json.loads(data)
        reward = {
            'description': json_data.get("description"),
            'location': json_data.get('location'),
            'time_redeem': int(json_data.get('time_redeem')) if json_data.get('time_redeem') else None,
            'status': json_data.get("status") if admin else Status.PENDING,  # Only admin can change status
        }
    except json.JSONDecodeError:
        raise InvalidJSONData()

    return reward


class InvalidJSONData(Exception):
    pass
