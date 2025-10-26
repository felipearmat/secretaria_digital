"""
Views for the payments app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Coupon, CouponUsage, Payment, ActorCost, FinancialReport
from .serializers import (
    CouponSerializer, CouponUsageSerializer, PaymentSerializer,
    ActorCostSerializer, FinancialReportSerializer
)


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet to manage coupons."""
    
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter coupons based on logged user."""
        user = self.request.user
        
        if user.is_superadmin:
            return Coupon.objects.all()
        elif user.is_admin:
            return Coupon.objects.filter(company=user.company)
        elif user.is_manager:
            return Coupon.objects.filter(company=user.company)
        else:
            return Coupon.objects.filter(company=user.company, is_active=True)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validates a coupon by code."""
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'Coupon code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                return Response({
                    'valid': True,
                    'coupon': CouponSerializer(coupon).data
                })
            else:
                return Response({
                    'valid': False,
                    'error': 'Invalid or expired coupon'
                })
        except Coupon.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Coupon not found'
            })


class CouponUsageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing coupon usage."""
    
    queryset = CouponUsage.objects.all()
    serializer_class = CouponUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters coupon usage based on logged user."""
        user = self.request.user
        
        if user.is_superadmin:
            return CouponUsage.objects.all()
        elif user.is_admin:
            return CouponUsage.objects.filter(coupon__company=user.company)
        else:
            return CouponUsage.objects.filter(client=user)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters payments based on logged user."""
        user = self.request.user
        
        if user.is_superadmin:
            return Payment.objects.all()
        elif user.is_admin:
            return Payment.objects.filter(appointment__service__company=user.company)
        else:
            return Payment.objects.filter(appointment__client=user)


class ActorCostViewSet(viewsets.ModelViewSet):
    """ViewSet for managing actor costs."""
    
    queryset = ActorCost.objects.all()
    serializer_class = ActorCostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters costs based on logged user."""
        user = self.request.user
        
        if user.is_superadmin:
            return ActorCost.objects.all()
        elif user.is_admin:
            return ActorCost.objects.filter(actor__company=user.company)
        else:
            return ActorCost.objects.filter(actor=user)
    
    def perform_create(self, serializer):
        """Sets the cost creator."""
        serializer.save(created_by=self.request.user)


class FinancialReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing financial reports."""
    
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters reports based on logged user."""
        user = self.request.user
        
        if user.is_superadmin:
            return FinancialReport.objects.all()
        elif user.is_admin:
            return FinancialReport.objects.filter(company=user.company)
        elif user.is_manager:
            return FinancialReport.objects.filter(company=user.company)
        else:
            return FinancialReport.objects.filter(actor=user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generates a new financial report."""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        type = request.data.get('type', 'complete')
        actor_id = request.data.get('actor_id')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Implement report generation logic
        # For now, returns basic data
        data = {
            'revenues': 0,
            'costs': 0,
            'profit': 0,
            'appointments': 0
        }
        
        report = FinancialReport.objects.create(
            company=request.user.company,
            actor_id=actor_id,
            type=type,
            start_date=start_date,
            end_date=end_date,
            data=data
        )
        
        return Response(FinancialReportSerializer(report).data)
