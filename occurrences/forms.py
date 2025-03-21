from django import forms
from .models import Occurrence
from clients.models import Client
from people.models import Person

class OccurrenceForm(forms.ModelForm):
    class Meta:
        model = Occurrence
        fields = ['related_to', 'client', 'person', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Set initial values for fields
        if self.instance.pk:
            if self.instance.related_to == 'client':
                self.fields['person'].required = False
                self.fields['person'].widget.attrs['disabled'] = 'disabled'
            elif self.instance.related_to == 'person':
                self.fields['client'].required = False
                self.fields['client'].widget.attrs['disabled'] = 'disabled'
    
    def clean(self):
        cleaned_data = super().clean()
        related_to = cleaned_data.get('related_to')
        client = cleaned_data.get('client')
        person = cleaned_data.get('person')
        
        if related_to == 'client' and not client:
            self.add_error('client', 'Este campo é obrigatório quando "Relacionado a" é Cliente.')
        
        if related_to == 'person' and not person:
            self.add_error('person', 'Este campo é obrigatório quando "Relacionado a" é Pessoa.')
        
        return cleaned_data
