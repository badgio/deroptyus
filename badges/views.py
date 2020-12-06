from base64 import b64encode

from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed

from firebase.auth import InvalidIdToken, NoTokenProvided
from users.models import PromoterUser
from . import queries
from .models import Badge


def badges(request):
    # Authenticating user
    try:
        user = authenticate(request)
        if not user:
            raise NoTokenProvided()
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'POST':

        if user.has_perm('badges.add_badge'):

            try:
                badge = queries.decode_badge(request.body, user.is_superuser)

                if not (badge["name"] and badge["description"]):
                    return HttpResponse(
                        status=400, reason="Bad Request: Need name and description")

                # Getting the promoter that's creating the badge
                promoter = PromoterUser.objects.get(user_id=user)

                created = queries.create_badge(badge, promoter)
                badge_serialize = queries.encode_badge([created])[0]["fields"]

                return JsonResponse(badge_serialize, status=201)

            except queries.NotAValidLocation:
                return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")

            except queries.NotAValidImage:
                return HttpResponse(status=400, reason="Bad Request: Invalid image provided")

            except queries.NotAValidStartDate:
                return HttpResponse(status=400, reason="Bad Request: Starting date format must be: "
                                                       "YYYY-MM-DDTHH:MM:SS")
            except queries.NotAValidEndDate:
                return HttpResponse(status=400, reason="Bad Request: Ending date format must be: "
                                                       "YYYY-MM-DDTHH:MM:SS")
            except queries.EndDateNotAfterStartDate:
                return HttpResponse(status=400, reason="Bad Request: Ending date must be later than Starting date")

            except Exception as e:
                return HttpResponse(status=400, reason=f"Bad Request: Could not post Badges {e}")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to add a badge")

    elif request.method == 'GET':

        # Possibly needs the permission to see if the badge is related to this user
        if user.has_perm('badges.view_badge'):

            try:

                all_badge = queries.get_badge()
                badge_serialize = queries.encode_badge(all_badge)

                to_return = []
                for i in badge_serialize:

                    current = i["fields"]

                    if current['image']:
                        encoder = b64encode(open(current['image'], 'rb').read())
                        current['image'] = encoder.decode('utf-8')

                    to_return.append(current)

                return JsonResponse(to_return, safe=False)

            except Exception as e:
                return HttpResponse(status=400, reason=f"Bad Request: Could not get Badges {e}")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to view badges")

    else:

        return HttpResponseNotAllowed(['POST', 'GET'])


def crud_badge(request, uuid):
    # Authenticating user
    try:
        user = authenticate(request)
    except (InvalidIdToken, NoTokenProvided):
        return HttpResponse(status=401,
                            reason="Unauthorized: Operation needs authentication")

    if request.method == 'GET':

        if user.has_perm('badges.view_badge'):

            try:
                get_badge = queries.get_badge_by_uuid(uuid)

                badge_serialize = queries.encode_badge([get_badge])[0]["fields"]
                return JsonResponse(badge_serialize)

            except Badge.DoesNotExist:
                return HttpResponse(status=400, reason="Bad request: Error no badge with that UUID")

            except Exception as e:
                return HttpResponse(status=400, reason=f"Bad request: Error on Get {e}")

        else:

            return HttpResponse(status=403,
                                reason="Forbidden: Current user does not have the permission"
                                       " required to view this badge")

    elif request.method == 'DELETE':

        try:

            badge = queries.get_badge_by_uuid(uuid)

            # Checking if it's admin or the promoter that created the badge
            if not user.is_superuser and badge.promoter.user != user:
                return HttpResponse(status=403,
                                    reason="Forbidden: Current user does not have the permission"
                                           " required to delete this badge")

            result = queries.delete_badge_by_uuid(uuid)
            if result:
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, reason="Bad request: Failed to delete")

        except Badge.DoesNotExist:
            return HttpResponse(status=404, reason="Not Found: No badge by that UUID")

        except Exception as e:
            return HttpResponse(status=400, reason=f"Bad request: Error on Delete {e}")

    elif request.method == 'PATCH':

        try:

            badge = queries.get_badge_by_uuid(uuid)

            # Checking if it's admin or the promoter that created the badge
            if not user.is_superuser and badge.promoter.user != user:
                return HttpResponse(status=403,
                                    reason="Forbidden: Current user does not have the permission"
                                           " required to delete this badge")

            patch_badge = queries.decode_badge(request.body, user.is_superuser)
            patch_badge['uuid'] = uuid

            updated = queries.patch_badge_by_uuid(uuid, patch_badge)
            badge_serialize = queries.encode_badge([updated])[0]["fields"]

            return JsonResponse(badge_serialize)

        except Badge.DoesNotExist:
            return HttpResponse(status=404, reason="Not Found: No badge by that UUID")

        except queries.NotAValidImage:
            return HttpResponse(status=400, reason="Bad Request: Invalid image provided")

        except queries.NotAValidLocation:
            return HttpResponse(status=400, reason="Bad Request: A valid Location UUID must be provided")

        except Exception as e:
            return HttpResponse(status=400, reason=f"Bad Request: Could not update badges {e}")

    else:

        return HttpResponseNotAllowed(['PATCH', 'DELETE', 'GET'])
