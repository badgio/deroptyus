import copy
from datetime import datetime, timedelta

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q

from badges.models import RedeemedBadges
from users.models import ManagerUser
from . import utils
from .models import Location


def create_location(location, user_id):
    # Creating Location
    location_created = Location()

    location_created.name = location.get('name')
    location_created.description = location.get('description')
    location_created.latitude = location.get('latitude')
    location_created.longitude = location.get('longitude')
    location_created.website = location.get("website")
    location_created.status = location.get("status")
    location_created.facebook = location.get('facebook')
    location_created.instagram = location.get('instagram')

    if location.get("image"):
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(location.get("image"), str(location_created.uuid))
        # Storing image
        location_created.image = ContentFile(decoded_img, name=filename)

    location_created.manager = ManagerUser.objects.get(user_id=user_id)
    location_created.save()

    return location_created


def get_locations():
    return Location.objects.all()


def get_location_by_uuid(location_uuid):
    return Location.objects.get(uuid=location_uuid)


def get_location_by_id(location_id):
    return Location.objects.get(id=location_id)


def delete_location_by_uuid(location_uuid):
    location = get_location_by_uuid(location_uuid)
    # Deleting previous image from storage
    if location.image:
        default_storage.delete(location.image.path)
    return location.delete()


def patch_location_by_uuid(location_uuid, location):
    # Getting location to update
    location_update = get_location_by_uuid(location_uuid)
    # Updating provided fields
    if location.get('name'):
        location_update.name = location.get('name')
    if location.get('description'):
        location_update.description = location.get('description')
    if location.get('latitude'):
        location_update.latitude = location.get('latitude')
    if location.get('longitude'):
        location_update.longitude = location.get('longitude')
    if location.get('website'):
        location_update.website = location.get('website')
    if location.get('status'):
        location_update.status = location.get('status')
    if location.get('facebook'):
        location_update.facebook = location.get('facebook')
    if location.get('instagram'):
        location_update.instagram = location.get('instagram')
    if location.get("image"):
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(location.get("image"), str(location_update.uuid))
        # Deleting previous image from storage
        default_storage.delete(location_update.image.path)
        # Storing image
        location_update.image = ContentFile(decoded_img, name=filename)

    location_update.save()

    return location_update


def get_location_stats(location_uuid):
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

    stats_week = get_location_weekly_report(location_uuid, map_stats_week)
    stats_chart_1 = get_location_main_chart(location_uuid, map_stats_chart_1)
    stats_chart_2 = get_location_secondary_chart(location_uuid, map_stats_chart_2)

    return [stats_week, stats_chart_1, stats_chart_2]


def get_location_weekly_report(location_uuid, map_stats):
    last_week_date = (datetime.now() - timedelta(days=7)).date()
    last_week_datetime = datetime.combine(last_week_date, datetime.max.time())

    weekly_redeemed_badges = RedeemedBadges.objects.filter(Q(badge__location__uuid=location_uuid),
                                                           Q(time_redeemed__gt=last_week_datetime))

    for redeemed_badge in weekly_redeemed_badges:
        date = redeemed_badge.time_redeemed
        # date = redeemed_badge.time_redeemed.day()
        user = redeemed_badge.app_user

        day = date.strftime('%A')

        map_stats = get_all_stats(user, day, map_stats)

    weekly_stats = get_weekly_stats(map_stats)

    return weekly_stats


def get_location_main_chart(location_uuid, map_stats):
    redeemed_badges = RedeemedBadges.objects.filter(Q(badge__location__uuid=location_uuid))

    for redeemed_badge in redeemed_badges:
        date = redeemed_badge.time_redeemed
        # date = redeemed_badge.time_redeemed.day()
        user = redeemed_badge.app_user

        day = date.strftime('%Y-%m-%d')

        main_chart_stats = get_all_stats(user, day, map_stats)

    return main_chart_stats


def get_location_secondary_chart(location_uuid, map_stats):
    redeemed_badges = RedeemedBadges.objects.filter(Q(badge__location__uuid=location_uuid))

    for redeemed_badge in redeemed_badges:
        date = redeemed_badge.time_redeemed
        # date = redeemed_badge.time_redeemed.day()
        user = redeemed_badge.app_user

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

    return map_stats


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
    young_visitors = 0
    adult_visitors = 0
    elder_visitors = 0
    most_common_gender = ''
    young = 'Young'
    adult = 'Adult'
    elder = 'Elder'
    general = 'General'
    busiest_day = 'Tuesday'
    countries = 'Countries'
    female_gender = 'Female'
    male_gender = 'Male'
    most_common_country = 'Portugal'
    stats = {}

    for x in map_stats[general]:
        stats[x] = map_stats[general][x]
        total_visitors += map_stats[general][x]
        if busiest_day not in map_stats[general]:
            busiest_day = x
        elif map_stats[general][x] > map_stats[general][busiest_day]:
            busiest_day = x

    for x in map_stats[countries]:
        if most_common_country not in map_stats[countries]:
            most_common_country = x
        elif map_stats[countries][x] > map_stats[countries][most_common_country]:
            most_common_country = x

    number_female_gender=len(map_stats[female_gender])
    number_male_gender = len(map_stats[male_gender])
    if number_male_gender > number_female_gender:
        most_common_gender=male_gender
    else: most_common_gender=female_gender

    young_visitors = len(map_stats[young])
    adult_visitors = len(map_stats[adult])
    elder_visitors = len(map_stats[elder])

    if young_visitors > adult_visitors and young_visitors > elder_visitors:
        most_common_age_range = young
    elif adult_visitors > young_visitors and adult_visitors > elder_visitors:
        most_common_age_range = adult
    else:
        most_common_age_range = elder

    stats['Total_visitors'] = total_visitors
    stats['Busiest_day'] = busiest_day
    stats['Most_common_age_range'] = most_common_age_range
    stats['Most_common_country'] = most_common_country
    stats['Most_common_gender'] = most_common_gender
    stats['Redeemed_rewards'] = redeemed_rewards

    return stats
