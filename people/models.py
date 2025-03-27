from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date

# Create your models here.

class CorOlhos(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Cor de Olhos'
        verbose_name_plural = 'Cores de Olhos'
        ordering = ['nome']


class CorCabelo(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Cor de Cabelo'
        verbose_name_plural = 'Cores de Cabelo'
        ordering = ['nome']


class CorPele(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Cor de Pele'
        verbose_name_plural = 'Cores de Pele'
        ordering = ['nome']


class Genero(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Gênero'
        verbose_name_plural = 'Gêneros'
        ordering = ['nome']


class ProfessionalCategory(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Categoria Profissional'
        verbose_name_plural = 'Categorias Profissionais'
        ordering = ['nome']


class Person(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('pendente', 'Pendente'),
        ('bloqueado', 'Bloqueado'),
        ('em_avaliacao', 'Em Avaliação'),
        ('licenca_temporaria', 'Licença Temporária'),
        ('arquivado', 'Arquivado'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Nome")
    document_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="Documento (CPF/RG)")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Nascimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Situação")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    address_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    address_complement = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    neighborhood = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    state = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    zipcode = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    pix = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chave Pix")
    photo = models.ImageField(upload_to='people_photos/', blank=True, null=True, verbose_name="Foto")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Categorias profissionais
    professional_categories = models.ManyToManyField(ProfessionalCategory, blank=True, verbose_name="Categorias Profissionais")
    
    # Características físicas
    altura = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, verbose_name="Altura (m)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Peso (kg)")
    manequim = models.CharField(max_length=10, blank=True, null=True, verbose_name="Manequim")
    cor_olhos = models.ForeignKey(CorOlhos, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Cor dos olhos")
    cor_cabelo = models.ForeignKey(CorCabelo, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Cor do cabelo")
    cor_pele = models.ForeignKey(CorPele, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Cor da pele")
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Gênero")
    
    # Avaliações
    efficiency = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name="Eficiência"
    )
    punctuality = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name="Pontualidade"
    )
    proactivity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name="Proatividade"
    )
    appearance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name="Aparência"
    )
    communication = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name="Comunicação"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def average_rating(self):
        fields = ['efficiency', 'punctuality', 'proactivity', 'appearance', 'communication']
        values = [getattr(self, field) for field in fields if getattr(self, field) is not None]
        
        if not values:
            return None
        
        return sum(values) / len(values)
    
    def get_average_rating(self):
        avg = self.average_rating()
        if avg is None:
            return "Não avaliado"
        return f"{avg:.1f}"
    
    def idade(self):
        if not self.data_nascimento:
            return None
        
        hoje = date.today()
        idade = hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return idade
    
    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        ordering = ['name']


class PersonContact(models.Model):
    CONTACT_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('instagram', 'Instagram'),
        ('outro', 'Outro')
    ]
    
    person = models.ForeignKey(Person, related_name='contacts', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=CONTACT_TYPES, verbose_name="Tipo")
    value = models.CharField(max_length=255, verbose_name="Valor")
    label = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: Pessoal, Trabalho, etc.", verbose_name="Rótulo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.person.name} - {self.get_type_display()}: {self.value}"
    
    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['person__name', 'type']


class WhatsAppMessage(models.Model):
    person = models.ForeignKey(Person, related_name='whatsapp_messages', on_delete=models.CASCADE)
    contact = models.ForeignKey(PersonContact, related_name='whatsapp_messages', on_delete=models.CASCADE)
    message = models.TextField(verbose_name="Mensagem")
    status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Status")
    response_data = models.JSONField(blank=True, null=True, verbose_name="Dados da resposta")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado em")
    
    def __str__(self):
        return f"Mensagem para {self.person.name} em {self.sent_at.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = 'Mensagem WhatsApp'
        verbose_name_plural = 'Mensagens WhatsApp'
        ordering = ['-sent_at']
