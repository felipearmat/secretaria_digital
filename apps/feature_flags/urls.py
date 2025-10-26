"""
URLs for the feature flags app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeatureFlagViewSet, LocalizationConfigViewSet

router = DefaultRouter()
router.register(r'flags', FeatureFlagViewSet)
router.register(r'localization', LocalizationConfigViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

