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
            created = queries.create_location(location)
            location_serialize = json.loads(serializers.serialize("json",
                                                                  Location.objects.filter(
                                                                      pk=created.pk),
                                                                  fields=[
                                                                      'uuid', 'name', 'description', 'website', 'latitude',
                                                                      'longitude',
                                                                      'image',
                                                                      'status']))[0]["fields"]

            social_media = queries.get_social_media_id(created.pk)

            if social_media:
                social_media_serialize = json.loads(serializers.serialize("json",
                                                                          social_media,
                                                                          fields=['social_media', 'link']))
                a = {}
                for i in range(len(social_media_serialize)):
                    a[social_media_serialize[i]["fields"]["social_media"]
                      ] = social_media_serialize[i]["fields"]["link"]
                location_serialize['social_media'] = a

            return JsonResponse(location_serialize)

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

            to_return = []
            for i in json.loads(location_serialize):
                current = i["fields"]
                social_media = queries.get_social_media_id(i['pk'])
                if social_media:
                    social_media_serialize = json.loads(serializers.serialize("json",
                                                                              social_media,
                                                                              fields=['social_media', 'link']))
                    a = {}
                    for i in range(len(social_media_serialize)):
                        a[social_media_serialize[i]["fields"]["social_media"]
                          ] = social_media_serialize[i]["fields"]["link"]
                    current['social_media'] = a
                to_return.append(current)

            return JsonResponse(to_return, safe=False)

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't get Locations")

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_location(request, uuid):

    if request.method == 'GET':
        try:
            get_location = queries.get_location_by_uuid(uuid)
            social_media = queries.get_social_media_id(get_location.id)
            if get_location:
                location_serialize = serializers.serialize("json",
                                                           Location.objects.filter(
                                                               pk=get_location.pk),
                                                           fields=[
                                                               'uuid', 'name', 'description', 'website', 'latitude',
                                                               'longitude',
                                                               'image',
                                                               'status'])
                return_json = json.loads(location_serialize)[0]["fields"]

                if social_media:
                    social_media_serialize = json.loads(serializers.serialize("json",
                                                                              social_media,
                                                                              fields=['social_media', 'link']))
                    a = {}
                    for i in range(len(social_media_serialize)):
                        a[social_media_serialize[i]["fields"]["social_media"]
                          ] = social_media_serialize[i]["fields"]["link"]
                    return_json['social_media'] = a

                return JsonResponse(return_json)

            else:
                HttpResponse(
                    status=400, reason="Bad request: Error on Get")

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

            if not Location.objects.filter(uuid=uuid):
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
            updated = queries.update_location_by_uuid(uuid, location)
            location_serialize = json.loads(serializers.serialize("json",
                                                                  Location.objects.filter(
                                                                      pk=updated.pk),
                                                                  fields=[
                                                                      'uuid', 'name', 'description', 'website', 'latitude',
                                                                      'longitude',
                                                                      'image',
                                                                      'status']))[0]["fields"]

            social_media = queries.get_social_media_id(updated.id)

            if social_media:
                social_media_serialize = json.loads(serializers.serialize("json",
                                                                          social_media,
                                                                          fields=['social_media', 'link']))
                a = {}
                for i in range(len(social_media_serialize)):
                    a[social_media_serialize[i]["fields"]["social_media"]
                      ] = social_media_serialize[i]["fields"]["link"]
                location_serialize['social_media'] = a

            return JsonResponse(location_serialize)

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't update Locations")

    else:

        return HttpResponseNotAllowed(['PUT', 'DELETE', 'GET'])
