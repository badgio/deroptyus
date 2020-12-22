from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from badges import queries as badges_queries
from badges.models import RedeemedBadge
from rewards import queries as rewards_queries
from rewards.models import Reward, RedeemableReward
from users.models import PromoterUser, AppUser
from . import utils
from .models import Collection, CollectionBadge


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
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(collection.get("image"), str(collection_created.uuid))
        # Storing image
        collection_created.image = ContentFile(decoded_img, name=filename)

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
    # Updating provided fields
    if collection.get('name'):
        collection_update.name = collection.get('name')
    if collection.get('description'):
        collection_update.description = collection.get('description')
    # If changing both dates
    if collection.get('start_date') and not collection.get('end_date'):
        collection_update.start_date = collection.get('start_date')
    # If changing only start
    elif collection.get('start_date'):
        if collection_update.end_date > collection.get('start_date'):
            collection_update.start_date = collection.get('start_date')
        else:
            raise StartDateAfterEndDate()
    if collection.get('end_date'):
        if collection.get('end_date') > collection_update.start_date:  # End must be after the start
            collection_update.end_date = collection.get('end_date')
        else:
            raise EndDateNotAfterStartDate()
    if collection.get('status'):
        collection_update.status = collection.get('status')

    if collection.get("image"):
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(collection.get("image"), str(collection_update.uuid))
        # Deleting previous image from storage
        default_storage.delete(collection_update.image.path)
        # Storing image
        collection_update.image = ContentFile(decoded_img, name=filename)

    if collection.get('badges'):
        badge_uuids = []
        for badge_uuid in collection.get('badges'):
            try:
                badge_uuids.append(badges_queries.get_badge_by_uuid(badge_uuid))
            except Exception:
                raise NotEveryBadgeExists()

        # Removing no longer wanted badges
        for collection_badge in CollectionBadge.objects.filter(collection=collection_uuid):
            if collection_badge.badge.uuid not in badge_uuids:
                collection_badge.delete()

        # Associating the badges provided with the collection
        for badge_uuid in badge_uuids:
            badge = badges_queries.get_badge_by_uuid(badge_uuid)
            try:
                CollectionBadge.objects.get(collection=collection_update, badge=badge)
            except CollectionBadge.DoesNotExist:
                CollectionBadge(collection=collection_update, badge=badge).save()

    # Checking if the collection has a reward
    if collection.get("reward"):
        try:
            collection_update.reward = rewards_queries.get_reward_by_uuid(collection.get("reward"))
        except Reward.DoesNotExist:
            raise NotAValidReward()

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

    # Collection status
    collection_status = len(badges_in_collection_collected) / len(badges_in_collection)

    if collection_status != 1:
        return collection_status, None

    # Getting reward
    try:
        redeemable_reward = rewards_queries.get_redeemable_award_by_collection_user(collection_uuid, user_id)
    except RedeemableReward.DoesNotExist:
        redeemable_reward = None

    return collection_status, redeemable_reward


def redeem_collections_by_badge(badge, user_id):
    # Creating reward codes for every collection completed
    for collection_id in CollectionBadge.objects.filter(badge=badge).values_list('collection', flat=True):

        collection = Collection.objects.get(id=collection_id)
        collection_status, _ = get_collection_status(collection.uuid, user_id)

        if collection_status == 1:
            rewards_queries.award_reward_to_user(collection.uuid, user_id)


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
