from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class GuestProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='guest_profile')
    phone_number = models.CharField(max_length=15)
    national_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.phone_number}"


class RoomCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    max_occupancy = models.IntegerField(default=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Room Categories"


class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms')
    floor = models.IntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")

    def __str__(self):
        return f"Room {self.room_number} ({self.category.name})"

    def get_amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    num_guests = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.pk} - {self.guest.user.get_full_name()} - Room {self.room.room_number}"

    def get_num_nights(self):
        return (self.check_out_date - self.check_in_date).days

    def calculate_total(self):
        nights = self.get_num_nights()
        return nights * self.room.price_per_night if nights > 0 else 0

    class Meta:
        ordering = ['-booked_at']


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_ref = models.CharField(max_length=100, blank=True, null=True, unique=True)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for Booking #{self.booking.pk} - {self.payment_status}"


class GuestHistory(models.Model):
    guest = models.ForeignKey(GuestProfile, on_delete=models.CASCADE, related_name='history')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.guest.user.get_full_name()} on {self.recorded_at.date()}"

    class Meta:
        verbose_name_plural = "Guest Histories"
        ordering = ['-recorded_at']


class ContactFeedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = "Contact & Feedback"
