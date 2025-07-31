"""
URL configuration for MedBot project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/symptoms/', include('apps.symptoms.urls')),
    path('api/consultations/', include('apps.consultations.urls')),
    path('api/departments/', include('apps.departments.urls')),
    path('api/healthcare-systems/', include('apps.healthcare_systems.urls')),
    path('api/admin-dashboard/', include('apps.admin_dashboard.urls')),
    path('api/clinic-dashboard/', include('apps.clinic_dashboard.urls')),
    path('api/analytics/', include('apps.analytics.urls')),

    # n8n webhook endpoints
    path('webhooks/n8n/', include('apps.n8n_integration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
