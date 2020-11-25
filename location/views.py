from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from . import queries
from .models import Location, Status
from django.core import serializers
from base64 import b64encode
import json


def locations(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)

            name = data.get("name")
            description = data.get("description")

            if not (name and description):
                return HttpResponse(
                    status=400, reason="Bad Request: Need name and description")

            location = {
                'name': name,
                'description': description,
                'latitude': data.get("latitude"),
                'longitude': data.get("longitude"),
                'social_media': data.get("social_media"),
                'website': data.get("website"),
                'image': data.get("image"),
                'status': data.get("status", Status.WAIT)
            }

            created = queries.create_location(location)
            location_serialize = queries.serialize_json_location([queries.create_location(location)])[0]["fields"]
            location_serialize['social_media'] = queries.serialize_social_media(queries.get_social_media_by_id(created.pk))

            return JsonResponse(location_serialize)

        except Exception as e:

            return HttpResponse(status=400, reason=f"Bad Request: Couldn't post Locations {e}")

    if request.method == 'GET':

        try:
            all_location = queries.get_location()
            location_serialize = queries.serialize_json_location(all_location)

            to_return = []
            for i in location_serialize:

                current = i["fields"]
                current['social_media'] = queries.serialize_social_media(queries.get_social_media_by_id(i['pk']))

                if current['image']:
                    encoder = b64encode(open(current['image'], 'rb').read())
                    current['image'] = encoder.decode('utf-8')

                to_return.append(current)

            return JsonResponse(to_return, safe=False)

        except Exception as e:

            return HttpResponse(status=400, reason=f"Bad Request: Failed get Locations {e}")

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_location(request, uuid):
    if request.method == 'GET':
        try:
            get_location = queries.get_location_by_uuid(uuid)
            social_media = queries.get_social_media_by_id(get_location.id)
            if get_location:
                location_serialize = queries.serialize_json_location([get_location])[0]["fields"]
                location_serialize['social_media'] = queries.serialize_social_media(social_media)

                return JsonResponse(location_serialize)

            else:
                HttpResponse(status=400, reason="Bad request: Error no Location with that UUID")

        except Exception as e:
            HttpResponse(status=400, reason=f"Bad request: Error on Get {e}")

    elif request.method == 'DELETE':

        try:

            result = queries.delete_location_by_uuid(uuid)
            if result:
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, reason="Bad request: Failed to delete")

        except Exception as e:
            HttpResponse(status=400, reason=f"Bad request: Error on Delete {e}")

    elif request.method == 'PATCH':

        try:

            if not Location.objects.filter(uuid=uuid):
                HttpResponse(status=404, reason="No Location found")

            data = json.loads(request.body)

            location = {
                'uuid': uuid,
                'name': data.get("name"),
                'description': data.get("description"),
                'latitude': data.get("latitude"),
                'longitude': data.get("longitude"),
                'social_media': data.get("social_media"),
                'website': data.get("website"),
                'image': data.get("image"),
                'status': data.get("status")
            }
            updated = queries.patch_location_by_uuid(uuid, location)
            location_serialize = queries.serialize_json_location([updated])[0]["fields"]

            social_media = queries.get_social_media_by_id(updated.id)

            location_serialize['social_media'] = queries.serialize_social_media(social_media)

            return JsonResponse(location_serialize)

        except Exception as e:

            return HttpResponse(status=400, reason=f"Bad Request: Couldn't update Locations {e}")

    else:

        return HttpResponseNotAllowed(['PATCH', 'DELETE', 'GET'])
