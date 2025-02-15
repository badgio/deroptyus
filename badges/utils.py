import json
from base64 import b64decode
from datetime import datetime
from mimetypes import guess_extension

from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from locations import queries as location_queries
from users import queries as user_queries
from .models import Status


def decode_image_from_base64(base64_image, filename):
    try:
        # Accepted format: data:<mime_type>;base64,<encoding>
        img_format, img_str = base64_image.split(';base64,')
        _, mime_type = img_format.split(':')

        # If MIME type is not image
        if mime_type.split("/")[0] != "image":
            raise NotAValidImage()

        # Decoding image from base64
        decoded_img = b64decode(img_str)
        # Getting extension from MIME type
        file_extension = guess_extension(mime_type)
        # Storing image
        return decoded_img, f'{filename}.{file_extension}'
    except Exception as e:
        raise NotAValidImage(e)


def encode_badge_to_json(badges):
    serialized_badges = json.loads(serializers.serialize("json",
                                                         badges,
                                                         fields=[
                                                             'uuid', 'name',
                                                             'description',
                                                             'start_date', 'end_date',
                                                             'location', 'promoter', 'status', 'image', ]))

    image_serialized_badges = []
    for serialized in serialized_badges:

        badge_fields = serialized["fields"]

        if badge_fields.get('location'):
            badge_fields['location'] = location_queries.get_str_by_pk(badge_fields.get('location'))

        if badge_fields.get('promoter'):
            badge_fields['promoter'] = user_queries.get_str_by_promoter_pk(badge_fields.get('promoter'))

        image_serialized_badges.append(badge_fields)

    return image_serialized_badges


def decode_badge_from_json(data, admin):
    try:
        json_data = json.loads(data)
        badge = {
            'name': json_data.get("name"),
            'description': json_data.get("description"),
            'location': json_data.get("location"),
            'status': json_data.get("status") if admin else Status.PENDING,  # Only admin can change status
        }

        # Setting start date
        if "start_date" in json_data:
            try:
                badge["start_date"] = datetime.fromisoformat(json_data.get("start_date"))
            except Exception:
                raise NotAValidStartDate()

        # Setting end date
        if "end_date" in json_data:
            try:
                badge["end_date"] = datetime.fromisoformat(json_data.get("end_date"))
            except Exception:
                raise NotAValidEndDate()

        if "image" in json_data:
            badge["image"] = json_data.get("image")

    except (json.JSONDecodeError, TypeError):
        raise InvalidJSONData()

    return badge


def paginator(request, f):
    page_size = request.GET.get('page_size')
    f = f.order_by('status')
    pager = Paginator(f, page_size) if page_size else Paginator(f, 50)

    page = request.GET.get('page')
    try:
        response = pager.page(page)
    except PageNotAnInteger:
        response = pager.page(1)
    except EmptyPage:
        response = pager.page(pager.num_pages)

    return response


class NotAValidStartDate(Exception):
    pass


class NotAValidEndDate(Exception):
    pass


class InvalidJSONData(Exception):
    pass


class NotAValidImage(Exception):
    pass
