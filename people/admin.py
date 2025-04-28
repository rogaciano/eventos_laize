from django.contrib import admin
from .models import Person, PersonContact, CorOlhos, CorCabelo, CorPele, Genero, PersonComment

# Register your models here.

class PersonContactInline(admin.TabularInline):
    model = PersonContact
    extra = 1

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'origem_cadastro', 'average_rating', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('origem_cadastro', 'created_at', 'genero', 'cor_olhos', 'cor_cabelo', 'cor_pele')
    inlines = [PersonContactInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'document_id', 'photo', 'status', 'origem_cadastro')
        }),
        ('Endereço', {
            'fields': ('address', 'address_number', 'address_complement', 'neighborhood', 'city', 'state', 'zipcode')
        }),
        ('Características Físicas', {
            'fields': ('altura', 'peso', 'cor_olhos', 'cor_cabelo', 'cor_pele', 'genero')
        }),
        ('Outros', {
            'fields': ('pix', 'notes')
        }),
        ('Avaliações', {
            'fields': ('efficiency', 'punctuality', 'proactivity', 'appearance', 'communication')
        }),
    )

@admin.register(PersonContact)
class PersonContactAdmin(admin.ModelAdmin):
    list_display = ('person', 'type', 'value', 'label')
    list_filter = ('type',)
    search_fields = ('value', 'person__name')

@admin.register(CorOlhos)
class CorOlhosAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(CorCabelo)
class CorCabeloAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(CorPele)
class CorPeleAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(PersonComment)
class PersonCommentAdmin(admin.ModelAdmin):
    list_display = ('person', 'user', 'comment_text', 'created_at', 'is_question', 'is_answered')
    list_filter = ('is_question', 'is_answered', 'created_at')
    search_fields = ('comment_text', 'person__name', 'user__username')
