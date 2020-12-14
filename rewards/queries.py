import random
from datetime import datetime, timedelta

from locations.models import Location
from users.models import PromoterUser, AppUser
from .models import Reward, RedeemableReward

CODE_LENGTH = 6
CODE_DIGITS = '0123456789ABCDEF'


def create_reward(reward, user_id):
    # Creating reward
    reward_created = Reward()

    reward_created.description = reward.get('description')

    if "time_redeem" in reward:
        reward_created.time_redeem = reward.get('time_redeem')

    reward_created.status = reward.get("status")

    try:
        reward_created.location = Location.objects.get(uuid=reward.get('location'))
    except Location.DoesNotExist:
        raise NotAValidLocation()

    reward_created.promoter = PromoterUser.objects.get(user_id=user_id)
    reward_created.save()

    return reward_created


def get_rewards():
    return Reward.objects.all()


def get_reward_by_uuid(reward_uuid):
    return Reward.objects.get(uuid=reward_uuid)


def get_str_by_pk(pk):
    return str(Reward.objects.get(pk=pk))


def delete_reward_by_uuid(reward_uuid):
    return get_reward_by_uuid(reward_uuid).delete()


def patch_reward_by_uuid(reward_uuid, reward):
    # Getting reward to update
    reward_update = get_reward_by_uuid(reward_uuid)
    # Updating provided fields
    if reward.get('description'):
        reward_update.description = reward.get('description')
    if reward.get('status'):
        reward_update.status = reward.get('status')
    if reward.get('location'):
        try:
            reward_update.location = Location.objects.get(uuid=reward.get('location'))
        except Location.DoesNotExist:
            raise NotAValidLocation()

    reward_update.save()

    return reward_update


def award_reward_to_user(collection_uuid, user_id):
    # Getting app user that
    apper = AppUser.objects.get(user_id=user_id)

    # Getting the reward that is associated with the collection
    # redeemable_reward = Collection.objects.get(uuid=collection_uuid).reward
    redeemable_reward = Reward.objects.first()  # PLACEHOLDER !!! Should use the above when Collection is implemented

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
                     reward=redeemable_reward).save()


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
