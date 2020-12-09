from django.core.management.base import BaseCommand

from ...queries import create_admin_user


class Command(BaseCommand):
    help = 'Creates an admin user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]

        create_admin_user(email=email, password=password)
