from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from firebase.auth import InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist
from . import queries, utils
from .models import Tag


# Views


def tags(request):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        return handle_create_tag(request, user)

    elif request.method == 'GET':

        return handle_get_tags(request, user)

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_tag(request, uid):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        return handle_get_tag(request, uid, user)

    elif request.method == 'PATCH':

        return handle_patch_tag(request, uid, user)

    elif request.method == 'DELETE':

        return handle_delete_tag(request, uid, user)

    else:

        return HttpResponseNotAllowed(['GET', 'PATCH', 'DELETE'])


# Auxiliary functions for the Views

def handle_create_tag(request, user):
    # Checking permissions
    if user.has_perm('tags.add_tag'):

        # Unserializing
        try:
            tag = utils.decode_tag_from_json(request.body)

            if not (tag.get("uid") and tag.get("app_key")):
                return HttpResponse(
                    status=400, reason="Bad Request: UID and App Key must be provided")

        except utils.InvalidJSONData:
            return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

        # Executing the query
        try:
            created_tag = queries.create_tag(tag, user.id)
        except queries.NotAValidLocation:
            return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")

        # Serializing
        serialized_tag = utils.encode_tag_to_json([created_tag])[0]
        return JsonResponse(serialized_tag, status=201)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to add a tag")


def handle_get_tags(request, user):
    # Checking permissions
    if user.has_perm('tags.view_tag'):

        # Executing the query
        all_tags = queries.get_tags()

        # Serializing
        serialized_tags = utils.encode_tag_to_json(all_tags)

        return JsonResponse(serialized_tags, safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view tags")


def handle_get_tag(request, uid, user):
    # Checking permissions
    if user.has_perm('tags.view_tag'):

        try:
            selected_tag = queries.get_tag_by_uid(uid)
        except Tag.DoesNotExist:
            return HttpResponse(status=400, reason="Bad request: Error no tag with that UID")

        # Serializing
        serialized_tag = utils.encode_tag_to_json([selected_tag])[0]

        return JsonResponse(serialized_tag, safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to view this tag")


def handle_patch_tag(request, uid, user):
    # Checking permissions
    if user.has_perm('tags.change_tag'):

        # Unserializing
        try:
            unserialized_patch_tag = utils.decode_tag_from_json(request.body)
        except utils.InvalidJSONData:
            return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

        # Executing query
        try:
            updated_tag = queries.patch_tag_by_uid(uid, unserialized_patch_tag)

        except Tag.DoesNotExist:
            return HttpResponse(status=404, reason="Not Found: No tag by that UID")
        except queries.NotAValidLocation:
            return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")

        # Serializing
        tag_serialize = utils.encode_tag_to_json([updated_tag])[0]

        return JsonResponse(tag_serialize, safe=False)

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to change this tag")


def handle_delete_tag(request, uid, user):
    # Checking permissions
    if user.has_perm('tags.delete_tag'):

        # Executing query
        try:
            success = queries.delete_tag_by_uid(uid)
            if success:
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, reason="Bad request: Failed to delete")

        except Tag.DoesNotExist:
            return HttpResponse(status=404, reason="Not Found: No tag by that UID")

    else:
        return HttpResponse(status=403,
                            reason="Forbidden: Current user does not have the permission"
                                   " required to delete this tag")
