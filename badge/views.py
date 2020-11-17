from django.http import *
from . import queries
from .models import Badge
from location.models import Status
from django.core import serializers

import json


def badge(request):
    if request.method == 'POST':

        try:
            data = json.loads(request.body)

            name = data.get("name")
            description = data.get("description", None)
            nfc_tag = data.get("nfc_tag", None)
            image = data.get("image", None)
            location = data.get("location", None)
            status = data.get("status", Status.WAIT)
            date_start = data.get("date_start", None)
            date_end = data.get("date_end", None)

            if not name:
                raise HttpResponse(
                    status=400, reason="Bad Request: Need name and description")

            badge_to_create = {
                'name': name,
                'description': description,
                'nfc_tag': nfc_tag,
                'image': image,
                'location': location,
                'status': status,
                'date_start': date_start,
                'date_end': date_end,
            }
            created = queries.create_badge(badge_to_create)
            badge_serialize = serializers.serialize("json",
                                                    Badge.objects.filter(
                                                        pk=created.pk),
                                                    fields=[
                                                        'name', 'description', 'nfc_tag', 'image', 'location',
                                                        'status', 'date_start', 'date_end'])
            return JsonResponse(json.loads(badge_serialize)[0]["fields"])

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't post Badge")

    if request.method == 'GET':

        try:
            badges = queries.get_badge()
            badge_serialize = serializers.serialize("json",
                                                       badges,
                                                       fields=[
                                                           'name', 'description', 'nfc_tag', 'image', 'location',
                                                           'status', 'date_start', 'date_end'])
            return JsonResponse([i["fields"] for i in json.loads(badge_serialize)], safe=False)

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't get Badge")

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_badge(request, uuid):
    if request.method == 'GET':
        try:
            get_badge = queries.get_badge_by_uuid(uuid)
            if badge:
                badge_serialize = serializers.serialize("json",
                                                           get_badge.objects.filter(pk=get_badge.pk),
                                                           fields=[
                                                               'name', 'description', 'nfc_tag', 'image', 'location',
                                                               'status', 'date_start', 'date_end'])
                return JsonResponse(json.loads(badge_serialize)[0]["fields"])

            else:
                HttpResponse(status=400, reason="Bad request: Error on Get")

        except:
            HttpResponse(status=400, reason="Bad request: Error on Get")

    elif request.method == 'DELETE':

        try:

            result = queries.delete_badge_by_uuid(uuid)
            if result:
                return HttpResponse("Success")
            else:
                return HttpResponse(status=400, reason="Bad request: Error on delete")

        except:
            HttpResponse(status=400, reason="Bad request: Error on Delete")

    elif request.method == 'PUT':

        try:

            if not Badge.objects.filter(pk=uuid):
                HttpResponse(status=404, reason="No Badge found")

            data = json.loads(request.body)

            name = data.get("name")
            description = data.get("description", None)
            nfc_tag = data.get("nfc_tag", None)
            image = data.get("image", None)
            location = data.get("location", None)
            status = data.get("status", Status.WAIT)
            date_start = data.get("date_start", None)
            date_end = data.get("date_end", None)

            if not name:
                raise HttpResponse(
                    status=400, reason="Bad Request: Need name and description")

            badge_to_update = {
                'name': name,
                'description': description,
                'nfc_tag': nfc_tag,
                'image': image,
                'location': location,
                'status': status,
                'date_start': date_start,
                'date_end': date_end,
            }
            updated = queries.update_badge_by_uuid(uuid, badge_to_update)
            badge_serialize = serializers.serialize("json",
                                                       Badge.objects.filter(pk=updated.pk),
                                                       fields=[
                                                           'name', 'description', 'nfc_tag', 'image', 'location',
                                                           'status', 'date_start', 'date_end'])
            return JsonResponse(json.loads(badge_serialize)[0]["fields"])

        except:

            return HttpResponse(status=400, reason="Bad Request: Couldn't update Badge")

    else:

        return HttpResponseNotAllowed(['PUT', 'DELETE', 'GET'])
