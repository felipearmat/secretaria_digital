"""
Serializers para o app de pagamentos.
"""

from rest_framework import serializers
from .models import Cupom, UsoCupom, Pagamento, CustoAtor, RelatorioFinanceiro
from apps.agendamentos.serializers import AgendamentoSerializer
from apps.autenticacao.serializers import UsuarioSerializer
from apps.empresas.serializers import EmpresaSerializer


class CupomSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Cupom."""
    
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)
    ator_nome = serializers.CharField(source='ator.get_full_name', read_only=True)
    servicos_nomes = serializers.StringRelatedField(source='servicos', many=True, read_only=True)
    
    class Meta:
        model = Cupom
        fields = [
            'id', 'codigo', 'empresa', 'ator', 'tipo_desconto', 'valor_desconto',
            'data_inicio', 'data_fim', 'max_usos', 'max_usos_por_cliente',
            'servicos', 'ativo', 'criado_em', 'empresa_nome', 'ator_nome', 'servicos_nomes'
        ]
        read_only_fields = ['id', 'criado_em']


class UsoCupomSerializer(serializers.ModelSerializer):
    """Serializer para o modelo UsoCupom."""
    
    cupom_codigo = serializers.CharField(source='cupom.codigo', read_only=True)
    cliente_nome = serializers.CharField(source='cliente.get_full_name', read_only=True)
    
    class Meta:
        model = UsoCupom
        fields = [
            'id', 'cupom', 'cliente', 'agendamento', 'valor_desconto_aplicado',
            'usado_em', 'cupom_codigo', 'cliente_nome'
        ]
        read_only_fields = ['id', 'usado_em']


class PagamentoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Pagamento."""
    
    agendamento_info = AgendamentoSerializer(source='agendamento', read_only=True)
    
    class Meta:
        model = Pagamento
        fields = [
            'id', 'agendamento', 'valor', 'metodo', 'status', 'observacoes',
            'data_pagamento', 'criado_em', 'agendamento_info'
        ]
        read_only_fields = ['id', 'criado_em']


class CustoAtorSerializer(serializers.ModelSerializer):
    """Serializer para o modelo CustoAtor."""
    
    ator_nome = serializers.CharField(source='ator.get_full_name', read_only=True)
    criado_por_nome = serializers.CharField(source='criado_por.get_full_name', read_only=True)
    
    class Meta:
        model = CustoAtor
        fields = [
            'id', 'ator', 'descricao', 'valor', 'data', 'categoria',
            'observacoes', 'criado_por', 'criado_em', 'ator_nome', 'criado_por_nome'
        ]
        read_only_fields = ['id', 'criado_em']


class RelatorioFinanceiroSerializer(serializers.ModelSerializer):
    """Serializer para o modelo RelatorioFinanceiro."""
    
    empresa_nome = serializers.CharField(source='empresa.nome', read_only=True)
    ator_nome = serializers.CharField(source='ator.get_full_name', read_only=True)
    
    class Meta:
        model = RelatorioFinanceiro
        fields = [
            'id', 'empresa', 'ator', 'tipo', 'data_inicio', 'data_fim',
            'dados', 'criado_em', 'empresa_nome', 'ator_nome'
        ]
        read_only_fields = ['id', 'criado_em']
