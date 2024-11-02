from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Master(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)  # Звание, например "Парикмахер"
    photo = models.ImageField(upload_to='masters/')
    services = models.ManyToManyField(Service, related_name='masters')

    def __str__(self):
        return f"{self.name} - {self.title}"


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Связь с моделью User
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=16)  # Пример: +7(999)999-99-99

    def __str__(self):
        return self.user.username


class Booking(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    datetime = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Ожидается'),
        ('completed', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ], default='pending')

    def __str__(self):
        return f"Запись {self.client.user.username} к {self.master.name} на {self.service.name}"


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
