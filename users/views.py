from django.http import HttpResponse
from django.core.serializers import serialize

from . import queries
from .models import AppUser

# Create your views here.

def appers (request):

    if request.method == 'POST':

        return create_app_user(request)

    else:

        return HttpResponse(status=405, reason=f"Method Not Allowed: {request.method} not supported")

def create_app_user (request):

    email = request.POST["email"]
    password = request.POST["password"]

    if email and password:

        try:

            app_user = queries.create_app_user(email, password)
            serialized_user = serialize('json',
                                        AppUser.objects.filter(pk=app_user.pk),
                                        fields=('email', 'date_joined'))

            return HttpResponse(serialized_user, status=201, content_type="text/json-comment-filtered")


        except queries.FirebaseError:

            return HttpResponse(status=503, reason="Internal Server Error: Firebase")

        except queries.AppUserExistsError:

            return HttpResponse(status=409, reason="Conflict: Email already associated with an app user")

    else:

        return HttpResponse(status=400, reason="Bad Request: Email and Password must be provided")