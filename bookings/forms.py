from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import GuestProfile, Booking, Payment, ContactFeedback, Room
import datetime


class GuestRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone_number = forms.CharField(max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    national_id = forms.CharField(max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID / Passport'}))
    date_of_birth = forms.DateField(required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            GuestProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                national_id=self.cleaned_data['national_id'],
                date_of_birth=self.cleaned_data.get('date_of_birth'),
            )
        return user


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'num_guests', 'special_requests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'num_guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                'placeholder': 'Any special requests? (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        self.room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        num_guests = cleaned_data.get('num_guests')

        if check_in and check_out:
            if check_in < datetime.date.today():
                raise forms.ValidationError("Check-in date cannot be in the past.")
            if check_out <= check_in:
                raise forms.ValidationError("Check-out date must be after check-in date.")

            if self.room:
                if not self.room.is_available:
                    raise forms.ValidationError(f"Room {self.room.room_number} is temporarily out of service.")

                if num_guests and num_guests > self.room.category.max_occupancy:
                    raise forms.ValidationError(
                        f"This room allows a maximum of {self.room.category.max_occupancy} guests."
                    )

                overlapping = Booking.objects.filter(
                    room=self.room,
                    status__in=['pending', 'approved'],
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                )
                if self.instance and self.instance.pk:
                    overlapping = overlapping.exclude(pk=self.instance.pk)

                if overlapping.exists():
                    raise forms.ValidationError("This room is already booked or pending approval for the selected dates.")

        return cleaned_data


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'transaction_ref']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_ref': forms.TextInput(attrs={'class': 'form-control',
                'placeholder': 'Transaction reference (for mobile money/card)'}),
        }


class ContactFeedbackForm(forms.ModelForm):
    class Meta:
        model = ContactFeedback
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                'placeholder': 'Your message...'}),
        }


class RoomSearchForm(forms.Form):
    check_in_date = forms.DateField(required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Check-in'}))
    check_out_date = forms.DateField(required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'Check-out'}))
    num_guests = forms.IntegerField(required=False, min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Guests', 'min': 1}))
    max_price = forms.DecimalField(required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max price/night'}))


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class GuestProfileForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    national_id = forms.CharField(max_length=20, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID / Passport'}))
    date_of_birth = forms.DateField(required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    profile_picture = forms.ImageField(required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file'}))

    class Meta:
        model = GuestProfile
        fields = ['phone_number', 'national_id', 'date_of_birth', 'profile_picture']

