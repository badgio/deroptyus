from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from firebase.auth import InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist
from . import utils, queries
from .models import Collection, CollectionFilter
from .utils import paginator

# Views


def collections(request):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        return handle_create_collection(request, user)

    elif request.method == 'GET':

        return handle_get_collections(request, user)

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_collection(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_collection(request, uuid, user)

    elif request.method == 'PATCH':

        return handle_patch_collection(request, uuid, user)

    elif request.method == 'DELETE':

        return handle_delete_collection(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET', 'PATCH', 'DELETE'])


def status(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_collection_status(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET'])


# Auxiliary functions for the Views

def handle_create_collection(request, user):
    # Checking permissions
    if user.has_perm('badge_collections.add_collection'):

        # Unserializing
        try:
            unserialized_collection = utils.decode_collection_from_json(request.body, False)

            # Required fields
            if not unserialized_collection.get("name") or not unserialized_collection.get("description"):
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

            created_collection = queries.create_collection(unserialized_collection, user.id)

        except queries.NotAValidLocation:
            return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")
        except queries.NotAValidReward:
            return HttpResponse(status=400, reason="Bad Request: Invalid Reward UUID provided.")
        except utils.NotAValidImage:
            return HttpResponse(status=400, reason="Bad Request: Invalid image provided")
        except queries.EndDateNotAfterStartDate:
            return HttpResponse(status=400, reason="Bad Request: Ending date must be later than Starting date")
        except queries.NotEveryBadgeExists:
            return HttpResponse(status=400, reason="Bad Request: Not every Badge UUID provided exists")

        # Serializing
        serialized_collection = utils.encode_collection_to_json([created_collection])[0]
        return JsonResponse(serialized_collection, safe=False, status=201)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to add a collection")


def handle_get_collections(request, user):
    # Checking permissions (possibly needs the permission to see if the collection is related to this user)
    if user.has_perm('badge_collections.view_collection'):

        f = CollectionFilter(request.GET, queryset=Collection.objects.all()).qs

        response = paginator(request, f)

        return JsonResponse(utils.encode_collection_to_json(response), safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view collections")


def handle_get_collection(request, uuid, user):
    # Checking permissions
    if user.has_perm('badge_collections.view_collection'):

        # Executing the query
        try:
            selected_collection = queries.get_collection_by_uuid(uuid)
        except Collection.DoesNotExist:
            return HttpResponse(status=400, reason="Bad request: Error no collection with that UUID")

        # Serializing
        serialized_collection = utils.encode_collection_to_json([selected_collection])[0]

        return JsonResponse(serialized_collection, safe=False)

    else:

        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view this collection")


def handle_patch_collection(request, uuid, user):
    try:
        collection_to_patch = queries.get_collection_by_uuid(uuid)
    except Collection.DoesNotExist:
        return HttpResponse(status=404, reason="Bad request: Error no collection with that UUID")

    # Checking if it's admin or the promoter that created the collection
    if not user.has_perm('badge_collections.change_collection') and collection_to_patch.promoter.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to delete this collection")

    # Unserializing
    try:
        unserialized_patch_collection = utils.decode_collection_from_json(request.body,
                                                                          user.has_perm(
                                                                              'collections.change_collection'))
    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        updated_collection = queries.patch_collection_by_uuid(uuid, unserialized_patch_collection)

    except utils.NotAValidImage:
        return HttpResponse(status=400, reason="Bad Request: Invalid image provided")
    except queries.NotAValidLocation:
        return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")
    except queries.NotAValidReward:
        return HttpResponse(status=400, reason="Bad Request: Invalid Reward UUID provided.")
    except queries.StartDateAfterEndDate:
        return HttpResponse(status=400, reason="Bad Request: Starting date must be before the Ending date")
    except queries.EndDateNotAfterStartDate:
        return HttpResponse(status=400, reason="Bad Request: Ending date must be later than Starting date")
    except queries.NotEveryBadgeExists:
        return HttpResponse(status=400, reason="Bad Request: Not every Badge UUID provided exists")
    except queries.BadgesMustBeApproved:
        return HttpResponse(status=400, reason="Bad Request: Badges must be approved for Collection approval")
    except queries.RewardMustBeApproved:
        return HttpResponse(status=400, reason="Bad Request: Reward must be approved for Collection approval")

    # Serializing
    serialized_collection = utils.encode_collection_to_json([updated_collection])[0]
    return JsonResponse(serialized_collection, safe=False)


def handle_delete_collection(request, uuid, user):
    # Checking permissions
    try:
        collection = queries.get_collection_by_uuid(uuid)

        # Checking if it's admin or the promoter that created the collection
        if not user.has_perm('badge_collections.delete_collection') and collection.promoter.user != user:
            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to delete this collection")

    except Collection.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No collection by that UUID")

    # Exectuing query
    success = queries.delete_collection_by_uuid(uuid)
    if success:
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, reason="Bad request: Failed to delete")


def handle_get_collection_status(request, uuid, user):
    # Checking permissions
    if user.has_perm('badge_collections.check_collection_status'):

        # Executing query
        try:
            collection_status, reward = queries.get_collection_status(uuid, user)

        except Collection.DoesNotExist:
            return HttpResponse(status=404,
                                reason="Not Found: No Collection by that UID")

        # Serializing
        serialized_collection_status = utils.encode_collection_status(collection_status, reward)
        return JsonResponse(serialized_collection_status, safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to check the completion status of a collection")


def stats_collection(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_stats_collection(request, uuid, user)

    else:

        return HttpResponseNotAllowed(['GET'])


def handle_get_stats_collection(request, uuid, user):
    try:
        collection = queries.get_collection_by_uuid(uuid)
    except Collection.DoesNotExist:
        return HttpResponse(status=404, reason="Not Found: No Collection by that UUID")

    # Checking if it's admin or the promoter that created the collection
    if not user.has_perm('badges_collections.view_stats') and collection.promoter.user != user:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view statistics about this collection")

    # Executing the query
    statistics = queries.get_collection_stats(uuid)

    # Serializing
    # serialized_statistics = utils.encode_statistics_to_json(statistics)

    return JsonResponse(statistics, safe=False)
