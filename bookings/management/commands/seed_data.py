from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from bookings.models import RoomCategory, Room, GuestProfile


class Command(BaseCommand):
    help = 'Seeds Tales Hotel safely for production'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Tales Hotel data...')

        User = get_user_model()

        # ---------------- ADMIN ----------------
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@taleshotel.com',
                password='admin1234'
            )
            self.stdout.write(self.style.SUCCESS('Created admin'))

        # ---------------- CATEGORIES ----------------
        categories = [
            ('Standard Room', 'Cozy rooms ideal for couples.', 150000, 2),
            ('Deluxe Room', 'Premium rooms with views.', 250000, 2),
            ('Executive Suite', 'Luxury suite with lounge.', 400000, 3),
            ('Presidential Suite', 'Top-tier luxury suite.', 800000, 4),
            ('Family Room', 'Spacious family-friendly rooms.', 300000, 4),
        ]

        cat_objects = {}

        for name, desc, price, occ in categories:
            cat, created = RoomCategory.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'base_price': price,
                    'max_occupancy': occ
                }
            )
            cat_objects[name] = cat

        # ---------------- ROOMS ----------------
        rooms = [
            ('101', 'Standard Room', 1, 150000),
            ('102', 'Standard Room', 1, 155000),
            ('201', 'Deluxe Room', 2, 250000),
            ('202', 'Deluxe Room', 2, 260000),
            ('301', 'Executive Suite', 3, 400000),
            ('302', 'Executive Suite', 3, 420000),
            ('401', 'Presidential Suite', 4, 800000),
            ('103', 'Family Room', 1, 300000),
            ('104', 'Family Room', 1, 310000),
        ]

        for number, cat_name, floor, price in rooms:
            Room.objects.get_or_create(
                room_number=number,
                defaults={
                    'category': cat_objects[cat_name],
                    'floor': floor,
                    'price_per_night': price,
                    'is_available': True,
                }
            )

        # ---------------- DEMO GUEST ----------------
        if not User.objects.filter(username='guest1').exists():
            u = User.objects.create_user(
                username='guest1',
                email='guest1@email.com',
                password='guest1234',
                first_name='Alice',
                last_name='Nakato'
            )
            GuestProfile.objects.create(
                user=u,
                phone_number='+256701234567',
                national_id='CM900100012345'
            )

        self.stdout.write(self.style.SUCCESS('Seeding complete'))
        self.stdout.write('Admin: admin / admin1234')
        self.stdout.write('Guest: guest1 / guest1234')