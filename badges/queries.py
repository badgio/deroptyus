from datetime import datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q

from badge_collections import queries as badge_collections_queries
from locations.models import Location
from users.models import PromoterUser, AppUser
from . import utils
from .models import Badge, RedeemedBadge


def create_badge(badge, user_id):
    # Creating badge
    badge_created = Badge()

    badge_created.name = badge.get('name')
    badge_created.description = badge.get('description')

    if "start_date" in badge:
        badge_created.start_date = badge.get('start_date')

    if "end_date" in badge:
        if badge.get('end_date') > badge_created.start_date:  # End must be after the start
            badge_created.end_date = badge.get('end_date')
        else:
            raise EndDateNotAfterStartDate()

    badge_created.status = badge.get("status")

    if badge.get("image"):
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(badge.get("image"), str(badge_created.uuid))
        # Storing image
        badge_created.image = ContentFile(decoded_img, name=filename)

    try:
        badge_created.location = Location.objects.get(uuid=badge.get('location'))
    except Location.DoesNotExist:
        raise NotAValidLocation()

    badge_created.promoter = PromoterUser.objects.get(user_id=user_id)
    badge_created.save()

    return badge_created


def get_badges():
    return Badge.objects.all()


def get_badge_by_uuid(badge_uuid):
    return Badge.objects.get(uuid=badge_uuid)


def get_str_by_pk(pk):
    return str(Badge.objects.get(pk=pk))


def delete_badge_by_uuid(badge_uuid):
    badge = get_badge_by_uuid(badge_uuid)
    # Trying to delete badge
    try:
        badge.delete()
        # Deleting badge image
        if badge.image:
            default_storage.delete(badge.image.path)
    except Exception:
        return False  # Couldn't delete
    return True


def patch_badge_by_uuid(badge_uuid, badge):
    # Getting badge to update
    badge_update = get_badge_by_uuid(badge_uuid)
    # Updating provided fields
    if badge.get('name'):
        badge_update.name = badge.get('name')
    if badge.get('description'):
        badge_update.description = badge.get('description')
    # If changing both dates
    if badge.get('start_date') and not badge.get('end_date'):
        badge_update.start_date = badge.get('start_date')
    # If changing only start
    elif badge.get('start_date'):
        if badge_update.end_date > badge.get('start_date'):
            badge_update.start_date = badge.get('start_date')
        else:
            raise StartDateAfterEndDate()
    if badge.get('end_date'):
        if badge.get('end_date') > badge_update.start_date:  # End must be after the start
            badge_update.end_date = badge.get('end_date')
        else:
            raise EndDateNotAfterStartDate()
    if badge.get('status'):
        badge_update.status = badge.get('status')
    if badge.get('location'):
        try:
            badge_update.location = Location.objects.get(uuid=badge.get('location'))
        except Location.DoesNotExist:
            raise NotAValidLocation()

    if badge.get("image"):
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(badge.get("image"), str(badge_update.uuid))
        # Deleting previous image from storage
        default_storage.delete(badge_update.image.path)
        # Storing image
        badge_update.image = ContentFile(decoded_img, name=filename)

    badge_update.save()

    return badge_update


def redeem_badges_by_location(location_uuid, user_id):
    # Getting all badges that are associated with a location and are "up"
    redeemable_badges = Badge.objects.filter(Q(location=location_uuid),
                                             Q(start_date__lte=datetime.now()),
                                             Q(end_date__isnull=True) | Q(end_date__gte=datetime.now()))

    # Getting app user that's redeeming the badge
    apper = AppUser.objects.get(user_id=user_id)

    badges_redeemed = []
    # Linking the App User with the Badges
    for redeemable_badge in redeemable_badges:
        try:  # Checking if the user has already redeemed this badge (and if so do nothing)
            RedeemedBadge.objects.get(app_user=apper, badge=redeemable_badge)
        except RedeemedBadge.DoesNotExist:
            # Redeeming Badge
            redeemed_badge = RedeemedBadge(app_user=apper, badge=redeemable_badge)
            redeemed_badge.save()
            badges_redeemed.append(redeemed_badge.badge)

    # Checking for collection completion
    for badge in badges_redeemed:
        badge_collections_queries.redeem_collections_by_badge(badge, user_id)

    return redeemable_badges


class NotAValidLocation(Exception):
    pass


class StartDateAfterEndDate(Exception):
    pass


class EndDateNotAfterStartDate(Exception):
    pass
