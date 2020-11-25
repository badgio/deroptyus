import json

from django.contrib.auth import authenticate
from django.core import serializers
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from firebase.auth import InvalidIdToken, NoTokenProvided
from users.models import ManagerUser
from . import queries
from .models import Location, ManagerLocation, Status


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
                data = json.loads(request.body)

                name = data.get("name")
                description = data.get("description")
                latitude = data.get("latitude", None)
                longitude = data.get("longitude", None)
                website = data.get("website", None)
                social_media = data.get("social_media", None)
                image = data.get("image", None)
                status = data.get("status", Status.WAIT)

                if not (name and description):
                    return HttpResponse(
                        status=400, reason="Bad Request: Need name and description")

                location = {
                    'name': name,
                    'description': description,
                    'latitude': latitude,
                    'longitude': longitude,
                    'social_media': social_media,
                    'website': website,
                    'image': image,
                    'status': status,
                }

                # Getting the manager that's creating the location
                manager = ManagerUser.objects.get(user_id=user)

                created = queries.create_location(location, manager)
                location_serialize = json.loads(serializers.serialize("json",
                                                                      [created],
                                                                      fields=[
                                                                          'uuid', 'name',
                                                                          'description', 'website',
                                                                          'latitude', 'longitude',
                                                                          'image',
                                                                          'status']))[0]["fields"]

                social_media = queries.get_social_media_by_id(created.pk)

                location_serialize['social_media'] = serialize_social_media(social_media)

                return JsonResponse(location_serialize)

            except Exception:

                return HttpResponse(status=400, reason="Bad Request: Couldn't post Locations")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission required to add a location")

    elif request.method == 'GET':

        # Possibly needs the permission to see if the location is related to this user
        if user.has_perm('location.view_location'):

            try:
                all_location = queries.get_location()
                location_serialize = serializers.serialize("json",
                                                           all_location,
                                                           fields=(
                                                               'uuid', 'name',
                                                               'description', 'website',
                                                               'latitude', 'longitude',
                                                               'image', 'status'))

                to_return = []
                for i in json.loads(location_serialize):
                    current = i["fields"]
                    social_media = queries.get_social_media_by_id(i['pk'])
                    if social_media:
                        social_media_serialize = json.loads(serializers.serialize("json",
                                                                                  social_media,
                                                                                  fields=['social_media',
                                                                                          'link']))
                        a = {}
                        for i in range(len(social_media_serialize)):
                            a[social_media_serialize[i]["fields"]["social_media"]
                            ] = social_media_serialize[i]["fields"]["link"]
                        current['social_media'] = a
                    to_return.append(current)

                return JsonResponse(to_return, safe=False)

            except Exception:

                return HttpResponse(status=400, reason="Bad Request: Couldn't get Locations")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission required to view locations")

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

        # Possibly needs the permission to see if the location is related to this user
        if user.has_perm('location.view_location'):

            try:
                get_location = queries.get_location_by_uuid(uuid)
                social_media = queries.get_social_media_by_id(get_location.id)
                if get_location:
                    location_serialize = serializers.serialize("json",
                                                               [get_location],
                                                               fields=[
                                                                   'uuid', 'name',
                                                                   'description', 'website',
                                                                   'latitude', 'longitude',
                                                                   'image', 'status'])
                    return_json = json.loads(location_serialize)[0]["fields"]

                    if social_media:
                        social_media_serialize = json.loads(serializers.serialize("json",
                                                                                  social_media,
                                                                                  fields=['social_media',
                                                                                          'link']))
                        a = {}
                        for i in range(len(social_media_serialize)):
                            a[social_media_serialize[i]["fields"]["social_media"]
                            ] = social_media_serialize[i]["fields"]["link"]
                        return_json['social_media'] = a

                    return JsonResponse(return_json)

                else:
                    HttpResponse(
                        status=400, reason="Bad request: Error on Get")

            except Exception:
                HttpResponse(status=400, reason="Bad request: Error on Get")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission required to view this location")

    elif request.method == 'DELETE':

        try:

            location = Location.objects.get(uuid=uuid)

            # Creating a backdoor so admins can delete managers' locations
            if not user.is_superuser:

                # Checking if it's a manager that's deleting the location
                manager = ManagerUser.objects.get(user_id=user)

                # Checking if the manager owns the location
                ManagerLocation.objects.get(manager=manager, location=location)

            result = queries.delete_location_by_uuid(uuid)
            if result:
                return HttpResponse("Success")
            else:
                return HttpResponse(status=400, reason="Bad request: Error on delete")

        except (ManagerLocation.DoesNotExist, ManagerUser.DoesNotExist):

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission required to delete this location")

        except Location.DoesNotExist:

            return HttpResponse(status=404, reason="Not Found: No Location by that UUID")

        except Exception:

            return HttpResponse(status=400, reason="Bad request: Error on Delete")

    elif request.method == 'PATCH':

        try:

            location = Location.objects.get(uuid=uuid)

            # Creating a backdoor so admins can delete managers' locations
            if not user.is_superuser:

                # Checking if it's a manager that's deleting the location
                manager = ManagerUser.objects.get(user_id=user)

                # Checking if the manager owns the location
                ManagerLocation.objects.get(manager=manager,location=location)

            data = json.loads(request.body)

            name = data.get("name", None)
            description = data.get("description", None)
            latitude = data.get("latitude", None)
            longitude = data.get("longitude", None)
            website = data.get("website", None)
            social_media = data.get("social_media", None)
            image = data.get("image", None)
            status = data.get("status", None)

            location = {
                'uuid': uuid,
                'name': name,
                'description': description,
                'latitude': latitude,
                'longitude': longitude,
                'social_media': social_media,
                'website': website,
                'image': image,
                'status': status,
            }
            updated = queries.patch_location_by_uuid(uuid, location)
            location_serialize = json.loads(serializers.serialize("json",
                                                                  [updated],
                                                                  fields=[
                                                                      'uuid', 'name',
                                                                      'description', 'website',
                                                                      'latitude', 'longitude',
                                                                      'image',
                                                                      'status']))[0]["fields"]

            social_media = queries.get_social_media_by_id(updated.id)

            location_serialize['social_media'] = serialize_social_media(social_media)

            return JsonResponse(location_serialize)


        except (ManagerLocation.DoesNotExist, ManagerUser.DoesNotExist):

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission required to patch this location")

        except Location.DoesNotExist:

            return HttpResponse(status=404, reason="Not Found: No Location by that UUID")

        except Exception:

            return HttpResponse(status=400, reason=f"Bad Request: Couldn't update Locations")

    else:

        return HttpResponseNotAllowed(['PATCH', 'DELETE', 'GET'])


def serialize_social_media(social_media):
    if social_media:
        social_media_serialize = json.loads(serializers.serialize("json",
                                                                  social_media,
                                                                  fields=['social_media',
                                                                          'link']))
        a = {}
        for i in range(len(social_media_serialize)):
            a[social_media_serialize[i]["fields"]["social_media"]
            ] = social_media_serialize[i]["fields"]["link"]
