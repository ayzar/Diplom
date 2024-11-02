from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('master/<int:master_id>/', views.master_detail, name='master_detail'),
    path('booking/<int:master_id>/', views.booking, name='booking'),
    path('price-list/', views.price_list, name='price_list'),
    path('profile/', views.profile_view, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('book_service/', views.book_service, name='book_service'),
]
