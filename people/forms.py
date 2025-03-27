from django import forms
from .models import Person, PersonContact, CorOlhos, CorCabelo, CorPele, Genero, ProfessionalCategory, PersonGallery

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'name', 'document_id', 'data_nascimento', 'photo',
            'status', 'professional_categories',
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
            'status': forms.Select(attrs={'class': 'bg-white text-gray-900'}),
            'professional_categories': forms.SelectMultiple(attrs={
                'class': 'select2-categories bg-white text-gray-900',
                'data-placeholder': 'Digite para buscar ou adicionar categorias'
            }),
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

class ProfessionalCategoryForm(forms.ModelForm):
    class Meta:
        model = ProfessionalCategory
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
        }

class PersonGalleryForm(forms.ModelForm):
    class Meta:
        model = PersonGallery
        fields = ['image', 'title', 'description', 'is_primary', 'order']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'title': forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
            'order': forms.NumberInput(attrs={'min': 0, 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'}),
        }
