"""
URLs for the notifications app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificacaoViewSet, ConfiguracaoNotificacaoViewSet, 
    TemplateNotificacaoViewSet
)

router = DefaultRouter()
router.register(r'notificacoes', NotificacaoViewSet)
router.register(r'configuracoes', ConfiguracaoNotificacaoViewSet)
router.register(r'templates', TemplateNotificacaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
