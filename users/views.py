from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed

from firebase.auth import NoTokenProvided, InvalidIdToken, FirebaseUserDoesNotExist
from . import queries, utils


# Views


def appers(request):
    if request.method == 'POST':
        return handle_create_apper(request)
    else:
        return HttpResponse(status=405, reason=f"Method Not Allowed: {request.method} not supported")


def managers(request):
    if request.method == 'POST':
        return handle_create_manager(request)
    else:
        return HttpResponse(status=405, reason=f"Method Not Allowed: {request.method} not supported")


def promoters(request):
    if request.method == 'POST':
        return handle_create_promoter(request)
    else:
        return HttpResponse(status=405, reason=f"Method Not Allowed: {request.method} not supported")


def profile(request):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided, FirebaseUserDoesNotExist):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == "GET":
        return handle_get_user_profile(request, user)

    elif request.method == "PATCH":
        return handle_patch_user_profile(request, user)

    elif request.method == "DELETE":
        return handle_delete_user_profile(request, user)

    else:
        return HttpResponseNotAllowed(['GET', 'PATCH', 'DELETE'])


# Auxiliary functions for the Views

def handle_create_apper(request):
    # Unserializing
    try:
        unserialized_apper = utils.decode_apper_from_json(request.body)

        if not unserialized_apper.get("email") or not unserialized_apper.get("password"):
            return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")
    except utils.NotAValidDateOfBirth:
        return HttpResponse(status=400, reason="Bad Request: Date of Birth format must be: "
                                               "YYYY-MM-DD")
    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        app_user = queries.create_app_user(unserialized_apper)

    except queries.FirebaseError:
        return HttpResponse(status=503, reason="Internal Server Error: Firebase")

    except queries.AppUserExistsError:
        return HttpResponse(status=409, reason="Conflict: Email already associated with an app user")

    except queries.PermissionGroupError:
        return HttpResponse(status=503, reason="Internal Server Error: Permission Groups not set")

    # Serializing
    serialized_user = utils.encode_apper_to_json(app_user)
    return JsonResponse(serialized_user, status=201)


def handle_create_manager(request):
    # Unserializing
    try:
        unserialized_manager = utils.decode_manager_from_json(request.body)

        if not unserialized_manager.get("email") or not unserialized_manager.get("password"):
            return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")
    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        manager_user = queries.create_manager_user(unserialized_manager)
    except queries.FirebaseError:
        return HttpResponse(status=503, reason="Internal Server Error: Firebase")
    except queries.ManagerExistsError:
        return HttpResponse(status=409, reason="Conflict: Email already associated with a manager")
    except queries.PermissionGroupError:
        return HttpResponse(status=503, reason="Internal Server Error: Permission Groups not set")

    # Serializing

    serialized_user = utils.encode_manager_to_json(manager_user)
    return JsonResponse(serialized_user, status=201)


def handle_create_promoter(request):
    # Unserializing
    try:
        unserialized_promoter = utils.decode_promoter_from_json(request.body)

        # Required fields
        if not unserialized_promoter.get("email") or not unserialized_promoter.get("password"):
            return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")

    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        promoter_user = queries.create_promoter_user(unserialized_promoter)
    except queries.FirebaseError:
        return HttpResponse(status=503, reason="Internal Server Error: Firebase")
    except queries.PromoterExistsError:
        return HttpResponse(status=409, reason="Conflict: Email already associated with a promoter")
    except queries.PermissionGroupError:
        return HttpResponse(status=503, reason="Internal Server Error: Permission Groups not set")

    # Serializing
    serialized_user = utils.encode_promoter_to_json(promoter_user)
    return JsonResponse(serialized_user, status=201)


def handle_get_user_profile(request, user):
    # Executing query
    users = [queries.get_admin_user(user),
             queries.get_manager_user(user),
             queries.get_promoter_user(user),
             queries.get_app_user(user)]
    users = [user for user in users if user]

    # Serializing
    serialized_user = utils.encode_user_to_json(users)
    return JsonResponse(serialized_user, status=201, safe=False)


def handle_patch_user_profile(request, user):
    # Unserializing
    try:
        unserialized_user = utils.decode_user_from_json(request.body)
    except utils.InvalidJSONData:
        return HttpResponse(status=400, reason="Bad Request: Malformed JSON object provided")

    # Executing query
    try:
        queries.patch_user(unserialized_user, user)
    except queries.FirebaseError:
        return HttpResponse(status=503, reason="Internal Server Error: Firebase")

    # Serializing
    users = [queries.get_admin_user(user),
             queries.get_manager_user(user),
             queries.get_promoter_user(user),
             queries.get_app_user(user)]
    users = [user for user in users if user]

    serialized_user = utils.encode_user_to_json(users)
    return JsonResponse(serialized_user, status=201, safe=False)


def handle_delete_user_profile(request, user):
    # Executing the Query
    try:
        queries.delete_user(user)
    except queries.FirebaseError:
        return HttpResponse(status=503, reason="Internal Server Error: Firebase")
    except Exception:
        return HttpResponse(status=400, reason="Bad Request: User can't be deleted.")

    return HttpResponse(status=200)
