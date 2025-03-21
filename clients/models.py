from django.db import models

# Create your models here.

class ClientClass(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Client Class'
        verbose_name_plural = 'Client Classes'


class Contact(models.Model):
    CONTACT_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('instagram', 'Instagram'),
        ('other', 'Other')
    ]
    
    type = models.CharField(max_length=20, choices=CONTACT_TYPES)
    value = models.CharField(max_length=255)
    label = models.CharField(max_length=100, blank=True, null=True, help_text="E.g. Personal, Work, etc.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_display()}: {self.value}"


class Client(models.Model):
    name = models.CharField(max_length=255)
    contacts = models.ManyToManyField(Contact, blank=True, related_name="client_contacts")
    client_class = models.ForeignKey(ClientClass, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['name']
