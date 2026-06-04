from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('contact/', views.contact, name='contact'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Guest
    path('dashboard/', views.dashboard, name='dashboard'),
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/<int:booking_id>/pay/', views.make_payment, name='make_payment'),
    path('my-history/', views.guest_history, name='guest_history'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-panel/bookings/<int:booking_id>/update/', views.admin_update_booking, name='admin_update_booking'),
    path('admin-panel/guests/', views.admin_guests, name='admin_guests'),
    path('admin-panel/guests/<int:guest_id>/', views.admin_guest_detail, name='admin_guest_detail'),
    path('admin-panel/rooms/', views.admin_rooms, name='admin_rooms'),
    path('admin-panel/rooms/<int:room_id>/toggle/', views.admin_toggle_room, name='admin_toggle_room'),
    path('admin-panel/messages/', views.admin_messages, name='admin_messages'),
    path('admin-panel/schedule/', views.admin_schedule, name='admin_schedule'),
]
