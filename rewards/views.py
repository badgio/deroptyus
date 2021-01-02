from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from firebase.auth import InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist
from . import queries, utils
from .models import Reward


# Views

def rewards(request):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        return handle_create_reward(request, user)

    elif request.method == 'GET':

        return handle_get_rewards(request, user)

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_reward(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_reward(request, uuid, user)

    elif request.method == 'PATCH':

        return handle_patch_reward(request, uuid, user)

    elif request.method == 'DELETE':

        return handle_delete_reward(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET', 'PATCH', 'DELETE'])


def redeem(request):
    # Authenticating user
    try:
        user = authenticate(request)
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        return handle_redeem_reward(request, user)

    else:
        return HttpResponseNotAllowed(['POST'])

def stats_reward(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_stats_reward(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET'])

# Auxiliary functions for the Views

def handle_create_reward(request, user):
    # Checking permissions
    if user.has_perm('rewards.add_reward'):

        # Unserializing
        try:
            unserialized_reward = utils.decode_reward_from_json(request.body, False)

            # Required fields
            if not unserialized_reward.get("name") or not unserialized_reward.get("description"):
                return HttpResponse(status=400, reason="Bad Request: Name and Description must be provided")

        except utils.InvalidJSONData:
            return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

        # Executing the query
        try:

            created_reward = queries.create_reward(unserialized_reward, user.id)

        except utils.NotAValidImage:
            return HttpResponse(status=400, reason="Bad Request: Invalid image provided")

        # Serializing
        serialized_reward = utils.encode_rewards_to_json([created_reward])[0]
        return JsonResponse(serialized_reward, safe=False, status=201)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to add a reward")


def handle_get_rewards(request, user):
    # Checking permissions (possibly needs the permission to see if the reward is related to this user)
    if user.has_perm('rewards.view_reward'):

        # Executing the query
        all_rewards = queries.get_rewards()

        # Serializing
        serialized_rewards = utils.encode_rewards_to_json(all_rewards)

        return JsonResponse(serialized_rewards, safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view rewards")


def handle_get_reward(request, uuid, user):
    # Checking permissions
    if user.has_perm('rewards.view_reward'):

        # Executing the query
        try:
            selected_reward = queries.get_reward_by_uuid(uuid)
        except Reward.DoesNotExist:
            return HttpResponse(status=400, reason="Bad request: Error no reward with that UUID")

        # Serializing
        serialized_reward = utils.encode_rewards_to_json([selected_reward])[0]

        return JsonResponse(serialized_reward, safe=False)

    else:

        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view this reward")


def handle_patch_reward(request, uuid, user):
    try:
        reward_to_patch = queries.get_reward_by_uuid(uuid)
    except Reward.DoesNotExist:
        return HttpResponse(status=404, reason="Bad request: Error no reward with that UUID")

    # Checking if it's admin or the promoter that created the reward
    if not user.has_perm('rewards.change_reward') and reward_to_patch.promoter.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to delete this reward")

    # Unserializing
    try:
        unserialized_patch_reward = utils.decode_reward_from_json(request.body,
                                                                  user.has_perm('rewards.change_reward'))
    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        updated_reward = queries.patch_reward_by_uuid(uuid, unserialized_patch_reward)
    except utils.NotAValidImage:
        return HttpResponse(status=400, reason="Bad Request: Invalid image provided")

    # Serializing
    serialized_reward = utils.encode_rewards_to_json([updated_reward])[0]
    return JsonResponse(serialized_reward, safe=False)


def handle_delete_reward(request, uuid, user):
    # Checking permissions
    try:
        reward = queries.get_reward_by_uuid(uuid)

        # Checking if it's admin or the promoter that created the reward
        if not user.has_perm('rewards.delete_reward') and reward.promoter.user != user:
            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to delete this reward")

    except Reward.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No reward by that UUID")

    # Exectuing query
    success = queries.delete_reward_by_uuid(uuid)
    if success:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, reason="Bad request: Failed to delete")


def handle_redeem_reward(request, user):
    # Checking permissions
    if user.has_perm('rewards.redeem_reward'):

        # Unserializing
        try:
            unserialized_redeem_info = utils.decode_redeem_info_from_json(request.body)

            # Required fields
            if not unserialized_redeem_info.get('reward_code'):
                return HttpResponse(status=400, reason="Bad Request: Reward Code must be provided")

        except utils.InvalidJSONData:
            return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

        # Executing query
        try:
            reward = queries.redeem_reward_by_code(unserialized_redeem_info)

        except queries.NoRewardByThatCode:
            return HttpResponse(status=404,
                                reason="Bad Request: No Reward to redeem by that code")
        except queries.RewardAlreadyRedeemed:
            return HttpResponse(status=410,
                                reason="Gone: Reward by that code already redeemed")
        except queries.RewardNoLongerValid:
            return HttpResponse(status=400,
                                reason="Not Found: The Reward expired")


        # Serializing
        serialized_rewards = utils.encode_rewards_to_json([reward])[0]
        return JsonResponse(serialized_rewards, safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to redeem a reward")

def handle_get_stats_reward(request, uuid, user):
    try:
        reward = queries.get_reward_by_uuid(uuid)
    except Reward.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No Reward by that UUID")

    # Checking if it's admin or the promoter that created the badge
    if not user.has_perm('rewards.view_stats') and reward.promoter.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view statistics about this reward")

    # Executing the query
    statistics = queries.get_reward_stats(uuid)

    # Serializing
    # serialized_statistics = utils.encode_statistics_to_json(statistics)

    return JsonResponse(statistics, safe=False)