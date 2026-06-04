from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
import datetime

from .models import (GuestProfile, Room, RoomCategory, Booking,
                     Payment, GuestHistory, ContactFeedback)
from .forms import (GuestRegistrationForm, BookingForm, PaymentForm,
                    ContactFeedbackForm, RoomSearchForm, UserUpdateForm,
                    GuestProfileForm)


def is_admin(user):
    return user.is_staff or user.is_superuser


# ─── PUBLIC VIEWS ───────────────────────────────────────────────────────────

def home(request):
    featured_rooms = Room.objects.filter(is_available=True).select_related('category')[:6]
    categories = RoomCategory.objects.all()
    search_form = RoomSearchForm()
    return render(request, 'bookings/home.html', {
        'featured_rooms': featured_rooms,
        'categories': categories,
        'search_form': search_form,
    })


def room_list(request):
    rooms = Room.objects.filter(is_available=True).select_related('category')
    form = RoomSearchForm(request.GET or None)
    check_in = check_out = None

    if form.is_valid():
        check_in = form.cleaned_data.get('check_in_date')
        check_out = form.cleaned_data.get('check_out_date')
        num_guests = form.cleaned_data.get('num_guests')
        max_price = form.cleaned_data.get('max_price')

        if check_in and check_out:
            # exclude rooms with overlapping approved/pending bookings
            booked_rooms = Booking.objects.filter(
                status__in=['pending', 'approved'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in,
            ).values_list('room_id', flat=True)
            rooms = rooms.exclude(id__in=booked_rooms)

        if num_guests:
            rooms = rooms.filter(category__max_occupancy__gte=num_guests)
        if max_price:
            rooms = rooms.filter(price_per_night__lte=max_price)

    categories = RoomCategory.objects.all()
    return render(request, 'bookings/room_list.html', {
        'rooms': rooms,
        'form': form,
        'categories': categories,
        'check_in': check_in,
        'check_out': check_out,
    })


def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, 'bookings/room_detail.html', {'room': room})


def contact(request):
    if request.method == 'POST':
        form = ContactFeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been received. We'll be in touch shortly.")
            return redirect('contact')
    else:
        form = ContactFeedbackForm()
    return render(request, 'bookings/contact.html', {'form': form})


# ─── AUTH VIEWS ─────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = GuestRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Tales Hotel, {user.first_name}! Your account is ready.")
            return redirect('dashboard')
    else:
        form = GuestRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out. We hope to see you again soon.")
    return redirect('home')


# ─── GUEST VIEWS ────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    try:
        guest = request.user.guest_profile
    except GuestProfile.DoesNotExist:
        messages.error(request, "Guest profile not found.")
        return redirect('home')
    bookings = Booking.objects.filter(guest=guest).select_related('room', 'room__category')
    return render(request, 'bookings/dashboard.html', {
        'guest': guest,
        'bookings': bookings,
        'pending_count': bookings.filter(status='pending').count(),
        'approved_count': bookings.filter(status='approved').count(),
    })


@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if not room.is_available:
        messages.error(request, f"Room {room.room_number} is temporarily out of service and cannot be booked.")
        return redirect('room_list')

    try:
        guest = request.user.guest_profile
    except GuestProfile.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('home')

    if request.method == 'POST':
        form = BookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.guest = guest
            booking.room = room
            booking.total_amount = booking.calculate_total()
            booking.save()
            messages.success(request, f"Booking request submitted for Room {room.room_number}! Awaiting approval.")
            return redirect('booking_detail', booking_id=booking.pk)
    else:
        form = BookingForm(room=room)
    return render(request, 'bookings/book_room.html', {'form': form, 'room': room})


@login_required
def booking_detail(request, booking_id):
    try:
        guest = request.user.guest_profile
        booking = get_object_or_404(Booking, pk=booking_id, guest=guest)
    except GuestProfile.DoesNotExist:
        if request.user.is_staff:
            booking = get_object_or_404(Booking, pk=booking_id)
        else:
            return redirect('home')
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    try:
        guest = request.user.guest_profile
        booking = get_object_or_404(Booking, pk=booking_id, guest=guest)
    except GuestProfile.DoesNotExist:
        return redirect('home')
    if booking.status in ['pending', 'approved']:
        if hasattr(booking, 'payment') and booking.payment.payment_status == 'completed':
            messages.error(request, "Paid bookings cannot be cancelled directly. Please contact support.")
            return redirect('booking_detail', booking_id=booking.pk)
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
    else:
        messages.error(request, "This booking cannot be cancelled.")
    return redirect('dashboard')


@login_required
def make_payment(request, booking_id):
    try:
        guest = request.user.guest_profile
        booking = get_object_or_404(Booking, pk=booking_id, guest=guest)
    except GuestProfile.DoesNotExist:
        return redirect('home')

    if booking.status != 'approved':
        messages.error(request, "You can only make a payment for approved bookings.")
        return redirect('booking_detail', booking_id=booking.pk)

    if hasattr(booking, 'payment') and booking.payment.payment_status == 'completed':
        messages.info(request, "This booking has already been paid.")
        return redirect('booking_detail', booking_id=booking.pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount_paid = booking.total_amount
            payment.payment_status = 'completed'
            payment.paid_at = timezone.now()
            payment.save()
            messages.success(request, "Payment successful! Thank you for choosing Tales Hotel.")
            return redirect('booking_detail', booking_id=booking.pk)
    else:
        form = PaymentForm()
    return render(request, 'bookings/make_payment.html', {'form': form, 'booking': booking})


@login_required
def guest_history(request):
    try:
        guest = request.user.guest_profile
    except GuestProfile.DoesNotExist:
        return redirect('home')
    history = GuestHistory.objects.filter(guest=guest).select_related('booking', 'recorded_by')
    completed_bookings = Booking.objects.filter(guest=guest, status='completed')
    return render(request, 'bookings/guest_history.html', {
        'history': history,
        'completed_bookings': completed_bookings,
    })


# ─── ADMIN VIEWS ────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    approved_bookings = Booking.objects.filter(status='approved').count()
    total_guests = GuestProfile.objects.count()
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    unread_messages = ContactFeedback.objects.filter(is_read=False).count()
    recent_bookings = Booking.objects.select_related(
        'guest__user', 'room').order_by('-booked_at')[:10]
    return render(request, 'bookings/admin_dashboard.html', {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'total_guests': total_guests,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'unread_messages': unread_messages,
        'recent_bookings': recent_bookings,
    })


@login_required
@user_passes_test(is_admin)
def admin_bookings(request):
    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.select_related('guest__user', 'room__category')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'bookings/admin_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
    })


@login_required
@user_passes_test(is_admin)
def admin_update_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    action = request.POST.get('action')
    if action == 'approve':
        # Check for overlapping approved bookings
        overlapping_approved = Booking.objects.filter(
            room=booking.room,
            status='approved',
            check_in_date__lt=booking.check_out_date,
            check_out_date__gt=booking.check_in_date
        ).exclude(pk=booking.pk)
        if overlapping_approved.exists():
            messages.error(request, f"Cannot approve Booking #{booking.pk} because Room {booking.room.room_number} is already booked/approved for those dates.")
        else:
            booking.status = 'approved'
            messages.success(request, f"Booking #{booking.pk} approved.")
    elif action == 'cancel':
        booking.status = 'cancelled'
        messages.warning(request, f"Booking #{booking.pk} cancelled.")
    elif action == 'complete':
        booking.status = 'completed'
        messages.success(request, f"Booking #{booking.pk} marked as completed.")
    booking.save()
    return redirect('admin_bookings')


@login_required
@user_passes_test(is_admin)
def admin_guests(request):
    guests = GuestProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'bookings/admin_guests.html', {'guests': guests})


@login_required
@user_passes_test(is_admin)
def admin_guest_detail(request, guest_id):
    guest = get_object_or_404(GuestProfile, pk=guest_id)
    bookings = Booking.objects.filter(guest=guest).select_related('room')
    history = GuestHistory.objects.filter(guest=guest)
    if request.method == 'POST':
        note = request.POST.get('note', '').strip()
        booking_id = request.POST.get('booking_id')
        if note:
            booking_obj = Booking.objects.filter(pk=booking_id).first() if booking_id else None
            GuestHistory.objects.create(
                guest=guest, booking=booking_obj,
                notes=note, recorded_by=request.user
            )
            messages.success(request, "Note added to guest history.")
            return redirect('admin_guest_detail', guest_id=guest_id)
    return render(request, 'bookings/admin_guest_detail.html', {
        'guest': guest, 'bookings': bookings, 'history': history,
    })


@login_required
@user_passes_test(is_admin)
def admin_rooms(request):
    rooms = Room.objects.select_related('category').order_by('room_number')
    return render(request, 'bookings/admin_rooms.html', {'rooms': rooms})


@login_required
@user_passes_test(is_admin)
def admin_toggle_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    room.is_available = not room.is_available
    room.save()
    status = "available" if room.is_available else "unavailable"
    messages.success(request, f"Room {room.room_number} is now {status}.")
    return redirect('admin_rooms')


@login_required
@user_passes_test(is_admin)
def admin_messages(request):
    feedback = ContactFeedback.objects.order_by('-submitted_at')
    msg_id = request.GET.get('mark_read')
    if msg_id:
        ContactFeedback.objects.filter(pk=msg_id).update(is_read=True)
        return redirect('admin_messages')
    return render(request, 'bookings/admin_messages.html', {'feedback': feedback})


@login_required
@user_passes_test(is_admin)
def admin_schedule(request):
    """Room schedule / availability view"""
    today = datetime.date.today()
    week_later = today + datetime.timedelta(days=14)
    rooms = Room.objects.select_related('category').order_by('floor', 'room_number')
    active_bookings = Booking.objects.filter(
        status__in=['approved', 'pending'],
        check_out_date__gte=today,
    ).select_related('guest__user', 'room').order_by('check_in_date')
    return render(request, 'bookings/admin_schedule.html', {
        'rooms': rooms,
        'active_bookings': active_bookings,
        'today': today,
    })


@login_required
def profile(request):
    try:
        guest = request.user.guest_profile
    except GuestProfile.DoesNotExist:
        messages.error(request, "Guest profile not found.")
        return redirect('home')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = GuestProfileForm(request.POST, request.FILES, instance=guest)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = GuestProfileForm(instance=guest)

    return render(request, 'bookings/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'guest': guest,
    })
