from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date

# Create your models here.

# Remove the import of CastingCatalog to break the circular dependency
from .models_casting import CastingCatalog

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
    
    ORIGEM_CHOICES = [
        ('interno', 'Interno (Escritório)'),
        ('externo', 'Externo (Site)'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Nome")
    document_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="Documento (CPF/RG)")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Nascimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Situação")
    origem_cadastro = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='interno', verbose_name="Origem do Cadastro")
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


class PersonGallery(models.Model):
    """Model to store additional photos for a person's gallery"""
    person = models.ForeignKey(Person, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='people_gallery/', verbose_name="Imagem")
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="Título")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    is_primary = models.BooleanField(default=False, verbose_name="Imagem Principal")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Foto de {self.person.name} - {self.title or 'Sem título'}"
    
    def save(self, *args, **kwargs):
        # If this image is set as primary, unset all other primary images for this person
        if self.is_primary:
            PersonGallery.objects.filter(person=self.person, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Foto da Galeria'
        verbose_name_plural = 'Fotos da Galeria'
        ordering = ['person__name', 'order', 'created_at']


class PersonView(models.Model):
    """
    Modelo para rastrear visualizações de perfis de pessoas.
    Registra quem visualizou, quando e quantas vezes.
    """
    person = models.ForeignKey(Person, related_name='views', on_delete=models.CASCADE, verbose_name="Pessoa")
    catalog = models.ForeignKey(CastingCatalog, related_name='views', on_delete=models.CASCADE, 
                               verbose_name="Catálogo", null=True, blank=True)
    user = models.ForeignKey('auth.User', related_name='person_views', on_delete=models.SET_NULL, 
                            null=True, blank=True, verbose_name="Usuário")
    ip_address = models.CharField(max_length=50, blank=True, null=True, verbose_name="Endereço IP")
    session_key = models.CharField(max_length=40, blank=True, null=True, verbose_name="Chave de Sessão")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    
    class Meta:
        verbose_name = 'Visualização de Perfil'
        verbose_name_plural = 'Visualizações de Perfis'
        ordering = ['-timestamp']
        
    def __str__(self):
        user_info = self.user.username if self.user else f"Anônimo ({self.ip_address})"
        catalog_info = f" no catálogo {self.catalog.name}" if self.catalog else ""
        return f"{self.person.name} visualizado por {user_info}{catalog_info} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


class PersonComment(models.Model):
    """
    Modelo para comentários e perguntas sobre pessoas.
    Permite que usuários deixem comentários ou façam perguntas sobre perfis.
    """
    person = models.ForeignKey(Person, related_name='comments', on_delete=models.CASCADE, verbose_name="Pessoa")
    catalog = models.ForeignKey(CastingCatalog, related_name='comments', on_delete=models.CASCADE, 
                               verbose_name="Catálogo", null=True, blank=True)
    user = models.ForeignKey('auth.User', related_name='person_comments', on_delete=models.SET_NULL,
                            null=True, blank=True, verbose_name="Usuário")
    comment_text = models.TextField(verbose_name="Comentário/Pergunta")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    is_question = models.BooleanField(default=False, verbose_name="É uma pergunta?")
    is_answered = models.BooleanField(default=False, verbose_name="Foi respondida?")
    answer_text = models.TextField(blank=True, null=True, verbose_name="Resposta")
    answered_at = models.DateTimeField(blank=True, null=True, verbose_name="Respondido em")
    
    class Meta:
        verbose_name = 'Comentário/Pergunta'
        verbose_name_plural = 'Comentários/Perguntas'
        ordering = ['-created_at']
        
    def __str__(self):
        tipo = "Pergunta" if self.is_question else "Comentário"
        user_info = self.user.username if self.user else "Anônimo"
        catalog_info = f" no catálogo {self.catalog.name}" if self.catalog else ""
        return f"{tipo} sobre {self.person.name}{catalog_info} por {user_info} em {self.created_at.strftime('%d/%m/%Y')}"


class PersonSelection(models.Model):
    """
    Modelo para armazenar pessoas selecionadas em um catálogo
    """
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='selections')
    catalog = models.ForeignKey('CastingCatalog', on_delete=models.CASCADE, related_name='selections')
    session_key = models.CharField(max_length=40, blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True, related_name='person_selections')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Seleção de Pessoa'
        verbose_name_plural = 'Seleções de Pessoas'
        unique_together = [('person', 'catalog', 'session_key')]
        
    def __str__(self):
        return f"Seleção: {self.person.name} em {self.catalog.name}"
