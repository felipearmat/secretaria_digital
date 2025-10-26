"""
URLs for the payments app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CupomViewSet, UsoCupomViewSet, PagamentoViewSet, 
    CustoAtorViewSet, RelatorioFinanceiroViewSet
)

router = DefaultRouter()
router.register(r'cupons', CupomViewSet)
router.register(r'usos-cupom', UsoCupomViewSet)
router.register(r'pagamentos', PagamentoViewSet)
router.register(r'custos-ator', CustoAtorViewSet)
router.register(r'relatorios', RelatorioFinanceiroViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
