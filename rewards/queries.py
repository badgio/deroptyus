import random
from datetime import datetime, timedelta

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from badge_collections import queries as badge_collections_queries
from badge_collections import utils
from locations.models import Location
from users.models import PromoterUser, AppUser
from .models import Reward, RedeemableReward

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
        # Decoding image from base64
        decoded_img, filename = utils.decode_image_from_base64(reward.get("image"), str(reward_created.uuid))
        # Storing image
        reward_created.image = ContentFile(decoded_img, name=filename)

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
        # Deleting reward image
        if reward.image:
            default_storage.delete(reward.image.path)
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
            # Deleting previous image from storage
            if reward_update.image:
                default_storage.delete(reward_update.image.path)
            # Setting field to null
            reward_update.image = None
        else:
            # Decoding image from base64
            decoded_img, filename = utils.decode_image_from_base64(reward.get("image"), str(reward_update.uuid))
            # Deleting previous image from storage
            if reward_update.image:
                default_storage.delete(reward_update.image.path)
            # Storing image
            reward_update.image = ContentFile(decoded_img, name=filename)

    reward_update.save()

    return reward_update


def award_reward_to_user(collection_uuid, user_id):
    # Getting app user
    apper = AppUser.objects.get(user_id=user_id)

    # Getting the collection
    collection = badge_collections_queries.get_collection_by_uuid(collection_uuid)

    # Getting the reward that is associated with the collection
    reward_to_redeem = collection.reward
    if not reward_to_redeem:
        return

    # Generating a unique code
    generated_code = ''.join(random.sample(CODE_DIGITS, CODE_LENGTH))
    while True:
        try:
            RedeemableReward.objects.get(reward_code=generated_code)
            generated_code = ''.join(random.sample(CODE_DIGITS, CODE_LENGTH))
        except RedeemableReward.DoesNotExist:
            break

    # Associating reward with the App User that redeemed it
    RedeemableReward(reward_code=generated_code,
                     app_user=apper,
                     reward=reward_to_redeem).save()


def get_redeemable_award_by_collection_user(collection_uuid, user_id):
    # Getting the App User
    apper = AppUser.objects.get(user_id=user_id)

    # Getting the Reward associated with the Collection
    reward = badge_collections_queries.get_collection_by_uuid(collection_uuid).reward

    if not reward:
        return None

    return RedeemableReward.objects.get(app_user=apper, reward=reward)


def redeem_reward_by_code(redeem_reward_info):
    # Getting reward by the code
    try:
        redeemable_reward = RedeemableReward.objects.get(reward_code=redeem_reward_info.get('reward_code'))
    except RedeemableReward.DoesNotExist:
        raise NoRewardByThatCode()

    # Removing the reward as redeemable
    redeemable_reward.delete()

    # Checking if reward code is still valid
    end_date = redeemable_reward.time_awarded + timedelta(seconds=redeemable_reward.reward.time_redeem)
    if end_date <= datetime.now():  # No longer valid
        raise RewardNoLongerValid()

    return redeemable_reward.reward


class NoRewardByThatCode(Exception):
    pass


class NotAValidLocation(Exception):
    pass


class RewardNoLongerValid(Exception):
    pass
