from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api/', include('salon.urls')),
    path('', include('salon.urls')),  # Маршруты основного приложения
    path('', include('django.contrib.auth.urls')),  # это включает URL для выхода
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
