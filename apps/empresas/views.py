"""
Views for the companies app.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing companies."""
    
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters companies based on the logged-in user."""
        user = self.request.user
        
        if user.role == 'superadmin':
            return Company.objects.all()
        elif user.role in ['admin', 'manager']:
            return Company.objects.filter(id=user.company_id)
        else:
            return Company.objects.none()
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Returns company statistics."""
        company = self.get_object()
        
        stats = {
            'total_users': company.total_users,
            'total_appointments_today': company.total_appointments_today,
            'company_active': company.is_active,
        }
        
        return Response(stats)
