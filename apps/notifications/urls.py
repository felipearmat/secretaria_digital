"""
URLs for the notifications app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, NotificationConfigViewSet, 
    NotificationTemplateViewSet
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)
router.register(r'configs', NotificationConfigViewSet)
router.register(r'templates', NotificationTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
