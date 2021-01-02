import copy
from datetime import datetime, timedelta

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q

from badge_collections import queries as badge_collections_queries
from locations import queries as location_queries
from locations.models import Location
from users.models import PromoterUser, AppUser
from . import utils
from .models import Badge, RedeemedBadge
from .models import Status


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


def redeem_badges_by_location(location_id, user_id):
    location = location_queries.get_location_by_id(location_id)
    # Getting app user that's redeeming the badge
    apper = AppUser.objects.get(user_id=user_id)
    # Getting all badges that are associated with a location and are "up"
    redeemable_badges = Badge.objects.filter(Q(location=location),
                                             Q(start_date__lte=datetime.now()),
                                             Q(status=Status.APPROVED),
                                             Q(end_date__isnull=True) | Q(end_date__gte=datetime.now())).exclude(
        Q(id__in=RedeemedBadge.objects.filter(app_user=apper)
          .values_list('badge', flat=True)))

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

    # Updating non-nullable fields
    if badge.get('name'):
        badge_update.name = badge.get('name')
    if badge.get('description'):
        badge_update.description = badge.get('description')

    # Updating dates
    start_date = badge.get('start_date') if 'start_date' in badge else badge_update.start_date
    end_date = badge.get('end_date') if 'end_date' in badge else badge_update.end_date
    # Updating start_date
    if not end_date or start_date < end_date:
        badge_update.start_date = start_date
    elif start_date and start_date >= end_date:
        raise StartDateAfterEndDate()
    # Updating end_date
    if not end_date or not start_date or start_date < end_date:
        badge_update.end_date = end_date
    elif end_date and end_date <= start_date:
        raise EndDateNotAfterStartDate()

    if badge.get('status'):
        badge_update.status = badge.get('status')
    if badge.get('location'):
        try:
            badge_update.location = Location.objects.get(uuid=badge.get('location'))
        except Location.DoesNotExist:
            raise NotAValidLocation()

    if "image" in badge:
        # Checking if a null was provided
        if not badge.get("image"):
            # Deleting previous image from storage
            if badge_update.image:
                default_storage.delete(badge_update.image.path)
            # Setting field to null
            badge_update.image = None
        else:
            # Decoding image from base64
            decoded_img, filename = utils.decode_image_from_base64(badge.get("image"), str(badge_update.uuid))
            # Deleting previous image from storage
            if badge_update.image:
                default_storage.delete(badge_update.image.path)
            # Storing image
            badge_update.image = ContentFile(decoded_img, name=filename)

    badge_update.save()

    return badge_update


def get_badge_stats(badge_uuid):
    map_stats_chart_1 = {}
    map_stats_chart_2 = {}
    young = 'Young'
    adult = 'Adult'
    elder = 'Elder'
    general = 'General'
    countries = 'Countries'
    map_stats_chart_1[general] = {}
    map_stats_chart_1[young] = {}
    map_stats_chart_1[adult] = {}
    map_stats_chart_1[elder] = {}
    map_stats_chart_1[countries] = {}

    map_stats_week = copy.deepcopy(map_stats_chart_1)

    stats_week = get_badge_weekly_report(badge_uuid, map_stats_week)
    stats_chart_1 = get_badge_main_chart(badge_uuid, map_stats_chart_1)
    stats_chart_2 = get_badge_secondary_chart(badge_uuid, map_stats_chart_2)

    return [stats_week, stats_chart_1, stats_chart_2]


def get_badge_weekly_report(badge_uuid, map_stats):
    last_week_date = (datetime.now() - timedelta(days=7)).date()
    last_week_datetime = datetime.combine(last_week_date, datetime.max.time())

    weekly_redeemed_badges = RedeemedBadge.objects.filter(Q(badge__uuid=badge_uuid),
                                                          Q(time_redeemed__gt=last_week_datetime))

    for redeemed_badge in weekly_redeemed_badges:
        date = redeemed_badge.time_redeemed
        user = redeemed_badge.app_user

        weekday = date.strftime('%A')

        get_all_stats(user, weekday, map_stats)

    weekly_stats = get_weekly_stats(map_stats)

    return weekly_stats


def get_badge_main_chart(badge_uuid, map_stats):
    redeemed_badges = RedeemedBadge.objects.filter(Q(badge__uuid=badge_uuid))

    for redeemed_badge in redeemed_badges:
        date = redeemed_badge.time_redeemed
        user = redeemed_badge.app_user

        day = date.strftime('%Y-%m-%d')

        get_all_stats(user, day, map_stats)

    return map_stats


def get_badge_secondary_chart(badge_uuid, map_stats):
    redeemed_badges = RedeemedBadge.objects.filter(Q(badge__uuid=badge_uuid))

    for redeemed_badge in redeemed_badges:
        date = redeemed_badge.time_redeemed

        day = date.strftime('%Y-%m-%d')
        hour = date.strftime('%H')

        map_stats = get_secondary_chart_stats(day, hour, map_stats)

    return map_stats


def get_all_stats(user, date, map_stats):
    young = 'Young'
    adult = 'Adult'
    elder = 'Elder'
    general = 'General'
    countries = 'Countries'
    current_date = datetime.now()

    datetime_birth = datetime.combine(user.date_birth, datetime.min.time())

    if user.gender not in map_stats:
        map_stats[user.gender] = {}
    if date not in map_stats[user.gender]:
        map_stats[user.gender][date] = 0
    map_stats[user.gender][date] += 1

    if user.country not in map_stats:
        map_stats[user.country] = {}
        map_stats[countries][user.country] = 0
    if date not in map_stats[user.country]:
        map_stats[user.country][date] = 0
    map_stats[user.country][date] += 1
    map_stats[countries][user.country] += 1

    if date not in map_stats[general]:
        map_stats[general][date] = 0
    map_stats[general][date] += 1

    delta = current_date - datetime_birth
    delta_years = delta.days / 365.2425

    if delta_years < 18:
        if date not in map_stats[young]:
            map_stats[young][date] = 0
        map_stats[young][date] += 1
    elif delta_years < 65:
        if date not in map_stats[adult]:
            map_stats[adult][date] = 0
        map_stats[adult][date] += 1
    else:
        if date not in map_stats[elder]:
            map_stats[elder][date] = 0
        map_stats[elder][date] += 1


def get_secondary_chart_stats(date, hour, map_stats):
    total_hour_visitors = 'Total hour visitors'

    if hour not in map_stats:
        map_stats[hour] = {}
    if date not in map_stats[hour]:
        map_stats[hour][date] = 0
    if total_hour_visitors not in map_stats[hour]:
        map_stats[hour][total_hour_visitors] = 0
    map_stats[hour][date] += 1
    map_stats[hour][total_hour_visitors] += 1

    return map_stats


def get_weekly_stats(map_stats):
    total_visitors = 0
    redeemed_rewards = 0
    young = 'Young'
    adult = 'Adult'
    elder = 'Elder'
    general = 'General'
    busiest_day = None
    countries = 'Countries'
    female_gender = 'Female'
    male_gender = 'Male'
    most_common_country = None
    stats = {}

    for weekday in map_stats[general]:
        stats[weekday] = map_stats[general][weekday]
        total_visitors += map_stats[general][weekday]
        if not busiest_day or map_stats[general][weekday] > map_stats[general][busiest_day]:
            busiest_day = weekday

    for country in map_stats[countries]:
        if not most_common_country or map_stats[countries][country] > map_stats[countries][most_common_country]:
            most_common_country = country

    number_female_gender = len(map_stats[female_gender]) if female_gender in map_stats else 0
    number_male_gender = len(map_stats[male_gender]) if male_gender in map_stats else 0

    if number_male_gender > number_female_gender:
        most_common_gender = male_gender
    elif number_female_gender != 0:
        most_common_gender = female_gender
    else:
        most_common_gender = None

    young_visitors = len(map_stats[young])
    adult_visitors = len(map_stats[adult])
    elder_visitors = len(map_stats[elder])

    if young_visitors > adult_visitors and young_visitors > elder_visitors:
        most_common_age_range = young
    elif adult_visitors > young_visitors and adult_visitors > elder_visitors:
        most_common_age_range = adult
    elif elder_visitors != 0:
        most_common_age_range = elder
    else:
        most_common_age_range = None

    stats['Total_visitors'] = total_visitors
    stats['Busiest_day'] = busiest_day
    stats['Most_common_age_range'] = most_common_age_range
    stats['Most_common_country'] = most_common_country
    stats['Most_common_gender'] = most_common_gender
    stats['Redeemed_rewards'] = redeemed_rewards

    return stats


class NotAValidLocation(Exception):
    pass


class StartDateAfterEndDate(Exception):
    pass


class EndDateNotAfterStartDate(Exception):
    pass
