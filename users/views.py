from django.http import HttpResponse, JsonResponse

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
    serialized_user = utils.encode_apper_to_json([app_user])[0]
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

    serialized_user = utils.encode_manager_to_json([manager_user])[0]
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
    serialized_user = utils.encode_promoter_to_json([promoter_user])[0]
    return JsonResponse(serialized_user, status=201)
