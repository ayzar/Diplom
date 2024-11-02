from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .forms import LoginForm, RegistrationForm, BookingForm
from .models import Master, Service, Review, Portfolio, Category, Client


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

def booking(request, master_id):
    master = get_object_or_404(Master, id=master_id)
    return render(request, 'salon/booking.html', {'master': master})

def price_list(request):
    categories = Category.objects.prefetch_related('services')
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

@login_required
def book_service(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user.client  # Предполагается, что у клиента есть связь с пользователем
            booking.save()
            return redirect('profile')  # Переход на личный кабинет после успешной записи
    else:
        form = BookingForm()
    return render(request, 'salon/book_service.html', {'form': form})