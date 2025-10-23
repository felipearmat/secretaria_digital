"""
Configuração do admin para o app de pagamentos.
"""

from django.contrib import admin
from .models import Cupom, UsoCupom, Pagamento, CustoAtor, RelatorioFinanceiro


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'empresa', 'ator', 'tipo_desconto', 'valor_desconto', 'ativo']
    list_filter = ['empresa', 'tipo_desconto', 'ativo', 'data_inicio', 'data_fim']
    search_fields = ['codigo', 'empresa__nome']
    readonly_fields = ['criado_em']


@admin.register(UsoCupom)
class UsoCupomAdmin(admin.ModelAdmin):
    list_display = ['cupom', 'cliente', 'agendamento', 'valor_desconto_aplicado', 'usado_em']
    list_filter = ['usado_em', 'cupom__empresa']
    search_fields = ['cupom__codigo', 'cliente__username']


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['agendamento', 'valor', 'metodo', 'status', 'data_pagamento']
    list_filter = ['metodo', 'status', 'criado_em']
    search_fields = ['agendamento__cliente__username']


@admin.register(CustoAtor)
class CustoAtorAdmin(admin.ModelAdmin):
    list_display = ['ator', 'descricao', 'valor', 'data', 'categoria']
    list_filter = ['categoria', 'data', 'ator']
    search_fields = ['ator__username', 'descricao']


@admin.register(RelatorioFinanceiro)
class RelatorioFinanceiroAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'ator', 'tipo', 'data_inicio', 'data_fim', 'criado_em']
    list_filter = ['tipo', 'empresa', 'criado_em']
    search_fields = ['empresa__nome']
    readonly_fields = ['criado_em']
