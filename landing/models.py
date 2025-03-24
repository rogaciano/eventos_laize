from django.db import models
from django.utils import timezone

# Create your models here.

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Nome da classe do ícone FontAwesome (ex: fa-calendar)")
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Depoimento de {self.name}"

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-published_at']

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Agência Atitude")
    tagline = models.CharField(max_length=200, blank=True)
    about_title = models.CharField(max_length=100, default="Sobre Nós")
    about_content = models.TextField(blank=True)
    services_title = models.CharField(max_length=100, default="Nossos Serviços")
    blog_title = models.CharField(max_length=100, default="Novidades")
    contact_title = models.CharField(max_length=100, default="Entre em Contato")
    contact_email = models.EmailField(default="contato@exemplo.com")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    footer_text = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.site_name
    
    class Meta:
        verbose_name = "Configurações do Site"
        verbose_name_plural = "Configurações do Site"
