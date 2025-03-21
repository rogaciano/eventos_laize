from django import forms
from .models import Event, EventType, EventParticipant, Funcao, EventStatusHistory

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_datetime', 'end_datetime', 'client', 'value', 
                 'location', 'event_type', 'description']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ['name']

class EventParticipantForm(forms.ModelForm):
    class Meta:
        model = EventParticipant
        fields = ['person', 'role', 'value', 'observations']
        widgets = {
            'observations': forms.Textarea(attrs={'rows': 3}),
            'value': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

class FuncaoForm(forms.ModelForm):
    class Meta:
        model = Funcao
        fields = ['nome', 'valor_padrao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da função'}),
            'valor_padrao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor padrão em R$', 'step': '0.01', 'min': '0'}),
        }

class EventStatusHistoryForm(forms.ModelForm):
    class Meta:
        model = EventStatusHistory
        fields = ['new_status', 'description']
        widgets = {
            'new_status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descreva o motivo da mudança de status...'}),
        }
