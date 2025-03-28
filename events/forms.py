from django import forms
from .models import Event, EventType, EventParticipant, Funcao, EventStatusHistory, EventGallery
from .models_cost import EventCost, CostCategory
from .models_budget import EventBudgetItem, BudgetSettings, DefaultBudgetSettings
from .models_company import CompanySettings

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

class EventBudgetItemForm(forms.ModelForm):
    """Formulário para itens de orçamento de eventos"""
    class Meta:
        model = EventBudgetItem
        fields = ['code', 'description', 'date', 'start_time', 'end_time', 'quantity', 'unit_value']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'description': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'type': 'time'}),
            'quantity': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': 1}),
            'unit_value': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': 0, 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Garantir que a data seja formatada corretamente para o campo de data HTML5
        if self.instance and self.instance.pk and 'date' in self.initial:
            self.initial['date'] = self.instance.date.strftime('%Y-%m-%d')

class BudgetSettingsForm(forms.ModelForm):
    """Formulário para configurações de orçamento"""
    class Meta:
        model = BudgetSettings
        fields = ['payment_terms', 'validity_days', 'client_responsibilities', 'additional_notes']
        widgets = {
            'payment_terms': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
            'validity_days': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'min': 1}),
            'client_responsibilities': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
            'additional_notes': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
        }

class DefaultBudgetSettingsForm(forms.ModelForm):
    """Formulário para configurações padrão de orçamentos"""
    class Meta:
        model = DefaultBudgetSettings
        fields = ['payment_terms', 'validity_days', 'client_responsibilities', 'additional_notes']
        widgets = {
            'payment_terms': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
            'validity_days': forms.NumberInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'client_responsibilities': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
            'additional_notes': forms.Textarea(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md', 'rows': 3}),
        }

class CompanySettingsForm(forms.ModelForm):
    """Formulário para configurações da empresa"""
    class Meta:
        model = CompanySettings
        fields = ['name', 'address', 'phone', 'email', 'cnpj', 'logo', 'signature_name', 'signature_title']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'address': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'phone': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'email': forms.EmailInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'cnpj': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'signature_name': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'signature_title': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
        }
