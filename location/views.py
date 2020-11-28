import json
from base64 import b64encode

from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from firebase.auth import InvalidIdToken, NoTokenProvided
from users.models import ManagerUser
from . import queries
from .models import Location


def locations(request):
    # Authenticating user
    try:
        user = authenticate(request)
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        if user.has_perm('location.add_location'):

            try:
                location = queries.decode(json.loads(request.body))

                if not (location.name and location.description):
                    return HttpResponse(
                        status=400, reason="Bad Request: Need name and description")

                # Getting the manager that's creating the location
                manager = ManagerUser.objects.get(user_id=user)

                created = queries.create_location(location, manager)
                location_serialize = queries.serialize_json_location([created])[0]["fields"]

                return JsonResponse(location_serialize)

            except Exception as e:

                return HttpResponse(status=400, reason=f"Bad Request: Couldn't post Locations {e}")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to add a location")

    elif request.method == 'GET':

        # Possibly needs the permission to see if the location is related to this user
        if user.has_perm('location.view_location'):

            try:

                all_location = queries.get_location()
                location_serialize = queries.serialize_json_location(all_location)

                to_return = []
                for i in location_serialize:

                    current = i["fields"]

                    if current['image']:
                        encoder = b64encode(open(current['image'], 'rb').read())
                        current['image'] = encoder.decode('utf-8')

                    to_return.append(current)

                return JsonResponse(to_return, safe=False)

            except Exception:

                return HttpResponse(status=400, reason="Bad Request: Couldn't get Locations")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to view locations")

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_location(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        if user.has_perm('location.view_location'):

            try:
                get_location = queries.get_location_by_uuid(uuid)

                if get_location:
                    location_serialize = queries.serialize_json_location([get_location])[0]["fields"]
                    return JsonResponse(location_serialize)

                else:
                    HttpResponse(status=400, reason="Bad request: Error no Location with that UUID")

            except Exception as e:
                HttpResponse(status=400, reason=f"Bad request: Error on Get {e}")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to view this location")

    elif request.method == 'DELETE':

        try:

            location = queries.get_location_by_uuid(uuid)

            # Checking if it's admin or the manager that created the location
            if not user.is_superuser and location.manager.user != user:
                return HttpResponse(status=403,
                                    reason="Forbidden: Current user does not have the permission"
                                           " required to delete this location")

            result = queries.delete_location_by_uuid(uuid)
            if result:
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, reason="Bad request: Failed to delete")

        except Location.DoesNotExist:

            return HttpResponse(status=404, reason="Not Found: No Location by that UUID")

        except Exception as e:

            return HttpResponse(status=400, reason=f"Bad request: Error on Delete {e}")

    elif request.method == 'PATCH':

        try:

            location = queries.get_location_by_uuid(uuid)

            # Checking if it's admin or the manager that created the location
            if not user.is_superuser and location.manager.user != user:
                return HttpResponse(status=403,
                                    reason="Forbidden: Current user does not have the permission"
                                           " required to delete this location")

            patch_location = queries.decodeLocation(json.loads(request.body))
            patch_location['uuid'] = uuid

            updated = queries.patch_location_by_uuid(location, patch_location)
            location_serialize = queries.serialize_json_location([updated])[0]["fields"]

            return JsonResponse(location_serialize)

        except Location.DoesNotExist:

            return HttpResponse(status=404, reason="Not Found: No Location by that UUID")

        except Exception as e:

            return HttpResponse(status=400, reason=f"Bad Request: Couldn't update Locations {e}")

    else:

        return HttpResponseNotAllowed(['PATCH', 'DELETE', 'GET'])
