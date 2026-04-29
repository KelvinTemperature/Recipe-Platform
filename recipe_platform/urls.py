from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
import cloudinary

def cloudinary_test(request):
    try:
        config = cloudinary.config()
        return JsonResponse({
            'cloud_name': config.cloud_name,
            'api_key': config.api_key[:6] + '...' if config.api_key else None,
            'configured': bool(config.cloud_name)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})

# Simple health check view
def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('',       health_check,            name='health-check'),
    path('admin/',        admin.site.urls),
    path('api/auth/',     include('accounts.urls')),
    path('api/',       include('recipes.urls')),
    path('cloudinary-test/', cloudinary_test),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)