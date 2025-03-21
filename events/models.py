from django.db import models
from clients.models import Client
from people.models import Person

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
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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
