from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from ...models import User, AppUser, ManagerUser, PromoterUser, AdminUser


class Command(BaseCommand):
    help = 'Validates the Permission Groups'

    def handle(self, *args, **options):

        # Validating App Users
        self.validate_appers()

        # Validating Managers
        self.validate_managers()

        # Validating Promoters
        self.validate_promoters()

        # Validating Admins
        self.validate_admins()

    def validate_appers(self):

        # Checking that a Permission Group for App Users exists
        appers_group, _ = Group.objects.get_or_create(name='appers_permission_group')

        # Listing every permission that an App User should have
        appers_permission_codenames = [
            'view_location',
            'view_badge',
            'view_collection',
            'check_collection_status',
            'redeem_badge',
            'redeem_reward',
            'view_reward',
        ]

        # Clearing previous permissions
        appers_group.permissions.clear()

        # Adding Permissions to Group
        for permission in Permission.objects.filter(codename__in=appers_permission_codenames):
            appers_group.permissions.add(permission)

        # Making sure every AppUser is in the Appers' Permission Group
        for apper in AppUser.objects.all():
            user = User.objects.get(id=apper.user_id)
            user.groups.add(appers_group)

    def validate_managers(self):

        # Checking that a Permission Group for Managers exists
        managers_group, _ = Group.objects.get_or_create(name='managers_permission_group')

        # Listing every permission that an Manager should have
        managers_permission_codenames = [
            'add_location',
            'view_location',
            'view_badge',
            'view_collection',
            'view_reward',
        ]

        # Clearing previous permissions
        managers_group.permissions.clear()
        # Adding Permissions to Group
        for permission in Permission.objects.filter(codename__in=managers_permission_codenames):
            managers_group.permissions.add(permission)

        # Making sure every ManagerUser is in the Managers' Permission Group
        for manager in ManagerUser.objects.all():
            user = User.objects.get(id=manager.user_id)
            user.groups.add(managers_group)

    def validate_promoters(self):

        # Checking that a Permission Group for Promoters exists
        promoters_group, _ = Group.objects.get_or_create(name='promoters_permission_group')

        # Listing every permission that an Promoter should have
        promoters_permission_codenames = [
            'view_location',
            'add_badge',
            'view_badge',
            'add_reward',
            'view_reward',
            'add_collection',
            'view_collection',
        ]

        # Clearing previous permissions
        promoters_group.permissions.clear()
        # Adding Permissions to Group
        for permission in Permission.objects.filter(codename__in=promoters_permission_codenames):
            promoters_group.permissions.add(permission)

        # Making sure every PromoterUser is in the Promoters' Permission Group
        for promoter in PromoterUser.objects.all():
            user = User.objects.get(id=promoter.user_id)
            user.groups.add(promoters_group)

    def validate_admins(self):

        # Checking that a Permission Group for Admins exists
        admins_group, _ = Group.objects.get_or_create(name='admins_permission_group')

        # Listing every permission that an Admin should have
        admins_permission_codenames = [
            'view_location',
            'locations.view_stats',
            'badges.view_stats',
            'rewards.view_stats',
            'badges_collections.view_stats',
            'change_location',
            'delete_location',
            'view_badge',
            'change_location',
            'delete_location',
            'add_tag',
            'view_tag',
            'change_tag',
            'delete_tag',
            'view_reward',
            'change_reward',
            'delete_reward',
            'view_collection',
            'change_collection',
            'delete_collection',
        ]

        # Clearing previous permissions
        admins_group.permissions.clear()
        # Adding existing Permissions to Group
        for permission in Permission.objects.filter(codename__in=admins_permission_codenames):
            admins_group.permissions.add(permission)

        # Making sure every AdminUser is in the Admins' Permission Group
        for admin in AdminUser.objects.all():
            user = User.objects.get(id=admin.user_id)
            user.groups.add(admins_group)
