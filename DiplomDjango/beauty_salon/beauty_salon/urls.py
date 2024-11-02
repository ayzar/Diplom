from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('salon.urls')),  # Маршруты основного приложения
    path('', include('django.contrib.auth.urls')),  # это включает URL для выхода
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
