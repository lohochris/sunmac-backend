from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # App-specific routes
    path('accounts/', include('django.contrib.auth.urls')),  # Enables login, logout, password reset
]
