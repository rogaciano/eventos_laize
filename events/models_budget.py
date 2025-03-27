from django.db import models
from .models import Event

class EventBudgetItem(models.Model):
    """Modelo para itens de orçamento de eventos"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='budget_items')
    code = models.CharField(max_length=10, verbose_name='Código')
    description = models.TextField(verbose_name='Descrição')
    date = models.DateField(verbose_name='Data')
    start_time = models.TimeField(verbose_name='Horário Inicial')
    end_time = models.TimeField(verbose_name='Horário Final')
    quantity = models.PositiveIntegerField(verbose_name='Quantidade')
    unit_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Unitário')
    
    class Meta:
        verbose_name = 'Item de Orçamento'
        verbose_name_plural = 'Itens de Orçamento'
        ordering = ['date', 'start_time']
    
    @property
    def total_value(self):
        """Calcula o valor total do item"""
        return self.quantity * self.unit_value
    
    def __str__(self):
        return f"{self.code} - {self.description[:30]}"


class DefaultBudgetSettings(models.Model):
    """Configurações padrão para orçamentos"""
    payment_terms = models.TextField(verbose_name='Condições de Pagamento', blank=True, null=True)
    validity_days = models.PositiveIntegerField(verbose_name='Validade (dias)', default=30)
    client_responsibilities = models.TextField(verbose_name='Responsabilidades do Cliente', blank=True, null=True)
    additional_notes = models.TextField(verbose_name='Observações Adicionais', blank=True, null=True)
    bank_details = models.TextField(verbose_name='Dados Bancários', blank=True, null=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração Padrão de Orçamento'
        verbose_name_plural = 'Configurações Padrão de Orçamento'
    
    @classmethod
    def get_default(cls):
        """Retorna as configurações padrão ativas ou cria uma nova"""
        default_settings = cls.objects.filter(is_active=True).first()
        if not default_settings:
            default_settings = cls.objects.create(
                payment_terms="50% de sinal e 50% no dia do evento.",
                validity_days=30,
                client_responsibilities="Providenciar local adequado para a realização do evento.\nDisponibilizar pontos de energia elétrica conforme necessidade.",
                additional_notes="Valores sujeitos a alteração sem aviso prévio."
            )
        return default_settings
    
    def __str__(self):
        return f"Configurações Padrão (Atualizado em: {self.updated_at.strftime('%d/%m/%Y')})"


class BudgetSettings(models.Model):
    """Configurações gerais para orçamentos"""
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='budget_settings')
    payment_terms = models.TextField(verbose_name='Condições de Pagamento', blank=True, null=True)
    validity_days = models.PositiveIntegerField(verbose_name='Validade (dias)', default=30)
    client_responsibilities = models.TextField(verbose_name='Responsabilidades do Cliente', blank=True, null=True)
    additional_notes = models.TextField(verbose_name='Observações Adicionais', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Configuração de Orçamento'
        verbose_name_plural = 'Configurações de Orçamento'
    
    def __str__(self):
        return f"Configurações de Orçamento - {self.event.title}"
    
    @classmethod
    def create_from_default(cls, event):
        """Cria configurações para um evento baseado nas configurações padrão"""
        default_settings = DefaultBudgetSettings.get_default()
        
        return cls.objects.create(
            event=event,
            payment_terms=default_settings.payment_terms,
            validity_days=default_settings.validity_days,
            client_responsibilities=default_settings.client_responsibilities,
            additional_notes=default_settings.additional_notes
        )
