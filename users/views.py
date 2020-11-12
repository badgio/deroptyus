import json
from datetime import date

from django.core.serializers import serialize
from django.http import HttpResponse

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
    email = request.POST["email"]
    password = request.POST["password"]
    name = request.POST["name"]
    date_birth = date.fromisoformat(request.POST["date_birth"])
    country = request.POST["country"]
    city = request.POST["city"]
    gender = request.POST["gender"]

    if email and password and name and date_birth and country and city and gender:

        try:

            app_user = queries.create_app_user(email, password, name, date_birth, country, city, gender)
            serialized_user = serialize('json',
                                        AppUser.objects.filter(pk=app_user.pk),
                                        fields=(
                                            'email', 'name', 'date_birth', 'country', 'city', 'gender', 'date_joined'))
            user_fields = json.loads(serialized_user)[0]["fields"]

            return HttpResponse([user_fields], status=201, content_type="application/json")

        except queries.FirebaseError:

            return HttpResponse(status=503, reason="Internal Server Error: Firebase")

        except queries.AppUserExistsError:

            return HttpResponse(status=409, reason="Conflict: Email already associated with an app user")

    else:

        return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")


def create_manager(request):
    email = request.POST["email"]
    password = request.POST["password"]

    if email and password:

        try:

            manager_user = queries.create_manager_user(email, password)
            serialized_user = serialize('json',
                                        ManagerUser.objects.filter(pk=manager_user.pk),
                                        fields=('email', 'date_joined'))
            user_fields = json.loads(serialized_user)[0]["fields"]

            return HttpResponse([user_fields], status=201, content_type="application/json")

        except queries.FirebaseError:

            return HttpResponse(status=503, reason="Internal Server Error: Firebase")

        except queries.ManagerExistsError:

            return HttpResponse(status=409, reason="Conflict: Email already associated with a manager")

    else:

        return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")


def create_promoter(request):
    email = request.POST["email"]
    password = request.POST["password"]

    if email and password:

        try:

            promoter_user = queries.create_promoter_user(email, password)
            serialized_user = serialize('json',
                                        PromoterUser.objects.filter(pk=promoter_user.pk),
                                        fields=('email', 'date_joined'))
            user_fields = json.loads(serialized_user)[0]["fields"]

            return HttpResponse([user_fields], status=201, content_type="application/json")

        except queries.FirebaseError:

            return HttpResponse(status=503, reason="Internal Server Error: Firebase")

        except queries.PromoterExistsError:

            return HttpResponse(status=409, reason="Conflict: Email already associated with a promoter")

    else:

        return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")
