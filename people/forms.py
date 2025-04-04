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

class PersonFilterForm(forms.Form):
    """
    Formulário para filtrar pessoas no catálogo de casting
    """
    name = forms.CharField(
        required=False, 
        label="Nome",
        widget=forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_height = forms.DecimalField(
        required=False, 
        label="Altura Mínima (m)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    max_height = forms.DecimalField(
        required=False, 
        label="Altura Máxima (m)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_weight = forms.DecimalField(
        required=False, 
        label="Peso Mínimo (kg)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    max_weight = forms.DecimalField(
        required=False, 
        label="Peso Máximo (kg)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_age = forms.IntegerField(
        required=False, 
        label="Idade Mínima",
        widget=forms.NumberInput(attrs={'min': '0', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    max_age = forms.IntegerField(
        required=False, 
        label="Idade Máxima",
        widget=forms.NumberInput(attrs={'min': '0', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    manequim = forms.CharField(
        required=False, 
        label="Manequim",
        widget=forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    eye_colors = forms.ModelMultipleChoiceField(
        queryset=CorOlhos.objects.all(),
        required=False,
        label="Cores de Olhos",
        widget=forms.SelectMultiple(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    hair_colors = forms.ModelMultipleChoiceField(
        queryset=CorCabelo.objects.all(),
        required=False,
        label="Cores de Cabelo",
        widget=forms.SelectMultiple(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    skin_colors = forms.ModelMultipleChoiceField(
        queryset=CorPele.objects.all(),
        required=False,
        label="Cores de Pele",
        widget=forms.SelectMultiple(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    genders = forms.ModelMultipleChoiceField(
        queryset=Genero.objects.all(),
        required=False,
        label="Gêneros",
        widget=forms.SelectMultiple(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    professional_categories = forms.ModelMultipleChoiceField(
        queryset=ProfessionalCategory.objects.all(),
        required=False,
        label="Categorias Profissionais",
        widget=forms.SelectMultiple(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_efficiency = forms.IntegerField(
        required=False, 
        label="Eficiência Mínima",
        widget=forms.NumberInput(attrs={'min': '1', 'max': '5', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_punctuality = forms.IntegerField(
        required=False, 
        label="Pontualidade Mínima",
        widget=forms.NumberInput(attrs={'min': '1', 'max': '5', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_proactivity = forms.IntegerField(
        required=False, 
        label="Proatividade Mínima",
        widget=forms.NumberInput(attrs={'min': '1', 'max': '5', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_appearance = forms.IntegerField(
        required=False, 
        label="Aparência Mínima",
        widget=forms.NumberInput(attrs={'min': '1', 'max': '5', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    min_communication = forms.IntegerField(
        required=False, 
        label="Comunicação Mínima",
        widget=forms.NumberInput(attrs={'min': '1', 'max': '5', 'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    cities = forms.CharField(
        required=False, 
        label="Cidades (separadas por vírgula)",
        widget=forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    states = forms.CharField(
        required=False, 
        label="Estados (separados por vírgula)",
        widget=forms.TextInput(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
    
    status_choices = forms.MultipleChoiceField(
        choices=Person.STATUS_CHOICES,
        required=False,
        label="Status",
        widget=forms.SelectMultiple(attrs={'class': 'shadow-sm focus:ring-black focus:border-black block w-full sm:text-sm border-gray-300 rounded-md bg-white text-gray-900'})
    )
