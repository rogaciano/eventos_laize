from django.contrib import admin
from .models import Occurrence

# Register your models here.

@admin.register(Occurrence)
class OccurrenceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date', 'related_to', 'status')
    list_filter = ('status', 'related_to', 'date')
    search_fields = ('description', 'client__name', 'person__name')
    date_hierarchy = 'date'
    
    def get_fields(self, request, obj=None):
        fields = ['related_to', 'description', 'status']
        if obj and obj.related_to == 'client':
            fields.insert(1, 'client')
        elif obj and obj.related_to == 'person':
            fields.insert(1, 'person')
        elif not obj:  # It's a new object
            fields.insert(1, 'client')
            fields.insert(2, 'person')
        return fields
