from django import forms
from .models import Person, PersonContact, CorOlhos, CorCabelo, CorPele, Genero

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'name', 'document_id', 'data_nascimento', 'photo',
            'address', 'address_number', 'address_complement', 
            'neighborhood', 'city', 'state', 'zipcode',
            'altura', 'peso', 'manequim', 'cor_olhos', 'cor_cabelo', 'cor_pele', 'genero',
            'pix', 'notes', 
            'efficiency', 'punctuality', 'proactivity', 
            'appearance', 'communication'
        ]
        widgets = {
            'address': forms.TextInput(),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.FileInput(),
            'altura': forms.TextInput(attrs={'placeholder': 'Ex: 1,75'}),
            'peso': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'manequim': forms.TextInput(),
            'cor_olhos': forms.Select(attrs={'class': 'form-select'}),
            'cor_cabelo': forms.Select(attrs={'class': 'form-select'}),
            'cor_pele': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'efficiency': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'punctuality': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'proactivity': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'appearance': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'communication': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

class PersonContactForm(forms.ModelForm):
    class Meta:
        model = PersonContact
        fields = ['type', 'value', 'label']
