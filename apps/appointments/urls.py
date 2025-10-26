"""
URLs for the appointments app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, AppointmentViewSet, RecurrenceViewSet, BlockViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'recurrences', RecurrenceViewSet)
router.register(r'blocks', BlockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
