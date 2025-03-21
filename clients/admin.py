from django.contrib import admin
from .models import Client, ClientClass, Contact

# Register your models here.

class ContactInline(admin.TabularInline):
    model = Client.contacts.through
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_class', 'created_at')
    list_filter = ('client_class', 'created_at')
    search_fields = ('name',)
    inlines = [ContactInline]
    exclude = ('contacts',)

@admin.register(ClientClass)
class ClientClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('type', 'value', 'label')
    list_filter = ('type',)
    search_fields = ('value', 'label')
