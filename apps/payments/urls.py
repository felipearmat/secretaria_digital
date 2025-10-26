"""
URLs for the payments app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CouponViewSet, CouponUsageViewSet, PaymentViewSet, 
    ActorCostViewSet, FinancialReportViewSet
)

router = DefaultRouter()
router.register(r'cupons', CouponViewSet, basename='coupon')
router.register(r'usos-cupom', CouponUsageViewSet, basename='coupon-usage')
router.register(r'pagamentos', PaymentViewSet, basename='payment')
router.register(r'custos-ator', ActorCostViewSet, basename='actor-cost')
router.register(r'relatorios', FinancialReportViewSet, basename='financial-report')

urlpatterns = [
    path('', include(router.urls)),
]
