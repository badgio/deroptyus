from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from firebase.auth import InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist
from . import queries, utils
from .models import Location, LocationFilter
from .utils import paginator


def locations(request):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        return handle_create_location(request, user)

    elif request.method == 'GET':

        return handle_get_locations(request, user)

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_location(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_location(request, uuid, user)

    elif request.method == 'PATCH':

        return handle_patch_location(request, uuid, user)

    elif request.method == 'DELETE':

        return handle_delete_location(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET', 'PATCH', 'DELETE'])


def stats_location(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_stats_location(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET'])


# Auxiliary functions for the Views


def handle_create_location(request, user):
    # Checking permissions
    if user.has_perm('locations.add_location'):

        # Unserializing
        try:
            unserialized_location = utils.decode_location_from_json(request.body, False)

            if not unserialized_location.get("name") or not unserialized_location.get("description"):
                return HttpResponse(status=400, reason="Bad Request: Name and Description must be provided")

        except utils.InvalidJSONData:
            return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

        # Executing query
        try:

            created_location = queries.create_location(unserialized_location, user.id)

        except utils.NotAValidImage:
            return HttpResponse(status=400, reason="Bad Request: Invalid image provided")

        # Serializing
        serialized_location = utils.encode_location_to_json([created_location])[0]
        return JsonResponse(serialized_location, safe=False, status=201)

    else:

        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to add a location")


def handle_get_locations(request, user):
    # Checking permissions (possibly needs the permission to see if the badge is related to this user)
    if user.has_perm('locations.view_location'):

        f = LocationFilter(request.GET, queryset=Location.objects.all()).qs

        response = paginator(request, f)

        return JsonResponse(utils.encode_location_to_json(response), safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view locations")


def handle_get_location(request, uuid, user):
    # Checking permissions
    if user.has_perm('locations.view_location'):

        # Executing the query
        try:
            selected_location = queries.get_location_by_uuid(uuid)
        except Location.DoesNotExist:
            return HttpResponse(status=400, reason="Bad request: No Location with that UUID")

        # Serializing
        serialized_location = utils.encode_location_to_json([selected_location])[0]

        return JsonResponse(serialized_location, safe=False)

    else:

        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view this location")


def handle_patch_location(request, uuid, user):
    try:
        location_to_patch = queries.get_location_by_uuid(uuid)
    except Location.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No Location by that UUID")

    # Checking if it's admin or the manager that created the location
    if not user.has_perm('locations.change_location') and location_to_patch.manager.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to delete this location")

    # Unserializing
    try:
        unserialized_patch_location = utils.decode_location_from_json(request.body,
                                                                      user.has_perm('locations.change_location'))
    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        updated_location = queries.patch_location_by_uuid(uuid, unserialized_patch_location)

    except utils.NotAValidImage as e:
        return HttpResponse(status=400, reason=f"Bad Request: Invalid image provided {e}")

    # Serializing
    serialized_location = utils.encode_location_to_json([updated_location])[0]
    return JsonResponse(serialized_location, safe=False)


def handle_delete_location(request, uuid, user):
    # Checking permissions
    try:
        location = queries.get_location_by_uuid(uuid)

        # Checking if it's admin or the manager that created the location
        if not user.has_perm('locations.delete_location') and location.manager.user != user:
            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to delete this location")

    except Location.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No Location by that UUID")

    # Executing query
    success = queries.delete_location_by_uuid(uuid)
    if success:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, reason="Bad request: Failed to delete")


def handle_get_stats_location(request, uuid, user):
    try:
        location = queries.get_location_by_uuid(uuid)
    except Location.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No Location by that UUID")

    # Checking if it's admin or the manager that created the location
    if not user.has_perm('locations.view_stats') and location.manager.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view statistics about this location")

    # Executing the query
    statistics = queries.get_location_stats(uuid)

    # Serializing
    # serialized_statistics = utils.encode_statistics_to_json(statistics)

    return JsonResponse(statistics, safe=False)
