from django.apps import AppConfig


class BookingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'

    def ready(self):
        from django.contrib.auth import get_user_model
        from .models import RoomCategory, Room

        User = get_user_model()

        # ---- CREATE ADMIN (SAFE) ----
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin1234"
            )

        # ---- CREATE BASIC DATA (ROOMS) ----
        if RoomCategory.objects.count() == 0:
            cat = RoomCategory.objects.create(
                name="Standard",
                description="Default category"
            )
        else:
            cat = RoomCategory.objects.first()

        if Room.objects.count() == 0:
            for i in range(1, 4):
                Room.objects.create(
                    room_number=f"A{i}",
                    category=cat,
                    price_per_night=100,
                    is_available=True
                )
