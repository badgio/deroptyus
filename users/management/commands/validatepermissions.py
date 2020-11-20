from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from ...models import User, AppUser, ManagerUser, PromoterUser


class Command(BaseCommand):
    help = 'Validates the Permission Groups'

    def handle(self, *args, **options):

        # Validating App Users
        self.validate_appers()

        # Validating Managers
        self.validate_managers()

        # Validating Promoters
        self.validate_promoters()

    def validate_appers(self):

        # Checking that a Permission Group for App Users exists
        appers_group, _ = Group.objects.get_or_create(name='appers_permission_group')

        # Listing every permission that an App User should have
        appers_permission_codenames = [
            'change_appuser',
            'view_appuser',
            'delete_appuser'
        ]

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
            'change_manageruser',
            'view_manageruser',
            'delete_manageruser'
        ]

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
            'change_promoteruser',
            'view_promoteruser',
            'delete_promoteruser'
        ]

        # Adding Permissions to Group
        for permission in Permission.objects.filter(codename__in=promoters_permission_codenames):
            promoters_group.permissions.add(permission)

        # Making sure every PromoterUser is in the Promoters' Permission Group
        for promoter in PromoterUser.objects.all():
            user = User.objects.get(id=promoter.user_id)
            user.groups.add(promoters_group)
