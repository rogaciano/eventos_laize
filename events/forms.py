from django import forms
from .models import Event, EventType, EventParticipant, Funcao, EventStatusHistory, EventGallery
from .models_cost import EventCost, CostCategory

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

class EventGalleryForm(forms.ModelForm):
    class Meta:
        model = EventGallery
        fields = ['image', 'title', 'description', 'is_primary', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'title': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'order': forms.NumberInput(attrs={'min': 0, 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
        }

class EventCostForm(forms.ModelForm):
    class Meta:
        model = EventCost
        fields = ['category', 'description', 'amount', 'cost_type', 'date', 'paid', 'receipt', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
        }
