from django.db import models
from clients.models import Client
from people.models import Person

# Create your models here.

class Occurrence(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('in_progress', 'Em Andamento'),
        ('resolved', 'Resolvido'),
        ('closed', 'Fechado')
    ]
    
    RELATED_TO_CHOICES = [
        ('client', 'Cliente'),
        ('person', 'Pessoa')
    ]
    
    date = models.DateTimeField(auto_now_add=True)
    related_to = models.CharField(max_length=10, choices=RELATED_TO_CHOICES)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='occurrences')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='occurrences')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.related_to == 'client' and self.client:
            return f"Ocorrência para cliente: {self.client.name}"
        elif self.related_to == 'person' and self.person:
            return f"Ocorrência para pessoa: {self.person.name}"
        else:
            return f"Ocorrência #{self.id}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.related_to == 'client' and not self.client:
            raise ValidationError("Client must be specified when related to is set to client")
        
        if self.related_to == 'person' and not self.person:
            raise ValidationError("Person must be specified when related to is set to person")
        
        super().clean()

    class Meta:
        verbose_name = 'Ocorrência'
        verbose_name_plural = 'Ocorrências'
        ordering = ['-date']
