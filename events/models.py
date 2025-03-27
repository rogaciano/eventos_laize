from django.db import models
from clients.models import Client
from people.models import Person
from django.db.models import Sum
from decimal import Decimal

class Funcao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor Padrão (R$)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Função'
        verbose_name_plural = 'Funções'
        ordering = ['nome']


class EventType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Event Type'
        verbose_name_plural = 'Event Types'
        ordering = ['name']


class Event(models.Model):
    STATUS_CHOICES = [
        ('cadastrado', 'Cadastrado'),
        ('prospectado', 'Prospectado'),
        ('agendado', 'Agendado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
        ('adiado', 'Adiado'),
        ('pendente', 'Pendente de Confirmação'),
        ('orcamento', 'Orçamento'),
        ('pre_producao', 'Pré-produção'),
        ('pos_producao', 'Pós-produção'),
        ('arquivado', 'Arquivado'),
    ]
    
    title = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='events')
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor Contratado (R$)')
    location = models.TextField(blank=True, null=True)
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='cadastrado', verbose_name='Situação')
    description = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(Person, through='EventParticipant', related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start_datetime']
        
    def get_total_participant_costs(self):
        """Retorna o total de custos com participantes"""
        result = self.eventparticipant_set.aggregate(total=Sum('value'))
        return result['total'] or Decimal('0.00')
        
    def get_total_costs(self, cost_type='actual'):
        """Retorna o total de custos do evento por tipo (orçamento ou real)"""
        from .models_cost import EventCost
        result = EventCost.objects.filter(event=self, cost_type=cost_type).aggregate(total=Sum('amount'))
        return result['total'] or Decimal('0.00')
    
    def get_total_budgeted_costs(self):
        """Retorna o total de custos orçados do evento"""
        return self.get_total_costs(cost_type='budget')
    
    def get_total_real_costs(self):
        """Retorna o total de custos reais do evento"""
        return self.get_total_costs(cost_type='actual')
    
    def get_pending_costs(self):
        """Retorna o total de custos pendentes de pagamento"""
        from .models_cost import EventCost
        result = EventCost.objects.filter(event=self, cost_type='actual', paid=False).aggregate(total=Sum('amount'))
        return result['total'] or Decimal('0.00')
        
    def get_total_expenses(self):
        """Retorna o total de despesas (custos reais + participantes)"""
        participant_costs = self.get_total_participant_costs()
        other_costs = self.get_total_costs(cost_type='actual')
        return participant_costs + other_costs
        
    def get_profit(self):
        """Calcula o lucro do evento (receita - despesas)"""
        if not self.value:
            return None
        return self.value - self.get_total_expenses()
        
    def get_profit_margin(self):
        """Calcula a margem de lucro em percentual"""
        if not self.value or self.value == 0:
            return None
        profit = self.get_profit()
        if profit is None:
            return None
        return (profit / self.value) * 100

    def get_profit_margin_percentage(self):
        """Retorna a margem de lucro em percentual"""
        total_expenses = self.get_total_expenses()
        if total_expenses and self.value:
            return ((self.value - total_expenses) / self.value) * 100
        return None


class EventGallery(models.Model):
    """Model to store photos for an event's gallery"""
    event = models.ForeignKey(Event, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events_gallery/', verbose_name="Imagem")
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Título")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    is_primary = models.BooleanField(default=False, verbose_name="Imagem Principal")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Foto de {self.event.title} - {self.title or 'Sem título'}"
    
    def save(self, *args, **kwargs):
        # If this image is set as primary, unset all other primary images for this event
        if self.is_primary:
            EventGallery.objects.filter(event=self.event, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Foto da Galeria do Evento'
        verbose_name_plural = 'Fotos da Galeria do Evento'
        ordering = ['event__title', 'order', 'created_at']


class EventStatusHistory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Event.STATUS_CHOICES, null=True, blank=True, verbose_name='Status Anterior')
    new_status = models.CharField(max_length=20, choices=Event.STATUS_CHOICES, verbose_name='Novo Status')
    description = models.TextField(blank=True, null=True, verbose_name='Descrição')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data da Mudança')
    created_by = models.CharField(max_length=100, blank=True, null=True, verbose_name='Criado por')

    def __str__(self):
        return f"{self.event.title} - {self.get_new_status_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = 'Histórico de Status'
        verbose_name_plural = 'Históricos de Status'
        ordering = ['-created_at']


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.ForeignKey(Funcao, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Função')
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Valor')
    observations = models.TextField(blank=True, null=True, verbose_name='Observações')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.name} - {self.event.title}"

    class Meta:
        verbose_name = 'Participante de Evento'
        verbose_name_plural = 'Participantes de Eventos'
        unique_together = ('event', 'person')
