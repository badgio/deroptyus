from django.http import *
from . import queries
from .models import Location, Status
from django.core import serializers
import json


def locations(request):

    if request.method == 'POST':

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
                raise HttpResponse(
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
            # TODO: Add the social_media to the json return file
            created = queries.create_location(location)
            location_serialize = serializers.serialize("json",
                                                       Location.objects.filter(
                                                           pk=created.pk),
                                                       fields=[
                                                           'uuid', 'name', 'description', 'website', 'latitude',
                                                           'longitude',
                                                           'image',
                                                           'status'])
            return JsonResponse(json.loads(location_serialize)[0]["fields"])

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't post Locations")

    if request.method == 'GET':

        try:
            all_location = queries.get_location()
            location_serialize = serializers.serialize("json",
                                                       all_location,
                                                       fields=(
                                                           'uuid', 'name', 'description', 'website', 'latitude', 'longitude',
                                                           'image',
                                                           'status'))
            return JsonResponse([i["fields"] for i in json.loads(location_serialize)], safe=False)

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't get Locations")

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_location(request, uuid):

    if request.method == 'GET':
        try:
            get_location = queries.get_location_by_uuid(uuid)
            HttpResponse(get_location)
            if get_location:
                location_serialize = serializers.serialize("json",
                                                           Location.objects.filter(
                                                               pk=get_location.pk),
                                                           fields=[
                                                               'uuid', 'name', 'description', 'website', 'latitude',
                                                               'longitude',
                                                               'image',
                                                               'status'])
                return JsonResponse(json.loads(location_serialize)[0]["fields"])

            else:
                HttpResponse(status=400, reason="Bad request: Error on Get")

        except:
            HttpResponse(status=400, reason="Bad request: Error on Get")

    elif request.method == 'DELETE':

        try:

            result = queries.delete_location_by_uuid(uuid)
            if result:
                return HttpResponse("Success")
            else:
                return HttpResponse(status=400, reason="Bad request: Error on delete")

        except:
            HttpResponse(status=400, reason="Bad request: Error on Delete")

    elif request.method == 'PUT':

        try:

            if not Location.objects.filter(pk=uuid):
                HttpResponse(status=404, reason="No Location found")

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
            # TODO: Add the social_media to the json return file
            updated = queries.update_location_by_uuid(uuid, location)
            location_serialize = serializers.serialize("json",
                                                       Location.objects.filter(
                                                           pk=updated.pk),
                                                       fields=[
                                                           'uuid', 'name', 'description', 'website', 'latitude',
                                                           'longitude',
                                                           'image',
                                                           'status'])
            return JsonResponse(json.loads(location_serialize)[0]["fields"])

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't update Locations")

    else:

        return HttpResponseNotAllowed(['PUT', 'DELETE', 'GET'])
