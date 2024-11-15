from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework.authtoken.views import obtain_auth_token

# Создаем экземпляр DefaultRouter и регистрируем BookingViewSet
router = DefaultRouter()
router.register(r'bookings', views.BookingViewSet)  # Предполагаем, что у вас есть BookingViewSet

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
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
    path('get_services_by_category/<int:category_id>/', views.get_services_by_category, name='get_services_by_category'),
    path('get_masters_by_service/<int:service_id>/', views.get_masters_by_service, name='get_masters_by_service'),
    path('get_time_slots_by_master/<int:master_id>/', views.get_time_slots_by_master, name='get_time_slots_by_master'),
    path('get_available_time_slots/<str:date>/', views.available_time_slots, name='get_available_time_slots'),
    path('get_available_dates_by_master/<int:master_id>/', views.get_available_dates_by_master, name='get_available_dates_by_master'),
    path('get_time_slots_by_master_and_date/<int:master_id>/<str:date>/', views.get_time_slots_by_master_and_date, name='get_time_slots_by_master_and_date'),


    # Используем include для подключения URL-ов от DefaultRouter
    path('api/', include(router.urls)),  # Добавляем сюда маршруты из DefaultRouter
]
