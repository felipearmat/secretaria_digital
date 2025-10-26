from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GoogleCalendarIntegrationViewSet,
    GoogleCalendarEventViewSet,
    GoogleCalendarSyncLogViewSet
)

router = DefaultRouter()
router.register(r'integrations', GoogleCalendarIntegrationViewSet, basename='googlecalendar-integration')
router.register(r'events', GoogleCalendarEventViewSet, basename='googlecalendar-event')
router.register(r'sync-logs', GoogleCalendarSyncLogViewSet, basename='googlecalendar-synclog')

urlpatterns = [
    path('', include(router.urls)),
]

