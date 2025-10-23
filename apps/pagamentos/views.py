"""
Views para o app de pagamentos.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Cupom, UsoCupom, Pagamento, CustoAtor, RelatorioFinanceiro
from .serializers import (
    CupomSerializer, UsoCupomSerializer, PagamentoSerializer,
    CustoAtorSerializer, RelatorioFinanceiroSerializer
)


class CupomViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar cupons."""
    
    queryset = Cupom.objects.all()
    serializer_class = CupomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra cupons baseado no usuário logado."""
        user = self.request.user
        
        if user.is_superadmin:
            return Cupom.objects.all()
        elif user.is_admin:
            return Cupom.objects.filter(empresa=user.empresa)
        elif user.is_manager:
            return Cupom.objects.filter(empresa=user.empresa)
        else:
            return Cupom.objects.filter(empresa=user.empresa, ativo=True)
    
    @action(detail=False, methods=['post'])
    def validar(self, request):
        """Valida um cupom pelo código."""
        codigo = request.data.get('codigo')
        if not codigo:
            return Response(
                {'error': 'Código do cupom é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cupom = Cupom.objects.get(codigo=codigo)
            if cupom.is_valido():
                return Response({
                    'valido': True,
                    'cupom': CupomSerializer(cupom).data
                })
            else:
                return Response({
                    'valido': False,
                    'erro': 'Cupom inválido ou expirado'
                })
        except Cupom.DoesNotExist:
            return Response({
                'valido': False,
                'erro': 'Cupom não encontrado'
            })


class UsoCupomViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar usos de cupons."""
    
    queryset = UsoCupom.objects.all()
    serializer_class = UsoCupomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra usos de cupons baseado no usuário logado."""
        user = self.request.user
        
        if user.is_superadmin:
            return UsoCupom.objects.all()
        elif user.is_admin:
            return UsoCupom.objects.filter(cupom__empresa=user.empresa)
        else:
            return UsoCupom.objects.filter(cliente=user)


class PagamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar pagamentos."""
    
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra pagamentos baseado no usuário logado."""
        user = self.request.user
        
        if user.is_superadmin:
            return Pagamento.objects.all()
        elif user.is_admin:
            return Pagamento.objects.filter(agendamento__servico__empresa=user.empresa)
        else:
            return Pagamento.objects.filter(agendamento__cliente=user)


class CustoAtorViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar custos dos atores."""
    
    queryset = CustoAtor.objects.all()
    serializer_class = CustoAtorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra custos baseado no usuário logado."""
        user = self.request.user
        
        if user.is_superadmin:
            return CustoAtor.objects.all()
        elif user.is_admin:
            return CustoAtor.objects.filter(ator__empresa=user.empresa)
        else:
            return CustoAtor.objects.filter(ator=user)
    
    def perform_create(self, serializer):
        """Define o criador do custo."""
        serializer.save(criado_por=self.request.user)


class RelatorioFinanceiroViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar relatórios financeiros."""
    
    queryset = RelatorioFinanceiro.objects.all()
    serializer_class = RelatorioFinanceiroSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra relatórios baseado no usuário logado."""
        user = self.request.user
        
        if user.is_superadmin:
            return RelatorioFinanceiro.objects.all()
        elif user.is_admin:
            return RelatorioFinanceiro.objects.filter(empresa=user.empresa)
        elif user.is_manager:
            return RelatorioFinanceiro.objects.filter(empresa=user.empresa)
        else:
            return RelatorioFinanceiro.objects.filter(ator=user)
    
    @action(detail=False, methods=['post'])
    def gerar(self, request):
        """Gera um novo relatório financeiro."""
        data_inicio = request.data.get('data_inicio')
        data_fim = request.data.get('data_fim')
        tipo = request.data.get('tipo', 'completo')
        ator_id = request.data.get('ator_id')
        
        if not data_inicio or not data_fim:
            return Response(
                {'error': 'data_inicio e data_fim são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Implementar lógica de geração de relatório
        # Por enquanto, retorna dados básicos
        dados = {
            'receitas': 0,
            'custos': 0,
            'lucro': 0,
            'agendamentos': 0
        }
        
        relatorio = RelatorioFinanceiro.objects.create(
            empresa=request.user.empresa,
            ator_id=ator_id,
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dados=dados
        )
        
        return Response(RelatorioFinanceiroSerializer(relatorio).data)
