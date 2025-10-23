"""
Main URLs for the secretariaVirtual project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.autenticacao.urls')),
    path('api/companies/', include('apps.empresas.urls')),
    path('api/appointments/', include('apps.agendamentos.urls')),
    path('api/notifications/', include('apps.notificacoes.urls')),
    path('api/payments/', include('apps.pagamentos.urls')),
    path('api/google-calendar/', include('apps.google_calendar.urls')),
    path('api/feature-flags/', include('apps.feature_flags.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
