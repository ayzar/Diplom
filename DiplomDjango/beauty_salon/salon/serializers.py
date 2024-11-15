from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['client', 'master', 'datetime', 'service', 'status']

    def validate(self, data):
        """
        Проверка, доступен ли выбранный временной слот.
        """
        # Создаем объект бронирования для проверки
        booking = Booking(
            client=data['client'],
            master=data['master'],
            datetime=data['datetime'],
            service=data['service']
        )

        # Проверяем, доступен ли выбранный временной слот
        if not booking.is_time_slot_available():
            raise serializers.ValidationError("Выбранный временной слот уже занят или вне рабочего времени.")

        return data

    def create(self, validated_data):
        """
        Создание нового бронирования с проверкой временного слота.
        """
        # Если данные прошли валидацию, создаем новое бронирование
        return Booking.objects.create(**validated_data)
