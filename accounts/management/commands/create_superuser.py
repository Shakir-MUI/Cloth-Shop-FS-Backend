from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                username="admin"
            )
            self.stdout.write("✅ Superuser created")
        else:
            self.stdout.write("ℹ️ Superuser already exists")
