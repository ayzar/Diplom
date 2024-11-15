from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
from django.utils import timezone

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('ServiceCategory', on_delete=models.CASCADE,
                                 related_name='services')  # Связь с моделью категории
    duration = models.DurationField()  # Поле для продолжительности
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена услуги

    def __str__(self):
        return self.name

    def formatted_duration(self):
        # Извлекаем количество минут из timedelta
        total_seconds = self.duration.total_seconds()  # Получаем общее количество секунд
        total_minutes = total_seconds // 60  # Переводим в минуты
        hours = total_minutes // 60  # Вычисляем количество часов
        minutes = total_minutes % 60  # Оставшиеся минуты

        if hours > 0:
            return f"{int(hours)} ч {int(minutes)} мин"
        else:
            return f"{int(minutes)} мин"



class Master(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, default=" ")  # Специализация
    experience = models.IntegerField(null=True, blank=True)  # Опыт в годах
    description = models.TextField(default="Описание отсутствует")  # Описание с дефолтным значением
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)  # Рейтинг
    categories = models.ManyToManyField(ServiceCategory, related_name='masters')  # Связь с категориями
    photo = models.ImageField(upload_to='masters/', null=True, blank=True)  # Фото мастера
    services = models.ManyToManyField(Service, related_name='masters')  # Поле ManyToMany для выбора услуг

    def __str__(self):
        return self.name

    def formatted_info(self):
        # Форматируем информацию о мастере
        experience_text = f"{self.experience} лет" if self.experience else "Без опыта"
        return f"{self.name} - {self.specialization}, стаж {experience_text}, рейтинг {self.rating}  "


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь с моделью User
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=16)  # Пример: +7(999)999-99-99

    def __str__(self):
        return f"{self.user.username} {self.user.first_name} {self.user.last_name} (Телефон: {self.phone})"


class Review(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Оценка от 1 до 5
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.client.user.username} на {self.master.name}"


class Portfolio(models.Model):
    master = models.ForeignKey('Master', on_delete=models.CASCADE, related_name='portfolios')
    photo = models.ImageField(upload_to='portfolio/')
    description = models.CharField(max_length=255)  # Краткое описание работы

    def __str__(self):
        return f"Работа мастера {self.master.name}: {self.description}"






class TimeSlot(models.Model):
    master = models.ForeignKey('Master', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        # Преобразуем start_time и end_time в Московскую временную зону
        moscow_start_time = timezone.localtime(self.start_time)
        moscow_end_time = timezone.localtime(self.end_time)
        return f'{moscow_start_time} - {moscow_end_time} ({self.master.name})'

    def is_past(self):
        # Используем московское время для проверки
        return self.start_time < timezone.localtime(timezone.now())

    @property
    def date(self):
        # Возвращаем только дату из start_time
        return self.start_time.date()

class Booking(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='bookings')
    datetime = models.DateTimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Ожидается'),
        ('completed', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ], default='pending')

    def is_time_slot_available(self):
        # Проверка, занято ли это время другим клиентом
        overlapping_bookings = Booking.objects.filter(
            master=self.master,
            datetime__lt=self.datetime + self.service.duration,
            datetime__gt=self.datetime
        )

        # Проверка рабочего времени
        start_time = self.datetime.time()
        end_time = (self.datetime + self.service.duration).time()
        salon_open_time = time(10, 0)  # 10:00
        salon_close_time = time(21, 0)  # 21:00

        if not (salon_open_time <= start_time <= salon_close_time):
            return False  # Начало услуги вне рабочего времени
        if not (salon_open_time <= end_time <= salon_close_time):
            return False  # Окончание услуги выходит за пределы рабочего времени

        return not overlapping_bookings.exists()

    def __str__(self):
        return f"Запись {self.client.user.username} {self.client.user.first_name} {self.client.user.last_name} (Телефон: {self.client.phone}) к мастеру {self.master.name}"