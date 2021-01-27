import copy
from datetime import datetime, timedelta

from django.db.models import Q

from badges.models import RedeemedBadge
from rewards.models import RedeemedReward
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
    location_created.twitter = location.get('twitter')

    if location.get("image"):
        # Attempting to decode image from base64 to check if image is valid
        _, _ = utils.decode_image_from_base64(location.get("image"), str(location_created.uuid))
        # Storing base64 string in the DB
        location_created.image = location.get("image")

    location_created.manager = ManagerUser.objects.get(user_id=user_id)
    location_created.save()

    return location_created


def get_locations():
    return Location.objects.all()


def get_location_by_uuid(location_uuid):
    return Location.objects.get(uuid=location_uuid)


def get_location_by_id(location_id):
    return Location.objects.get(id=location_id)


def get_str_by_pk(pk):
    return str(Location.objects.get(pk=pk))


def delete_location_by_uuid(location_uuid):
    location = get_location_by_uuid(location_uuid)
    # Trying to delete location
    try:
        location.delete()
    except Exception:
        return False  # Couldn't delete
    return True


def patch_location_by_uuid(location_uuid, location):
    # Getting location to update
    location_update = get_location_by_uuid(location_uuid)
    # Updating non-nullable fields
    if location.get('name'):
        location_update.name = location.get('name')
    if location.get('description'):
        location_update.description = location.get('description')
    # Updating nullable fields
    if 'latitude' in location:
        location_update.latitude = location.get('latitude')
    if 'longitude' in location:
        location_update.longitude = location.get('longitude')
    if 'website' in location:
        location_update.website = location.get('website')
    if 'status' in location:
        location_update.status = location.get('status')
    if 'facebook' in location:
        location_update.facebook = location.get('facebook')
    if 'instagram' in location:
        location_update.instagram = location.get('instagram')
    if 'twitter' in location:
        location_update.twitter = location.get('twitter')
    if 'image' in location:
        # Checking if a null was provided
        if not location.get("image"):
            # Setting field to null
            location_update.image = None
        else:
            # Attempting to decode image from base64 to check if image is valid
            _, _ = utils.decode_image_from_base64(location.get("image"), str(location_update.uuid))
            # Storing base64 string in the DB
            location_update.image = location.get("image")

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

    location = get_location_by_uuid(location_uuid)
    location_name = location.name

    stats_week = get_location_weekly_report(location_uuid, map_stats_week)
    stats_chart_1 = get_location_main_chart(location_uuid, map_stats_chart_1)
    stats_chart_2 = get_location_secondary_chart(location_uuid, map_stats_chart_2)

    return [location_name, stats_week, stats_chart_1, stats_chart_2]


def get_location_weekly_report(location_uuid, map_stats):
    last_week_date = (datetime.now() - timedelta(days=7)).date()
    last_week_datetime = datetime.combine(last_week_date, datetime.max.time())
    redeemed_rewards = 0

    weekly_redeemed_rewards = RedeemedReward.objects.filter(Q(reward__location__uuid=location_uuid),
                                                            Q(time_awarded__gt=last_week_datetime)).order_by(
        'time_awarded')

    for redeemed_reward in weekly_redeemed_rewards:
        redeemed_rewards += 1

    weekly_redeemed_badges = RedeemedBadge.objects.filter(Q(badge__location__uuid=location_uuid),
                                                          Q(time_redeemed__gt=last_week_datetime)).order_by(
        'time_redeemed')

    for redeemed_badge in weekly_redeemed_badges:
        date = redeemed_badge.time_redeemed
        user = redeemed_badge.app_user

        weekday = date.strftime('%A')

        get_all_stats(user, weekday, map_stats)

    map_stats['Redeemed_rewards'] = redeemed_rewards
    weekly_stats = get_weekly_stats(map_stats)

    return weekly_stats


def get_location_main_chart(location_uuid, map_stats):
    redeemed_badges = RedeemedBadge.objects.filter(Q(badge__location__uuid=location_uuid)).order_by('time_redeemed')

    for redeemed_badge in redeemed_badges:
        date = redeemed_badge.time_redeemed
        user = redeemed_badge.app_user

        day = date.strftime('%Y-%m-%d')

        get_all_stats(user, day, map_stats)

    return map_stats


def get_location_secondary_chart(location_uuid, map_stats):
    redeemed_badges = RedeemedBadge.objects.filter(Q(badge__location__uuid=location_uuid)).order_by('time_redeemed')

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

    if user.gender:
        if user.gender not in map_stats:
            map_stats[user.gender] = {}
        if date not in map_stats[user.gender]:
            map_stats[user.gender][date] = 0
        map_stats[user.gender][date] += 1

    if user.country:
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

    if user.date_birth:
        datetime_birth = datetime.combine(user.date_birth, datetime.min.time())
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
    young = 'Young'
    adult = 'Adult'
    elder = 'Elder'
    general = 'General'
    busiest_day = None
    countries = 'Countries'
    other_gender = 'Other'
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
    number_other_gender = len(map_stats[other_gender]) if other_gender in map_stats else 0

    if number_male_gender > number_female_gender and number_male_gender > number_other_gender:
        most_common_gender = male_gender
    elif number_female_gender > number_male_gender and number_female_gender > number_other_gender:
        most_common_gender = female_gender
    elif number_other_gender != 0:
        most_common_gender = other_gender
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
    stats['Redeemed_rewards'] = map_stats['Redeemed_rewards']

    return stats
