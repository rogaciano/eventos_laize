from django.contrib import admin
from .models import Service, Testimonial, Post, SiteSettings, Message

# Register your models here.

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title', 'description')
    ordering = ('order',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name', 'position', 'content')
    ordering = ('-created_at',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'read_at')
    ordering = ('-created_at',)
    list_editable = ('is_read',)
    
    def has_add_permission(self, request):
        # Messages should only be created through the contact form
        return False

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('site_name', 'tagline', 'footer_text')
        }),
        ('Seções', {
            'fields': ('about_title', 'about_content', 'services_title', 'blog_title', 'contact_title')
        }),
        ('Contato', {
            'fields': ('contact_email', 'phone', 'address')
        }),
        ('Redes Sociais', {
            'fields': ('facebook', 'instagram', 'whatsapp')
        }),
    )
    
    def has_add_permission(self, request):
        # Limitar a apenas uma instância
        return SiteSettings.objects.count() == 0
