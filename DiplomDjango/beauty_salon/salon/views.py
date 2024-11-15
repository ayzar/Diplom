from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from .forms import LoginForm, RegistrationForm, BookingForm
from .models import Master, Service, Review, Portfolio, Client, ServiceCategory, Booking, TimeSlot
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, time, timedelta
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from .models import TimeSlot
from .serializers import BookingSerializer
from .utils import moscow_tz
import locale
import pytz
from rest_framework import serializers, viewsets, status
from .models import Booking, Client, Master, Service
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse

def home(request):
    masters = Master.objects.all()
    services = Service.objects.all()
    reviews = Review.objects.all()
    portfolios = Portfolio.objects.all()

    context = {
        'masters': masters,
        'services': services,
        'reviews': reviews,
        'portfolios': portfolios,
    }
    return render(request, 'salon/home.html', context)


def master_detail(request, master_id):
    master = Master.objects.get(id=master_id)
    context = {
        'master': master,
    }
    return render(request, 'salon/master_detail.html', context)


def price_list(request):
    categories = ServiceCategory.objects.prefetch_related('services')
    return render(request, 'salon/price_list.html', {'categories': categories})


@login_required
def profile_view(request):
    try:
        client = Client.objects.get(user=request.user)
    except Client.DoesNotExist:
        client = None  # Или перенаправить на страницу создания клиента

    return render(request, 'salon/profile.html', {'client': client})


def user_account(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        return redirect('login')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                messages.error(request, 'Неправильное имя пользователя или пароль.')
    else:
        form = LoginForm()
    return render(request, 'salon/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()  # Сохраняем пользователя
            # Теперь создаем запись в модели Client
            Client.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email']
            )
            messages.success(request, 'Регистрация прошла успешно!')
            login(request, user)  # Авторизуем пользователя
            return redirect('profile')  # Переход к личному кабинету
    else:
        form = RegistrationForm()
    return render(request, 'salon/register.html', {'form': form})


from django.core.mail import send_mail


@login_required
def book_service(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = Client.objects.get(user=request.user)

            # Проверка доступности времени и соответствия рабочему графику
            if booking.is_time_slot_available():
                booking.save()

                # Отправка уведомления (как и раньше)
                send_mail(
                    'Подтверждение записи',
                    f'Вы успешно записались на услугу {booking.service.name} к мастеру {booking.master.name} на {booking.datetime}.',
                    'from@example.com',
                    [booking.client.email],
                    fail_silently=False,
                )

                messages.success(request, 'Вы успешно записались на услугу!')
                return redirect('success_page')
            else:
                messages.error(request, 'Выбранное время недоступно. Пожалуйста, выберите другое время.')
        else:
            messages.error(request, 'Произошла ошибка при записи.')
    else:
        form = BookingForm()

    return render(request, 'salon/book_service.html', {'form': form})


def booking_view(request):
    categories = ServiceCategory.objects.all()  # Получаем все категории из базы данных
    return render(request, 'booking_service.html', {'categories': categories})

def get_categories(request):
    categories = ServiceCategory.objects.all()
    categories_list = [{'id': category.id, 'name': category.name} for category in categories]
    return JsonResponse({'categories': categories_list})

def get_services_by_category(request, category_id):
    # Фильтруем услуги по переданному category_id
    services = Service.objects.filter(category_id=category_id)

    # Формируем список услуг
    services_data = [
        {
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'duration': service.formatted_duration()  # Форматированное время выполнения
        }
        for service in services
    ]

    # Отправляем данные в формате JSON
    return JsonResponse({'services': services_data})


def get_services_by_master(request, master_id):
    master = Master.objects.get(id=master_id)
    services = Service.objects.filter(category__in=master.categories.all())

    services_data = [{'id': service.id, 'name': service.name} for service in services]
    return JsonResponse({'services': services_data})


def get_masters_by_service(request, service_id):
    masters = Master.objects.filter(services__id=service_id)

    masters_data = [
        {
            'id': master.id,
            'name': master.formatted_info(),  # Используем метод formatted_info для форматирования строки
            'rating': master.rating,
            'specialization': master.specialization,
            'experience': master.experience,
            'photo': master.photo.url if master.photo else None  # Получаем URL изображения
        }
        for master in masters
    ]

    return JsonResponse({'masters': masters_data})

# Функция для получения временных слотов по мастеру
def get_time_slots_by_master(request, master_id):
    try:
        master = Master.objects.get(id=master_id)
        # Получаем все временные слоты для выбранного мастера
        time_slots = TimeSlot.objects.filter(master=master)

        # Если временные слоты не существуют
        if not time_slots.exists():
            return JsonResponse({'message': 'Нет доступных временных слотов.'}, status=404)

        time_slots_data = [
            {
                'id': time_slot.id,
                'start_time': time_slot.start_time.strftime('%H:%M'),
                'end_time': time_slot.end_time.strftime('%H:%M')
            }
            for time_slot in time_slots
        ]
        return JsonResponse({'time_slots': time_slots_data})

    except Master.DoesNotExist:
        return JsonResponse({'error': 'Мастер не найден'}, status=404)






@login_required
def available_time_slots(request, master_id, service_id):
    # Получаем услугу и её продолжительность
    service = Service.objects.get(id=service_id)
    master = Master.objects.get(id=master_id)

    # Список всех возможных слотов (например, каждые 30 минут)
    possible_slots = []
    start_time = datetime.combine(datetime.today(), time(10, 0))  # Начало дня
    end_time = datetime.combine(datetime.today(), time(21, 0))  # Конец дня

    current_time = start_time
    while current_time + service.duration <= end_time:
        possible_slots.append(current_time)
        current_time += timedelta(minutes=60)

    # Фильтруем только свободные слоты
    available_slots = []
    for slot in possible_slots:
        overlapping_bookings = Booking.objects.filter(
            master=master,
            datetime__lt=slot + service.duration,
            datetime__gt=slot
        )
        if not overlapping_bookings.exists():
            available_slots.append(slot.strftime('%H:%M'))

    return JsonResponse({'time_slots': available_slots})


@login_required
def success_page(request):
    return render(request, 'salon/success.html')

def get_available_dates_by_master(request, master_id):
    # Получаем все слоты для мастера
    slots = TimeSlot.objects.filter(master_id=master_id, is_available=True)

    # Фильтруем слоты по будущим датам (не прошедшим)
    available_dates = []
    for slot in slots:
        if not slot.is_past():  # Проверяем, что дата не прошедшая
            if slot.date not in available_dates:
                available_dates.append(slot.date)

    available_dates.sort()  # Сортируем даты

    return JsonResponse({"dates": available_dates})


@api_view(['GET'])
def get_available_dates_by_master(request, master_id):
    # Получаем все временные слоты для выбранного мастера, которые доступны
    time_slots = TimeSlot.objects.filter(master_id=master_id, is_available=True)

    # Получаем текущую дату в Московской временной зоне
    current_date = timezone.localtime(timezone.now()).date()

    # Используем set для уникальных дат
    available_dates = set()

    # Проходим по временным слотам и добавляем уникальные даты
    for slot in time_slots:
        slot_date = slot.start_time.date()

        # Добавляем только будущие даты
        if slot_date >= current_date:
            available_dates.add(str(slot_date))

    # Преобразуем set обратно в список и сортируем даты
    available_dates = sorted(available_dates)

    # Возвращаем список доступных дат
    return Response({"dates": available_dates})

current_time = timezone.localtime(timezone.now())
# Устанавливаем русскую локаль
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
# Московский часовой пояс
moscow_tz = pytz.timezone('Europe/Moscow')
# Задайте временную зону для Москвы
moscow_tz = pytz.timezone('Europe/Moscow')

@api_view(['GET'])
@permission_classes([AllowAny])  # Это разрешит доступ всем, даже неавторизованным пользователям
def get_available_dates_by_master(request, master_id):
    # Получаем все временные слоты для выбранного мастера, которые доступны
    time_slots = TimeSlot.objects.filter(master_id=master_id, is_available=True)

    # Получаем текущую дату в Московской временной зоне
    current_date = timezone.localtime(timezone.now()).date()

    # Используем set для уникальных дат
    available_dates = set()

    # Проходим по временным слотам и добавляем уникальные даты
    for slot in time_slots:
        slot_date = slot.start_time.date()

        # Добавляем только будущие даты
        if slot_date >= current_date:
            available_dates.add(str(slot_date))

    # Преобразуем set обратно в список и сортируем даты
    available_dates = sorted(available_dates)

    # Возвращаем список доступных дат
    return Response({"dates": available_dates})

class BookingViewSet(viewsets.ModelViewSet):
    """
    API ViewSet для работы с бронированиями.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Привязываем клиента (пользователя) к бронированию
        serializer.save(client=self.request.user.client)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Только для аутентифицированных пользователей
def create_booking(request):
    # Получаем данные из запроса
    master_id = request.data.get('master')
    service_id = request.data.get('service')
    datetime = request.data.get('datetime')

    # Получаем пользователя (клиента), который делает запрос
    client = request.user.client  # Это клиент, который аутентифицирован

    # Получаем мастера по id
    master = get_object_or_404(Master, id=master_id)

    # Получаем услугу по id
    service = get_object_or_404(Service, id=service_id)

    # Создаем бронирование
    booking = Booking.objects.create(
        client=client,  # Привязываем клиента к бронированию
        master=master,
        service=service,
        datetime=datetime,
    )

    # Возвращаем успешный ответ с деталями бронирования
    return Response({
        'status': 'success',
        'booking_id': booking.id,
        'client_id': client.id,
        'master': master.name,
        'datetime': booking.datetime
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # Это разрешит доступ всем, даже неавторизованным пользователям
def get_time_slots_by_master_and_date(request, master_id, date):
    try:
        master = Master.objects.get(id=master_id)

        # Преобразуем строку даты в объект datetime
        try:
            date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Expected YYYY-MM-DD.'}, status=400)

        # Получаем временные слоты для мастера на указанную дату
        time_slots = TimeSlot.objects.filter(master=master, start_time__date=date_obj)

        # Если слоты не найдены, возвращаем ошибку
        if not time_slots.exists():
            return JsonResponse({'message': 'Нет доступных временных слотов для этой даты.'}, status=404)

        time_slots_data = [
            {
                'id': time_slot.id,
                'start_time': time_slot.start_time.strftime('%H:%M'),
                'end_time': time_slot.end_time.strftime('%H:%M')
            }
            for time_slot in time_slots
        ]
        return JsonResponse({'time_slots': time_slots_data})

    except Master.DoesNotExist:
        return JsonResponse({'error': 'Мастер не найден'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    # Получаем данные из запроса
    master_id = request.data.get('master')
    service_id = request.data.get('service')
    datetime = request.data.get('datetime')

    # Получаем клиента из запроса (предполагаем, что клиент авторизован)
    client = request.user.client  # Это клиент, который делает запрос

    # Проверяем, что мастер и услуга существуют
    try:
        master = Master.objects.get(id=master_id)
    except Master.DoesNotExist:
        return Response({'status': 'error', 'message': 'Master not found'}, status=400)

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'status': 'error', 'message': 'Service not found'}, status=400)

    # Создаем бронирование
    booking = Booking.objects.create(
        client=client,  # Это клиент, который делает запрос
        master=master,
        service=service,
        datetime=datetime,
    )

    # Возвращаем успешный ответ
    return Response({
        'status': 'success',
        'booking_id': booking.id,
        'client_id': booking.client.id,
        'master': master.name,
        'datetime': booking.datetime
    }, status=status.HTTP_201_CREATED)


@login_required
def booking_view(request):
    # Получаем клиента, который авторизован
    client = request.user.client  # объект клиента, связанный с пользователем

    # Передаем ID клиента в шаблон
    return render(request, 'book_service.html', {'client_id': client.id})

