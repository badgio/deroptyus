import copy
from datetime import datetime, timedelta

from django.core.files.storage import default_storage
from django.db.models import Q

from badges import queries as badges_queries
from badges.models import RedeemedBadge, Badge
from badges.models import Status as BadgeStatus
from rewards import queries as rewards_queries
from rewards.models import Reward, RedeemedReward
from rewards.models import Status as RewardStatus
from users.models import PromoterUser, AppUser
from . import utils
from .models import Collection, CollectionBadge, Status


def create_collection(collection, user_id):
    # Creating collection
    collection_created = Collection()

    collection_created.name = collection.get('name')
    collection_created.description = collection.get('description')

    if "start_date" in collection:
        collection_created.start_date = collection.get('start_date')

    if "end_date" in collection:
        if collection.get('end_date') > collection_created.start_date:  # End must be after the start
            collection_created.end_date = collection.get('end_date')
        else:
            raise EndDateNotAfterStartDate()

    collection_created.status = collection.get("status")

    if collection.get("image"):
        # Attempting to decode image from base64 to check if image is valid
        _, _ = utils.decode_image_from_base64(collection.get("image"), str(collection_created.uuid))
        # Storing base64 string in the DB
        collection_created.image = collection.get("image")

    # Checking if every badge provided exists
    badges = []
    for badge_uuid in collection.get('badges'):
        try:
            badges.append(badges_queries.get_badge_by_uuid(badge_uuid))
        except Exception:
            raise NotEveryBadgeExists()

    # Checking if the collection has a reward
    if collection.get("reward"):
        try:
            collection_created.reward = rewards_queries.get_reward_by_uuid(collection.get("reward"))
        except Reward.DoesNotExist:
            raise NotAValidReward()

    collection_created.promoter = PromoterUser.objects.get(user_id=user_id)
    collection_created.save()

    # Associating the badges provided with the successfully created collection
    for badge in badges:
        CollectionBadge(collection=collection_created, badge=badge).save()

    return collection_created


def get_collections():
    return Collection.objects.all()


def get_collection_by_uuid(collection_uuid):
    return Collection.objects.get(uuid=collection_uuid)


def get_collection_badges_uuids_by_collection_uuid(collection_uuid):
    collection = get_collection_by_uuid(collection_uuid)
    return [collection_badge.badge.uuid for collection_badge in CollectionBadge.objects.filter(collection=collection)]


def get_str_by_pk(pk):
    return str(Collection.objects.get(pk=pk))


def delete_collection_by_uuid(collection_uuid):
    collection = get_collection_by_uuid(collection_uuid)
    # Trying to delete collection
    try:
        collection.delete()
        # Deleting collection image
        if collection.image:
            default_storage.delete(collection.image.path)
    except Exception:
        return False  # Couldn't delete
    return True


def patch_collection_by_uuid(collection_uuid, collection):
    # Getting collection to update
    collection_update = get_collection_by_uuid(collection_uuid)

    # Updating non-nullable fields
    if collection.get('name'):
        collection_update.name = collection.get('name')
    if collection.get('description'):
        collection_update.description = collection.get('description')

    # Updating dates
    start_date = collection.get('start_date') if 'start_date' in collection else collection_update.start_date
    end_date = collection.get('end_date') if 'end_date' in collection else collection_update.end_date
    # Updating start_date
    if not end_date or start_date < end_date:
        collection_update.start_date = start_date
    elif start_date and start_date >= end_date:
        raise StartDateAfterEndDate()
    # Updating end_date
    if not end_date or not start_date or start_date < end_date:
        collection_update.end_date = end_date
    elif end_date and end_date <= start_date:
        raise EndDateNotAfterStartDate()

    if "image" in collection:
        # Checking if a null was provided
        if not collection.get("image"):
            # Setting field to null
            collection_update.image = None
        else:
            # Attempting to decode image from base64 to check if image is valid
            _, _ = utils.decode_image_from_base64(collection.get("image"), str(collection_update.uuid))
            # Storing base64 string in the DB
            collection_update.image = collection.get("image")

    if 'badges' in collection:
        badge_uuids = []
        if collection.get('badges'):
            for badge_uuid in collection.get('badges'):
                try:
                    # Getting Badge
                    badge = badges_queries.get_badge_by_uuid(badge_uuid)
                    # If the Collection is approved, then all badges submitted must be approved
                    if collection_update.status == Status.APPROVED and badge.status != BadgeStatus.APPROVED:
                        raise BadgesMustBeApproved()
                    badge_uuids.append(badge_uuid)
                except Badge.objects.DoesNotExists:
                    raise NotEveryBadgeExists()

        # Removing no longer wanted badges
        for collection_badge in CollectionBadge.objects.filter(collection__uuid=collection_uuid):
            if collection_badge.badge.uuid not in badge_uuids:
                collection_badge.delete()

        # Associating the badges provided with the collection
        for badge_uuid in badge_uuids:
            badge = badges_queries.get_badge_by_uuid(badge_uuid)
            try:
                CollectionBadge.objects.get(collection=collection_update, badge=badge)
            except CollectionBadge.DoesNotExist:
                CollectionBadge(collection=collection_update, badge=badge).save()

    # Checking if the reward field was sent
    if "reward" in collection:
        # Deleting previous entry
        collection_update.reward = None
        if collection.get("reward"):
            try:
                reward = rewards_queries.get_reward_by_uuid(collection.get("reward"))
                if collection_update.status == Status.APPROVED and reward.status != RewardStatus.APPROVED:
                    raise RewardMustBeApproved()
                collection_update.reward = reward
            except Reward.DoesNotExist:
                raise NotAValidReward()

    if collection.get('status'):
        # If an admin approves a collection, every badge must be approved beforehand
        if collection.get('status') == Status.APPROVED and \
                any([col_badge.badge.status != BadgeStatus.APPROVED
                     for col_badge in CollectionBadge.objects.filter(collection=collection_update)]):
            raise BadgesMustBeApproved()
        # If an admin approves a collection with a reward associated, the reward must also be approved
        if collection.get('status') == Status.APPROVED and \
                collection_update.reward is not None and collection_update.reward.status != RewardStatus.APPROVED:
            raise RewardMustBeApproved()

        collection_update.status = collection.get('status')

    collection_update.save()

    return collection_update


def get_collection_status(collection_uuid, user_id):
    # Getting app user that's redeeming the badge
    apper = AppUser.objects.get(user_id=user_id)

    # Getting collection with UUID
    collection = get_collection_by_uuid(collection_uuid)

    # Getting every badge in the collection
    badges_in_collection = CollectionBadge.objects.filter(collection=collection).values_list('badge', flat=True)

    # Counting the number of badges in  in the collection
    badges_in_collection_collected = RedeemedBadge.objects.filter(badge__in=badges_in_collection, app_user=apper)

    # Get UUID of collected badges
    collected_badges_uuid = [collected_badge.badge.uuid for collected_badge in badges_in_collection_collected]
    
    # Collection status
    if len(badges_in_collection):
        collection_status = len(badges_in_collection_collected) / len(badges_in_collection)
    else:
        collection_status = 0

    if collection_status != 1:
        return collected_badges_uuid, collection_status, None

    # Getting reward
    try:
        redeemable_reward = rewards_queries.get_redeemable_award_by_collection_user(collection_uuid, user_id)
    except RedeemedReward.DoesNotExist:
        redeemable_reward = None

    return collected_badges_uuid, collection_status, redeemable_reward


def redeem_collections_by_badge(badge, user_id):
    # Creating reward codes for every collection completed
    for collection_id in CollectionBadge.objects.filter(badge=badge).values_list('collection', flat=True):

        collection = Collection.objects.get(id=collection_id)
        collection_status, _ = get_collection_status(collection.uuid, user_id)

        if collection_status == 1:
            rewards_queries.award_reward_to_user(collection.uuid, user_id)


def get_collection_stats(collection_uuid):
    map_stats_chart_1 = {}
    map_stats_chart_2 = {}
    map_stats_table = {}
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
    badge_uuids = []

    map_stats_week = copy.deepcopy(map_stats_chart_1)

    for collection_badge in CollectionBadge.objects.filter(collection__uuid=collection_uuid):
        badge_uuids.append(collection_badge.badge.uuid)

    stats_week = get_collection_weekly_report(collection_uuid, badge_uuids, map_stats_week)
    stats_chart_1 = get_collection_main_chart(badge_uuids, map_stats_chart_1)
    stats_chart_2 = get_collection_secondary_chart(badge_uuids, map_stats_chart_2)
    stats_table = get_collection_table_data(badge_uuids, map_stats_table)

    return [stats_week, stats_chart_1, stats_chart_2, stats_table]


def get_collection_weekly_report(collection_uuid, badge_uuids, map_stats):
    last_week_date = (datetime.now() - timedelta(days=7)).date()
    last_week_datetime = datetime.combine(last_week_date, datetime.max.time())

    redeemed_rewards = 0

    weekly_redeemed_rewards = RedeemedReward.objects.filter(Q(reward__collection__uuid=collection_uuid),
                                                            Q(time_awarded__gt=last_week_datetime))

    for redeemed_reward in weekly_redeemed_rewards:
        redeemed_rewards += 1

    for badge_uuid in badge_uuids:
        weekly_redeemed_badges = RedeemedBadge.objects.filter(Q(badge__uuid=badge_uuid),
                                                              Q(time_redeemed__gt=last_week_datetime))
        for redeemed_badge in weekly_redeemed_badges:
            date = redeemed_badge.time_redeemed
            user = redeemed_badge.app_user
            weekday = date.strftime('%A')
            get_all_stats(user, weekday, map_stats)

    map_stats['Redeemed_rewards'] = redeemed_rewards
    weekly_stats = get_weekly_stats(map_stats)

    return weekly_stats


def get_collection_main_chart(badge_uuids, map_stats):
    for badge_uuid in badge_uuids:
        redeemed_badges = RedeemedBadge.objects.filter(Q(badge__uuid=badge_uuid))
        for redeemed_badge in redeemed_badges:
            date = redeemed_badge.time_redeemed
            user = redeemed_badge.app_user

            day = date.strftime('%Y-%m-%d')

            get_all_stats(user, day, map_stats)

    return map_stats


def get_collection_table_data(badge_uuids, map_stats):
    for badge_uuid in badge_uuids:
        redeemed_badges = RedeemedBadge.objects.filter(Q(badge__uuid=badge_uuid))
        for redeemed_badge in redeemed_badges:
            badge = redeemed_badge.badge
            location = badge.location.name
            if location not in map_stats:
                map_stats[location] = 1
            else:
                map_stats[location] += 1

    # sorted_locations=sorted(map_stats.items(), key=lambda x: x[1], reverse=True)
    dict(sorted(map_stats.items(), key=lambda item: item[1]))

    return map_stats


def get_collection_secondary_chart(badge_uuids, map_stats):
    for badge_uuid in badge_uuids:
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
    stats['Redeemed_rewards'] = map_stats['Redeemed_rewards']

    return stats


class NotEveryBadgeExists(Exception):
    pass


class NotAValidLocation(Exception):
    pass


class NotAValidReward(Exception):
    pass


class StartDateAfterEndDate(Exception):
    pass


class EndDateNotAfterStartDate(Exception):
    pass


class BadgesMustBeApproved(Exception):
    pass


class RewardMustBeApproved(Exception):
    pass
