from django import forms
import re
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Client, Booking, Service, Master
from django.utils import timezone
from django.forms.widgets import DateInput

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        min_length=8,
        help_text='Минимум 8 символов, включая буквы и цифры.'
    )
    confirm_password = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=16,
        help_text='Формат: +7(XXX)XXX-XX-XX',
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password']
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match("^[a-zA-Z0-9]+$", username):
            raise ValidationError('Логин может содержать только латинские буквы и цифры.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.match("^(?=.*[a-zA-Z])(?=.*[0-9]).{8,}$", password):
            raise ValidationError('Пароль должен содержать минимум 8 символов, включая буквы и цифры.')
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError('Пароли не совпадают.')
        return confirm_password

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        pattern = re.compile(r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$')
        if not pattern.match(phone):
            raise ValidationError('Неверный формат телефона. Используйте формат: +7(XXX)XXX-XX-XX.')
        return phone

class BookingForm(forms.ModelForm):
    master = forms.ModelChoiceField(queryset=Master.objects.all(), label='Выберите мастера')

    class Meta:
        model = Booking
        fields = ['datetime', 'service', 'master']  # Добавлен выбор мастера
        widgets = {
            'datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_datetime(self):
        datetime = self.cleaned_data.get('datetime')
        if datetime < timezone.now():
            raise ValidationError('Выберите дату и время в будущем.')
        return datetime

    def clean(self):
        cleaned_data = super().clean()
        master = cleaned_data.get('master')
        datetime = cleaned_data.get('datetime')

        # Проверка на занятость мастера
        if master and datetime:
            overlapping_bookings = Booking.objects.filter(master=master, datetime=datetime)
            if overlapping_bookings.exists():
                raise ValidationError('Этот мастер занят в выбранное время.')

        return cleaned_data

class TimeSlotGenerationForm(forms.Form):
    start_date = forms.DateTimeField(label='Start Date', widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(label='End Date', widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

