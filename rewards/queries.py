import copy
import random
from datetime import datetime, timedelta

from django.db.models import Q

from badge_collections import queries as badge_collections_queries
from locations.models import Location
from users.models import PromoterUser, AppUser
from . import utils
from .models import Reward, RedeemedReward, Status

CODE_LENGTH = 6
CODE_DIGITS = '0123456789ABCDEF'


def create_reward(reward, user_id):
    # Creating reward
    reward_created = Reward()

    reward_created.name = reward.get('name')
    reward_created.description = reward.get('description')

    if "time_redeem" in reward:
        reward_created.time_redeem = reward.get('time_redeem')

    reward_created.status = reward.get("status")

    try:
        reward_created.location = Location.objects.get(uuid=reward.get('location'))
    except Location.DoesNotExist:
        raise NotAValidLocation()

    if reward.get("image"):
        # Attempting to decode image from base64 to check if image is valid
        _, _ = utils.decode_image_from_base64(reward.get("image"), str(reward_created.uuid))
        # Storing base64 string in the DB
        reward_created.image = reward.get("image")

    reward_created.promoter = PromoterUser.objects.get(user_id=user_id)
    reward_created.save()

    return reward_created


def get_rewards():
    return Reward.objects.all()


def get_reward_by_uuid(reward_uuid):
    return Reward.objects.get(uuid=reward_uuid)


def get_reward_by_pk(reward_id):
    return Reward.objects.get(id=reward_id)


def get_str_by_pk(pk):
    return str(Reward.objects.get(pk=pk))


def delete_reward_by_uuid(reward_uuid):
    reward = get_reward_by_uuid(reward_uuid)
    # Trying to delete reward
    try:
        reward.delete()
    except Exception:
        return False  # Couldn't delete
    return True


def patch_reward_by_uuid(reward_uuid, reward):
    # Getting reward to update
    reward_update = get_reward_by_uuid(reward_uuid)
    # Updating provided fields
    if reward.get('name'):
        reward_update.name = reward.get('name')
    if reward.get('description'):
        reward_update.description = reward.get('description')
    if reward.get('status'):
        reward_update.status = reward.get('status')
    if reward.get('location'):
        try:
            reward_update.location = Location.objects.get(uuid=reward.get('location'))
        except Location.DoesNotExist:
            raise NotAValidLocation()
    if "image" in reward:
        # Checking if a null was provided
        if not reward.get("image"):
            # Setting field to null
            reward_update.image = None
        else:
            # Attempting to decode image from base64 to check if image is valid
            _, _ = utils.decode_image_from_base64(reward.get("image"), str(reward_update.uuid))
            # Storing base64 string in the DB
            reward_update.image = reward.get("image")

    reward_update.save()

    return reward_update


def award_reward_to_user(collection_uuid, user_id):
    # Getting app user
    apper = AppUser.objects.get(user_id=user_id)

    # Getting the collection
    collection = badge_collections_queries.get_collection_by_uuid(collection_uuid)

    # Getting the reward that is associated with the collection
    reward_to_redeem = collection.reward
    if not reward_to_redeem or reward_to_redeem.status != Status.APPROVED:
        return

    # Generating a unique code
    generated_code = ''.join(random.sample(CODE_DIGITS, CODE_LENGTH))
    while True:
        try:
            RedeemedReward.objects.get(reward_code=generated_code)
            generated_code = ''.join(random.sample(CODE_DIGITS, CODE_LENGTH))
        except RedeemedReward.DoesNotExist:
            break

    # Associating reward with the App User that redeemed it
    RedeemedReward(reward_code=generated_code,
                   app_user=apper,
                   reward=reward_to_redeem).save()


def get_redeemable_award_by_collection_user(collection_uuid, user_id):
    # Getting the App User
    apper = AppUser.objects.get(user_id=user_id)

    # Getting the Reward associated with the Collection
    reward = badge_collections_queries.get_collection_by_uuid(collection_uuid).reward

    if not reward:
        return None

    return RedeemedReward.objects.get(app_user=apper, reward=reward)


def get_reward_by_code(redeem_reward_info):
    # Getting reward by the code
    try:
        redeemed_reward = RedeemedReward.objects.get(reward_code=redeem_reward_info.get('reward_code'))
    except RedeemedReward.DoesNotExist:
        raise NoRewardByThatCode()

    return redeemed_reward.reward


def redeem_reward_by_code(redeem_reward_info):
    # Getting reward by the code
    try:
        redeemed_reward = RedeemedReward.objects.get(reward_code=redeem_reward_info.get('reward_code'))
    except RedeemedReward.DoesNotExist:
        raise NoRewardByThatCode()

    if redeemed_reward.redeemed:
        raise RewardAlreadyRedeemed()

    # Checking if reward code is still valid
    if redeemed_reward.reward.time_redeem:
        end_date = redeemed_reward.time_awarded + timedelta(seconds=redeemed_reward.reward.time_redeem)
        if end_date <= datetime.now():  # No longer valid
            raise RewardNoLongerValid()

    # Removing the reward as redeemable
    redeemed_reward.redeemed = True
    redeemed_reward.save()


def get_reward_stats(reward_uuid):
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

    reward = get_reward_by_uuid(reward_uuid)
    reward_name = reward.name

    stats_week = get_reward_weekly_report(reward_uuid, map_stats_week)
    stats_chart_1 = get_reward_main_chart(reward_uuid, map_stats_chart_1)
    stats_chart_2 = get_reward_secondary_chart(reward_uuid, map_stats_chart_2)

    return [reward_name, stats_week, stats_chart_1, stats_chart_2]


def get_reward_weekly_report(reward_uuid, map_stats):
    last_week_date = (datetime.now() - timedelta(days=7)).date()
    last_week_datetime = datetime.combine(last_week_date, datetime.max.time())

    weekly_redeemed_rewards = RedeemedReward.objects.filter(Q(reward__uuid=reward_uuid),
                                                            Q(redeemed=True),
                                                            Q(time_awarded__gt=last_week_datetime))

    for redeemed_reward in weekly_redeemed_rewards:
        date = redeemed_reward.time_awarded
        user = redeemed_reward.app_user

        weekday = date.strftime('%A')

        get_all_stats(user, weekday, map_stats)

    weekly_stats = get_weekly_stats(map_stats)

    return weekly_stats


def get_reward_main_chart(reward_uuid, map_stats):
    redeemed_rewards = RedeemedReward.objects.filter(Q(redeemed=True),
                                                     Q(reward__uuid=reward_uuid))

    for redeemed_reward in redeemed_rewards:
        date = redeemed_reward.time_awarded
        user = redeemed_reward.app_user

        day = date.strftime('%Y-%m-%d')

        get_all_stats(user, day, map_stats)

    return map_stats


def get_reward_secondary_chart(reward_uuid, map_stats):
    redeemed_rewards = RedeemedReward.objects.filter(Q(redeemed=True),
                                                     Q(reward__uuid=reward_uuid))

    for redeemed_reward in redeemed_rewards:
        date = redeemed_reward.time_awarded

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
    redeemed_rewards = 0
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
        redeemed_rewards += map_stats[general][weekday]
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
    stats['Redeemed_rewards'] = redeemed_rewards

    return stats


class NoRewardByThatCode(Exception):
    pass


class RewardAlreadyRedeemed(Exception):
    pass


class NotAValidLocation(Exception):
    pass


class RewardNoLongerValid(Exception):
    pass
