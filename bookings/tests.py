from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from django.utils import timezone
from .models import GuestProfile, Room, RoomCategory, Booking, Payment
from .forms import BookingForm

class TalesHotelTests(TestCase):
    def setUp(self):
        # Create users
        self.guest_user = User.objects.create_user(username='guest', password='password', first_name='John', last_name='Doe', email='john@example.com')
        self.guest_profile = GuestProfile.objects.create(
            user=self.guest_user,
            phone_number='123456789',
            national_id='ID12345'
        )
        self.admin_user = User.objects.create_superuser(username='admin', password='password', is_staff=True)

        # Create category and room
        self.category = RoomCategory.objects.create(name='Deluxe', base_price=100.00, max_occupancy=2)
        self.room = Room.objects.create(
            room_number='101',
            category=self.category,
            floor=1,
            price_per_night=100.00,
            is_available=True
        )

    def test_booking_validation_success(self):
        # Test valid booking
        form_data = {
            'check_in_date': datetime.date.today(),
            'check_out_date': datetime.date.today() + datetime.timedelta(days=2),
            'num_guests': 2,
            'special_requests': ''
        }
        form = BookingForm(data=form_data, room=self.room)
        self.assertTrue(form.is_valid())

    def test_booking_occupancy_exceeded(self):
        # Test booking with guests exceeding max occupancy
        form_data = {
            'check_in_date': datetime.date.today(),
            'check_out_date': datetime.date.today() + datetime.timedelta(days=2),
            'num_guests': 3,  # Max is 2
            'special_requests': ''
        }
        form = BookingForm(data=form_data, room=self.room)
        self.assertFalse(form.is_valid())
        self.assertIn("allows a maximum of 2 guests", form.errors['__all__'][0])

    def test_booking_room_unavailable(self):
        # Mark room as unavailable
        self.room.is_available = False
        self.room.save()

        form_data = {
            'check_in_date': datetime.date.today(),
            'check_out_date': datetime.date.today() + datetime.timedelta(days=2),
            'num_guests': 1,
            'special_requests': ''
        }
        form = BookingForm(data=form_data, room=self.room)
        self.assertFalse(form.is_valid())
        self.assertIn("temporarily out of service", form.errors['__all__'][0])

    def test_booking_overlap_validation(self):
        # Create an approved booking
        Booking.objects.create(
            guest=self.guest_profile,
            room=self.room,
            check_in_date=datetime.date.today() + datetime.timedelta(days=2),
            check_out_date=datetime.date.today() + datetime.timedelta(days=5),
            num_guests=1,
            status='approved',
            total_amount=300
        )

        # Test overlap check-in inside the range
        form_data = {
            'check_in_date': datetime.date.today() + datetime.timedelta(days=3),
            'check_out_date': datetime.date.today() + datetime.timedelta(days=4),
            'num_guests': 1,
            'special_requests': ''
        }
        form = BookingForm(data=form_data, room=self.room)
        self.assertFalse(form.is_valid())
        self.assertIn("already booked or pending approval", form.errors['__all__'][0])

    def test_payment_security_unapproved_booking(self):
        # Create a pending booking
        booking = Booking.objects.create(
            guest=self.guest_profile,
            room=self.room,
            check_in_date=datetime.date.today() + datetime.timedelta(days=1),
            check_out_date=datetime.date.today() + datetime.timedelta(days=3),
            num_guests=1,
            status='pending',
            total_amount=200
        )

        # Log in the guest
        self.client.login(username='guest', password='password')

        # Try to access payment page for pending booking
        response = self.client.get(reverse('make_payment', args=[booking.pk]))
        self.assertRedirects(response, reverse('booking_detail', args=[booking.pk]))
        
        # Try to post payment for pending booking
        post_response = self.client.post(reverse('make_payment', args=[booking.pk]), {
            'payment_method': 'cash',
            'transaction_ref': '12345'
        })
        self.assertRedirects(post_response, reverse('booking_detail', args=[booking.pk]))
        self.assertFalse(hasattr(booking, 'payment'))

    def test_payment_security_approved_booking(self):
        # Create an approved booking
        booking = Booking.objects.create(
            guest=self.guest_profile,
            room=self.room,
            check_in_date=datetime.date.today() + datetime.timedelta(days=1),
            check_out_date=datetime.date.today() + datetime.timedelta(days=3),
            num_guests=1,
            status='approved',
            total_amount=200
        )

        # Log in the guest
        self.client.login(username='guest', password='password')

        # Access payment page
        response = self.client.get(reverse('make_payment', args=[booking.pk]))
        self.assertEqual(response.status_code, 200)

        # Submit payment
        post_response = self.client.post(reverse('make_payment', args=[booking.pk]), {
            'payment_method': 'cash',
            'transaction_ref': 'REF1234'
        })
        self.assertRedirects(post_response, reverse('booking_detail', args=[booking.pk]))
        
        # Refresh and assert payment was created
        booking.refresh_from_db()
        self.assertTrue(hasattr(booking, 'payment'))
        self.assertEqual(booking.payment.payment_status, 'completed')

    def test_cancel_paid_booking_fails(self):
        # Create an approved booking
        booking = Booking.objects.create(
            guest=self.guest_profile,
            room=self.room,
            check_in_date=datetime.date.today() + datetime.timedelta(days=1),
            check_out_date=datetime.date.today() + datetime.timedelta(days=3),
            num_guests=1,
            status='approved',
            total_amount=200
        )
        # Add completed payment
        Payment.objects.create(
            booking=booking,
            amount_paid=200,
            payment_method='cash',
            payment_status='completed',
            paid_at=timezone.now()
        )

        # Log in the guest
        self.client.login(username='guest', password='password')

        # Try to cancel
        response = self.client.get(reverse('cancel_booking', args=[booking.pk]))
        self.assertRedirects(response, reverse('booking_detail', args=[booking.pk]))
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'approved')  # Status should not change to cancelled

    def test_admin_double_approval_prevention(self):
        # Create two bookings that overlap
        booking1 = Booking.objects.create(
            guest=self.guest_profile,
            room=self.room,
            check_in_date=datetime.date.today() + datetime.timedelta(days=1),
            check_out_date=datetime.date.today() + datetime.timedelta(days=3),
            num_guests=1,
            status='pending',
            total_amount=200
        )
        booking2 = Booking.objects.create(
            guest=self.guest_profile,
            room=self.room,
            check_in_date=datetime.date.today() + datetime.timedelta(days=2),
            check_out_date=datetime.date.today() + datetime.timedelta(days=4),
            num_guests=1,
            status='pending',
            total_amount=200
        )

        # Log in as admin
        self.client.login(username='admin', password='password')

        # Approve booking1
        response1 = self.client.post(reverse('admin_update_booking', args=[booking1.pk]), {'action': 'approve'})
        self.assertRedirects(response1, reverse('admin_bookings'))
        booking1.refresh_from_db()
        self.assertEqual(booking1.status, 'approved')

        # Try to approve booking2 (should fail because of overlap with booking1 which is now approved)
        response2 = self.client.post(reverse('admin_update_booking', args=[booking2.pk]), {'action': 'approve'})
        self.assertRedirects(response2, reverse('admin_bookings'))
        booking2.refresh_from_db()
        self.assertEqual(booking2.status, 'pending')  # Should remain pending

    def test_guest_profile_update(self):
        # Log in the guest
        self.client.login(username='guest', password='password')

        # Update profile
        response = self.client.post(reverse('profile'), {
            'first_name': 'Johnathan',
            'last_name': 'Doe',
            'email': 'johnathan@example.com',
            'phone_number': '987654321',
            'national_id': 'ID98765',
            'date_of_birth': '1990-01-01'
        })
        self.assertRedirects(response, reverse('profile'))

        # Verify database
        self.guest_user.refresh_from_db()
        self.guest_profile.refresh_from_db()
        self.assertEqual(self.guest_user.first_name, 'Johnathan')
        self.assertEqual(self.guest_user.email, 'johnathan@example.com')
        self.assertEqual(self.guest_profile.phone_number, '987654321')
        self.assertEqual(self.guest_profile.national_id, 'ID98765')
