from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# Simple health check view
def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('',       health_check,            name='health-check'),
    path('admin/',        admin.site.urls),
    path('api/auth/',     include('accounts.urls')),
    path('api/',       include('recipes.urls')),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)