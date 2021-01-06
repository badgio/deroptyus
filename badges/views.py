from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

import tags.queries as tags_queries
import tags.utils as tags_utils
from firebase.auth import InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist
from tags import crypto

from . import queries, utils
from .models import Badge, BadgeFilter
from .utils import paginator

# Views


def badges(request):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        return handle_create_badge(request, user)

    elif request.method == 'GET':

        return handle_get_badges(request, user)

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_badge(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_badge(request, uuid, user)

    elif request.method == 'PATCH':

        return handle_patch_badge(request, uuid, user)

    elif request.method == 'DELETE':

        return handle_delete_badge(request, uuid, user)

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

        return handle_redeem_badge(request, user)

    else:
        return HttpResponseNotAllowed(['POST'])


def stats_badge(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_stats_badge(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET'])


# Auxiliary functions for the Views

def handle_create_badge(request, user):
    # Checking permissions
    if user.has_perm('badges.add_badge'):

        # Unserializing
        try:
            unserialized_badge = utils.decode_badge_from_json(request.body, False)

            # Required fields
            if not unserialized_badge.get("name") or not unserialized_badge.get("description"):
                return HttpResponse(status=400, reason="Bad Request: Name and Description must be provided")

        except utils.NotAValidStartDate:
            return HttpResponse(status=400, reason="Bad Request: Starting date format must be: "
                                                   "YYYY-MM-DDTHH:MM:SS")
        except utils.NotAValidEndDate:
            return HttpResponse(status=400, reason="Bad Request: Ending date format must be: "
                                                   "YYYY-MM-DDTHH:MM:SS")
        except utils.InvalidJSONData:
            return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

        # Executing the query
        try:

            created_badge = queries.create_badge(unserialized_badge, user.id)

        except queries.NotAValidLocation:
            return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")
        except utils.NotAValidImage:
            return HttpResponse(status=400, reason="Bad Request: Invalid image provided")
        except queries.EndDateNotAfterStartDate:
            return HttpResponse(status=400, reason="Bad Request: Ending date must be later than Starting date")

        # Serializing
        serialized_badge = utils.encode_badge_to_json([created_badge])[0]
        return JsonResponse(serialized_badge, safe=False, status=201)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to add a badge")


def handle_get_badges(request, user):
    # Checking permissions (possibly needs the permission to see if the badge is related to this user)
    if user.has_perm('badges.view_badge'):

        f = BadgeFilter(request.GET, queryset=Badge.objects.all()).qs

        response = paginator(request, f)

        return JsonResponse(utils.encode_badge_to_json(response), safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view badges")


def handle_get_badge(request, uuid, user):
    # Checking permissions
    if user.has_perm('badges.view_badge'):

        # Executing the query
        try:
            selected_badge = queries.get_badge_by_uuid(uuid)
        except Badge.DoesNotExist:
            return HttpResponse(status=400, reason="Bad request: Error no badge with that UUID")

        # Serializing
        serialized_badge = utils.encode_badge_to_json([selected_badge])[0]

        return JsonResponse(serialized_badge, safe=False)

    else:

        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view this badge")


def handle_patch_badge(request, uuid, user):
    try:
        badge_to_patch = queries.get_badge_by_uuid(uuid)
    except Badge.DoesNotExist:
        return HttpResponse(status=404, reason="Bad request: Error no badge with that UUID")

    # Checking if it's admin or the promoter that created the badge
    if not user.has_perm('badges.change_badge') and badge_to_patch.promoter.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to delete this badge")

    # Unserializing
    try:
        unserialized_patch_badge = utils.decode_badge_from_json(request.body,
                                                                user.has_perm('badges.change_badge'))
    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        updated_badge = queries.patch_badge_by_uuid(uuid, unserialized_patch_badge)

    except utils.NotAValidImage:
        return HttpResponse(status=400, reason="Bad Request: Invalid image provided")
    except queries.NotAValidLocation:
        return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")
    except queries.StartDateAfterEndDate:
        return HttpResponse(status=400, reason="Bad Request: Starting date must be before the Ending date")
    except queries.EndDateNotAfterStartDate:
        return HttpResponse(status=400, reason="Bad Request: Ending date must be later than Starting date")
    except queries.LocationMustBeApproved:
        return HttpResponse(status=400, reason="Bad Request: Location must be approved for Badge approval")

    # Serializing
    serialized_badge = utils.encode_badge_to_json([updated_badge])[0]
    return JsonResponse(serialized_badge, safe=False)


def handle_delete_badge(request, uuid, user):
    # Checking permissions
    try:
        badge = queries.get_badge_by_uuid(uuid)

        # Checking if it's admin or the promoter that created the badge
        if not user.has_perm('badges.delete_badge') and badge.promoter.user != user:
            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to delete this badge")

    except Badge.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No badge by that UUID")

    # Exectuing query
    success = queries.delete_badge_by_uuid(uuid)
    if success:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, reason="Bad request: Failed to delete")


def handle_redeem_badge(request, user):
    # Checking permissions
    if user.has_perm('badges.redeem_badge'):

        # Unserializing
        try:
            unserialized_redeem_info = tags_utils.decode_redeem_info_from_json(request.body)
        except tags_queries.MissingRedeemInfo as e:
            return HttpResponse(status=400, reason=f"Bad Request: Info not sufficient to redeem tag - {e}")

        # Executing query
        try:
            location_id = tags_queries.redeem_tag(unserialized_redeem_info)

            valid_badges = queries.redeem_badges_by_location(location_id, user.id)

        except (crypto.InvalidUID, crypto.InvalidCounter, crypto.InvalidAppKey, crypto.InvalidCMAC) as e:
            return HttpResponse(status=400, reason=f"Bad Request: {e}")

        except crypto.MessageAuthenticationFailed as e:
            return HttpResponse(status=406, reason=f"Not Acceptable: {e}")

        except tags_queries.NotAValidTagUID:
            return HttpResponse(status=404,
                                reason="Not Found: No Tag by that UID")
        except tags_queries.AlreadyRedeemedTag:
            return HttpResponse(status=410,
                                reason="Gone: The info provided refers to an already redeemed tag")

        # Serializing
        serialized_badges = utils.encode_badge_to_json(valid_badges)
        return JsonResponse(serialized_badges, safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to redeem a badge")


def handle_get_stats_badge(request, uuid, user):
    try:
        badge = queries.get_badge_by_uuid(uuid)
    except Badge.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No Badge by that UUID")

    # Checking if it's admin or the promoter that created the badge
    if not user.has_perm('badges.view_stats') and badge.promoter.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view statistics about this badge")

    # Executing the query
    statistics = queries.get_badge_stats(uuid)

    # Serializing
    # serialized_statistics = utils.encode_statistics_to_json(statistics)

    return JsonResponse(statistics, safe=False)
