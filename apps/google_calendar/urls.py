from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GoogleCalendarIntegrationViewSet,
    GoogleCalendarEventViewSet,
    GoogleCalendarSyncLogViewSet
)

router = DefaultRouter()
router.register(r'integrations', GoogleCalendarIntegrationViewSet)
router.register(r'events', GoogleCalendarEventViewSet)
router.register(r'sync-logs', GoogleCalendarSyncLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

