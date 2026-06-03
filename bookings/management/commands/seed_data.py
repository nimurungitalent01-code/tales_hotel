from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bookings.models import RoomCategory, Room, GuestProfile


class Command(BaseCommand):
    help = 'Seeds the database with sample Tales Hotel data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Tales Hotel data...')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@taleshotel.com', 'admin1234')
            self.stdout.write(self.style.SUCCESS('  Created superuser: admin / admin1234'))

        categories = [
            ('Standard Room', 'Cozy and comfortable rooms ideal for solo travellers and couples.', 150000, 2),
            ('Deluxe Room', 'Spacious rooms with premium furnishings and a garden or pool view.', 250000, 2),
            ('Executive Suite', 'Elegant suites with a separate lounge area and city views.', 400000, 3),
            ('Presidential Suite', 'The pinnacle of luxury — expansive suite with butler service.', 800000, 4),
            ('Family Room', 'Generously sized rooms designed for families with children.', 300000, 4),
        ]
        cat_objects = {}
        for name, desc, price, occ in categories:
            cat, created = RoomCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'base_price': price, 'max_occupancy': occ}
            )
            cat_objects[name] = cat
            if created:
                self.stdout.write(f'  Created category: {name}')

        rooms = [
            ('101', 'Standard Room', 1, 150000, 'A bright, well-appointed standard room with en-suite bathroom, queen bed, flat-screen TV, and complimentary WiFi.', 'WiFi, Air Conditioning, En-suite Bathroom, TV, Safe, Mini Fridge'),
            ('102', 'Standard Room', 1, 155000, 'Garden-facing standard room with natural light and serene views. Perfect for a restful stay.', 'WiFi, Air Conditioning, En-suite Bathroom, TV, Garden View'),
            ('201', 'Deluxe Room', 2, 250000, 'Spacious deluxe room featuring premium bedding, work desk, rainfall shower, and stunning city views.', 'WiFi, Air Conditioning, King Bed, Rainfall Shower, City View, Room Service, Mini Bar'),
            ('202', 'Deluxe Room', 2, 260000, 'Pool-facing deluxe room with luxurious amenities including a whirlpool bathtub and bespoke decor.', 'WiFi, Air Conditioning, King Bed, Whirlpool Bathtub, Pool View, Room Service, Mini Bar'),
            ('301', 'Executive Suite', 3, 400000, 'Magnificent executive suite with a separate living room, premium espresso machine, and panoramic views of the city skyline.', 'WiFi, Air Conditioning, King Bed, Living Room, Espresso Machine, Panoramic View, Butler Service, Jacuzzi'),
            ('302', 'Executive Suite', 3, 420000, 'Corner executive suite bathed in natural light with floor-to-ceiling windows and bespoke furnishings.', 'WiFi, Air Conditioning, King Bed, Corner Views, Living Area, Premium Minibar, Butler Service'),
            ('401', 'Presidential Suite', 4, 800000, 'Our crown jewel — the Presidential Suite spans the entire top floor with a private terrace, grand piano, and unrivalled luxury.', 'WiFi, Air Conditioning, Master Bedroom, Private Terrace, Grand Piano, Full Kitchen, Butler Service, Jacuzzi, Gym Access'),
            ('103', 'Family Room', 1, 300000, 'Specially designed family room with two queen beds and a safe family-friendly environment.', 'WiFi, Air Conditioning, Two Queen Beds, Children Amenities, TV, Mini Fridge, Cot Available'),
            ('104', 'Family Room', 1, 310000, 'Spacious family room with bunk beds for children and a garden view.', 'WiFi, Air Conditioning, Queen Bed, Bunk Beds, Garden View, Play Area Access'),
        ]
        for number, cat_name, floor, price, desc, amenities in rooms:
            room, created = Room.objects.get_or_create(
                room_number=number,
                defaults={
                    'category': cat_objects[cat_name],
                    'floor': floor,
                    'price_per_night': price,
                    'description': desc,
                    'amenities': amenities,
                    'is_available': True,
                }
            )
            if created:
                self.stdout.write(f'  Created room: {number} ({cat_name})')

        if not User.objects.filter(username='guest1').exists():
            u = User.objects.create_user('guest1', 'guest1@email.com', 'guest1234', first_name='Alice', last_name='Nakato')
            GuestProfile.objects.create(user=u, phone_number='+256701234567', national_id='CM900100012345')
            self.stdout.write(self.style.SUCCESS('  Created demo guest: guest1 / guest1234'))

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!'))
        self.stdout.write('Admin: admin / admin1234')
        self.stdout.write('Guest: guest1 / guest1234')
