import json

from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse

from . import queries
from .models import AppUser, PromoterUser, ManagerUser


# Create your views here.

def appers(request):
    if request.method == 'POST':

        return create_apper(request)

    else:

        return HttpResponse(status=405, reason=f"Method Not Allowed: {request.method} not supported")


def managers(request):
    if request.method == 'POST':

        return create_manager(request)

    else:

        return HttpResponse(status=405, reason=f"Method Not Allowed: {request.method} not supported")


def promoters(request):
    if request.method == 'POST':

        return create_promoter(request)

    else:

        return HttpResponse(status=405, reason=f"Method Not Allowed: {request.method} not supported")


def create_apper(request):
    try:
        json_data = json.loads(request.body)

        email = json_data["email"]
        password = json_data["password"]
        name = json_data["name"] if "name" in json_data else None
        date_birth = json_data["date_birth"] if "date_birth" in json_data else None
        country = json_data["country"] if "country" in json_data else None
        city = json_data["city"] if "city" in json_data else None
        gender = json_data["gender"] if "gender" in json_data else None

        if email and password:

            try:

                app_user = queries.create_app_user(email, password, name, date_birth, country, city, gender)
                serialized_user = serialize('json',
                                            AppUser.objects.filter(pk=app_user.pk),
                                            fields=(
                                                'email', 'name', 'date_birth', 'country', 'city', 'gender', 'date_joined'))
                user_fields = json.loads(serialized_user)[0]["fields"]

                return JsonResponse(user_fields, status=201)

            except queries.FirebaseError:

                return HttpResponse(status=503, reason="Internal Server Error: Firebase")

            except queries.AppUserExistsError:

                return HttpResponse(status=409, reason="Conflict: Email already associated with an app user")

        else:

            return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")

    except json.JSONDecodeError:

        return HttpResponse(status=400, reason="Bad Request: JSON object expected in POST body")


def create_manager(request):
    try:
        json_data = json.loads(request.body)

        email = json_data["email"]
        password = json_data["password"]

        if email and password:

            try:

                manager_user = queries.create_manager_user(email, password)
                serialized_user = serialize('json',
                                            ManagerUser.objects.filter(pk=manager_user.pk),
                                            fields=('email', 'date_joined'))
                user_fields = json.loads(serialized_user)[0]["fields"]

                return JsonResponse(user_fields, status=201)

            except queries.FirebaseError:

                return HttpResponse(status=503, reason="Internal Server Error: Firebase")

            except queries.ManagerExistsError:

                return HttpResponse(status=409, reason="Conflict: Email already associated with a manager")

        else:

            return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")

    except json.JSONDecodeError:

        return HttpResponse(status=400, reason="Bad Request: JSON object expected in POST body")


def create_promoter(request):
    try:
        json_data = json.loads(request.body)

        email = json_data["email"]
        password = json_data["password"]

        if email and password:

            try:

                promoter_user = queries.create_promoter_user(email, password)
                serialized_user = serialize('json',
                                            PromoterUser.objects.filter(pk=promoter_user.pk),
                                            fields=('email', 'date_joined'))
                user_fields = json.loads(serialized_user)[0]["fields"]

                return JsonResponse(user_fields, status=201)

            except queries.FirebaseError:

                return HttpResponse(status=503, reason="Internal Server Error: Firebase")

            except queries.PromoterExistsError:

                return HttpResponse(status=409, reason="Conflict: Email already associated with a promoter")

        else:

            return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")

    except json.JSONDecodeError:

        return HttpResponse(status=400, reason="Bad Request: JSON object expected in POST body")
