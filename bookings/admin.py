from django.contrib import admin
from .models import GuestProfile, RoomCategory, Room, Booking, Payment, GuestHistory, ContactFeedback

admin.site.site_header = "Tales Hotel Administration"
admin.site.site_title = "Tales Hotel Admin"
admin.site.index_title = "Welcome to Tales Hotel Admin Panel"

@admin.register(GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'national_id', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone_number']

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'max_occupancy']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'category', 'floor', 'price_per_night', 'is_available']
    list_filter = ['category', 'is_available', 'floor']
    list_editable = ['is_available']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest', 'room', 'check_in_date', 'check_out_date', 'status', 'total_amount']
    list_filter = ['status']
    search_fields = ['guest__user__first_name', 'room__room_number']
    list_editable = ['status']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount_paid', 'payment_method', 'payment_status', 'paid_at']

@admin.register(GuestHistory)
class GuestHistoryAdmin(admin.ModelAdmin):
    list_display = ['guest', 'booking', 'recorded_by', 'recorded_at']

@admin.register(ContactFeedback)
class ContactFeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'submitted_at']
    list_filter = ['is_read']
    list_editable = ['is_read']
