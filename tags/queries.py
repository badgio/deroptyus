from locations.models import Location
from locations.queries import get_location_by_uuid
from users.models import AdminUser
from .models import Tag, RedeemedCounter


def create_tag(tag, user_id):
    # Creating tag
    tag_created = Tag()

    tag_created.uid = tag.get('uid')
    tag_created.app_key = tag.get('app_key')
    tag_created.location = get_location_by_uuid(tag.get('location'))
    tag_created.admin = AdminUser.objects.get(user_id=user_id)
    tag_created.save()

    return tag_created


def get_tags():
    return Tag.objects.all()


def get_tag_by_uid(tag_uid):
    return Tag.objects.get(uid=tag_uid)


def get_str_by_pk(pk):
    return str(Tag.objects.get(pk=pk))


def delete_tag_by_uid(tag_uid):
    return get_tag_by_uid(tag_uid).delete()


def patch_tag_by_uid(tag_uid, tag):
    # Getting tag to update
    tag_update = get_tag_by_uid(tag_uid)
    # Updating provided fields
    if tag.get('app_key'):
        tag_update.app_key = tag.get('app_key')
    if 'location' in tag:
        if not tag.get('location'):
            tag_update.location = None
        else:
            try:
                tag_update.location = get_location_by_uuid('location')
            except Location.DoesNotExist:
                raise NotAValidLocation()

    tag_update.save()

    return tag_update


def redeem_tag(redeem_info):
    required_fields = ['uid', 'counter', 'cmac']
    if any([field not in redeem_info for field in required_fields]):
        raise MissingRedeemInfo(f"Missing: {[field for field in required_fields not in redeem_info]}")

    # TO BE COMPLETED -> CHECKING IF TAG IS VALID THROUGH CMAC
    try:
        tag = Tag.objects.get(uid=redeem_info.get('uid'))
    except Tag.DoesNotExist:
        raise NotAValidTagUID()

    # Updating last_counter if it's the next in line
    if redeem_info.get('counter') == tag.last_counter + 1:
        # Updating last counter
        tag.last_counter = redeem_info.get('counter')
        tag.save()
        # Further updating the last counter with redeemed tags that came out of order
        for redeemed in RedeemedCounter.objects.filter(tag_id=tag.id).order_by('counter'):
            if redeemed.counter == tag.last_counter + 1:
                tag.last_counter = redeemed.counter
                tag.save()
                redeemed.delete()
            else:
                break
    # If the counter is superior to the last stored counter and has not been redeemed yet, we store it
    elif redeem_info.get('counter') > tag.last_counter:
        redeemed, created = RedeemedCounter.objects.get_or_create(tag=tag, counter=redeem_info.get('counter'))
        if created:
            redeemed.save()
        else:
            raise AlreadyRedeemedTag()
    # If the counter is lower than the last_counter, then it has already been redeemed
    else:
        raise AlreadyRedeemedTag()

    return tag.location_id


class NotAValidLocation(Exception):
    pass


class NotAValidTagUID(Exception):
    pass


class AlreadyRedeemedTag(Exception):
    pass


class MissingRedeemInfo(Exception):
    pass
