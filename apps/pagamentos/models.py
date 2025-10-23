"""
Modelos para o app de pagamentos.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.autenticacao.models import Usuario
from apps.empresas.models import Empresa
from apps.agendamentos.models import Agendamento, Servico


class Cupom(models.Model):
    """Modelo para representar cupons de desconto."""
    
    TIPO_DESCONTO_CHOICES = (
        ('percentual', 'Percentual'),
        ('valor_fixo', 'Valor Fixo'),
    )

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código do Cupom'
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="cupons",
        verbose_name='Empresa'
    )
    ator = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cupons",
        null=True,
        blank=True,
        verbose_name='Ator/Prestador'
    )
    tipo_desconto = models.CharField(
        max_length=20,
        choices=TIPO_DESCONTO_CHOICES,
        verbose_name='Tipo de Desconto'
    )
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor do Desconto'
    )
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(verbose_name='Data de Fim')
    max_usos = models.PositiveIntegerField(
        default=1,
        verbose_name='Máximo de Usos'
    )
    max_usos_por_cliente = models.PositiveIntegerField(
        default=1,
        verbose_name='Máximo de Usos por Cliente'
    )
    servicos = models.ManyToManyField(
        Servico,
        blank=True,
        verbose_name='Serviços Válidos'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Cupom Ativo'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Cupom'
        verbose_name_plural = 'Cupons'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.codigo} - {self.empresa.nome}"

    def is_valido(self):
        """Verifica se o cupom é válido."""
        hoje = timezone.now().date()
        return (
            self.ativo and
            self.data_inicio <= hoje <= self.data_fim and
            self.usos.count() < self.max_usos
        )

    def pode_ser_usado_por(self, cliente):
        """Verifica se o cupom pode ser usado por um cliente específico."""
        if not self.is_valido():
            return False
        
        usos_cliente = self.usos.filter(cliente=cliente).count()
        return usos_cliente < self.max_usos_por_cliente

    def calcular_desconto(self, valor_original):
        """Calcula o valor do desconto."""
        if self.tipo_desconto == 'percentual':
            return valor_original * (self.valor_desconto / 100)
        else:
            return min(self.valor_desconto, valor_original)


class UsoCupom(models.Model):
    """Modelo para rastrear o uso de cupons."""
    
    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.CASCADE,
        related_name="usos",
        verbose_name='Cupom'
    )
    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="usos_cupom",
        verbose_name='Cliente'
    )
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="usos_cupom",
        verbose_name='Agendamento'
    )
    valor_desconto_aplicado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor do Desconto Aplicado'
    )
    usado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Usado em'
    )

    class Meta:
        verbose_name = 'Uso de Cupom'
        verbose_name_plural = 'Usos de Cupons'
        ordering = ['-usado_em']
        unique_together = ['cupom', 'agendamento']

    def __str__(self):
        return f"{self.cupom.codigo} - {self.cliente.username}"


class Pagamento(models.Model):
    """Modelo para representar pagamentos."""
    
    METODO_CHOICES = (
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência Bancária'),
        ('outro', 'Outro'),
    )

    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('cancelado', 'Cancelado'),
    )

    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="pagamentos",
        verbose_name='Agendamento'
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )
    metodo = models.CharField(
        max_length=20,
        choices=METODO_CHOICES,
        verbose_name='Método de Pagamento'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    data_pagamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data do Pagamento'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Pagamento {self.id} - {self.agendamento}"


class CustoAtor(models.Model):
    """Modelo para representar custos dos atores."""
    
    ator = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="custos",
        verbose_name='Ator/Prestador'
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name='Descrição do Custo'
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )
    data = models.DateField(
        default=timezone.now,
        verbose_name='Data'
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Categoria'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    criado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="custos_criados",
        verbose_name='Criado por'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Custo do Ator'
        verbose_name_plural = 'Custos dos Atores'
        ordering = ['-data', '-criado_em']

    def __str__(self):
        return f"{self.ator.username} - {self.descricao} - R$ {self.valor}"


class RelatorioFinanceiro(models.Model):
    """Modelo para armazenar relatórios financeiros gerados."""
    
    TIPO_RELATORIO_CHOICES = (
        ('receitas', 'Receitas'),
        ('custos', 'Custos'),
        ('lucro', 'Lucro'),
        ('completo', 'Relatório Completo'),
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="relatorios",
        verbose_name='Empresa'
    )
    ator = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="relatorios",
        null=True,
        blank=True,
        verbose_name='Ator/Prestador'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_RELATORIO_CHOICES,
        verbose_name='Tipo de Relatório'
    )
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(verbose_name='Data de Fim')
    dados = models.JSONField(verbose_name='Dados do Relatório')
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Relatório Financeiro'
        verbose_name_plural = 'Relatórios Financeiros'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Relatório {self.get_tipo_display()} - {self.empresa.nome}"
