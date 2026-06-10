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
            ('101', 'Standard Room', 1, 150000, 'rooms/room101.jpg',
             'A cozy Standard Room with a queen-size bed, modern amenities, and a warm ambiance perfect for couples or solo travellers.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, Daily Housekeeping'),
            ('102', 'Standard Room', 1, 155000, 'rooms/room102.jpg',
             'Comfortable Standard Room featuring a plush queen bed, flat-screen TV, and elegant decor for a restful stay.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, Daily Housekeeping'),
            ('201', 'Deluxe Room',   2, 250000, 'rooms/room201.jpg',
             'Spacious Deluxe Room with panoramic city views, a king-size bed, and premium furnishings for a truly elevated experience.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, City View, Room Service, Bathrobe'),
            ('202', 'Deluxe Room',   2, 260000, 'rooms/room202.jpg',
             'Elegant Deluxe Room with city vistas, a luxurious king bed, marble bathroom, and curated in-room dining options.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, City View, Room Service, Bathrobe, Jacuzzi'),
            ('301', 'Executive Suite', 3, 400000, 'rooms/room301.jpg',
             'Our Executive Suite combines a generous living lounge with a king bedroom, butler service, and breathtaking views.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, City View, Butler Service, Private Lounge, Jacuzzi, Room Service'),
            ('302', 'Executive Suite', 3, 420000, 'rooms/room302.jpg',
             'Refined Executive Suite featuring a private lounge, king bed, and exclusive access to our executive floor amenities.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, City View, Butler Service, Private Lounge, Room Service'),
            ('401', 'Presidential Suite', 4, 800000, 'rooms/room401.jpg',
             'The pinnacle of luxury — our Presidential Suite offers a grand living room, private dining, butler service, and unparalleled comfort.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Full Bar, Panoramic View, Butler Service, Private Dining, Jacuzzi, Gym Access, Concierge'),
            ('103', 'Family Room',   1, 300000, 'rooms/room103.jpg',
             'Spacious Family Room with two queen beds, extra storage, and family-friendly amenities to keep every member comfortable.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, Extra Beds, Daily Housekeeping, Child Amenities'),
            ('104', 'Family Room',   1, 310000, 'rooms/room104.jpg',
             'Welcoming Family Room designed for four, with two queen beds, a play area corner, and ample natural light.',
             'Free WiFi, Air Conditioning, Flat-screen TV, Mini Bar, Extra Beds, Daily Housekeeping, Child Amenities, Play Area'),
        ]

        for number, cat_name, floor, price, image_path, desc, amenities in rooms:
            Room.objects.get_or_create(
                room_number=number,
                defaults={
                    'category': cat_objects[cat_name],
                    'floor': floor,
                    'price_per_night': price,
                    'is_available': True,
                    'image': image_path,
                    'description': desc,
                    'amenities': amenities,
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