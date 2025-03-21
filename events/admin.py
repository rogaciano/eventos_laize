from django.contrib import admin
from .models import Event, EventType, EventParticipant, Funcao

# Register your models here.

@admin.register(Funcao)
class FuncaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_padrao', 'created_at')
    search_fields = ('nome',)

class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_datetime', 'end_datetime', 'client', 'event_type', 'value')
    list_filter = ('event_type', 'client', 'start_datetime')
    search_fields = ('title', 'description', 'client__name')
    date_hierarchy = 'start_datetime'
    inlines = [EventParticipantInline]

@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'person')
    list_filter = ('event', 'person')
    search_fields = ('event__title', 'person__name', 'observations')
