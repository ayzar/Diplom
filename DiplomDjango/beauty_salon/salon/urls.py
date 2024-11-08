from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('master/<int:master_id>/', views.master_detail, name='master_detail'),
    path('price_list/', views.price_list, name='price_list'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('book_service/', views.book_service, name='book_service'),
    path('success/', views.success_page, name='success_page'),
    path('get_categories/', views.get_categories, name='get_categories'),
    path('get_services_by_master/<int:master_id>/', views.get_services_by_master, name='get_services_by_master'),
    path('get_services_by_category/<int:category_id>/', views.get_services_by_category, name='get_services_by_category'),  # Получение услуг по категории
    path('get_masters_by_service/<int:service_id>/', views.get_masters_by_service, name='get_masters_by_service'),  # Получение мастеров по услуге
    path('get_time_slots_by_master/<int:master_id>/', views.get_time_slots_by_master, name='get_time_slots_by_master'),  # Получение временных слотов
]

