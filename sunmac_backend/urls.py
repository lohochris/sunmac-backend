from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from core import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # App-specific routes (all core URLs)
    path('', include('core.urls')),
    
    # Django built-in authentication URLs (login, logout, password reset)
    # Note: These will work but your custom views in core.urls will override them
    path('accounts/', include('django.contrib.auth.urls')),
]

# ✅ Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)