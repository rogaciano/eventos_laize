from django.db import models
from .models import Event

class CostCategory(models.Model):
    """Categorias de custos para eventos (ex: equipamentos, alimentação, transporte)"""
    name = models.CharField(max_length=100, verbose_name='Nome')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Categoria de Custo'
        verbose_name_plural = 'Categorias de Custos'
        ordering = ['name']


class EventCost(models.Model):
    """Custos específicos associados a um evento"""
    TYPE_CHOICES = [
        ('budget', 'Orçamento'),
        ('actual', 'Custo Real'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='costs')
    category = models.ForeignKey(CostCategory, on_delete=models.PROTECT, related_name='event_costs')
    description = models.CharField(max_length=255, verbose_name='Descrição')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor (R$)')
    cost_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='actual', verbose_name='Tipo')
    date = models.DateField(verbose_name='Data')
    paid = models.BooleanField(default=False, verbose_name='Pago')
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True, verbose_name='Comprovante')
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

    class Meta:
        verbose_name = 'Custo de Evento'
        verbose_name_plural = 'Custos de Eventos'
        ordering = ['-date']
