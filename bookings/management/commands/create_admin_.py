from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Create default admin user safely"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = os.environ.get("DJANGO_ADMIN_USERNAME", "admin")
        email = os.environ.get("DJANGO_ADMIN_EMAIL", "admin@hotel.com")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "admin1234")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS("Admin created successfully"))
        else:
            self.stdout.write("Admin already exists")