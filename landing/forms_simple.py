import os
from django import forms
from people.models import Person, ProfessionalCategory, CorOlhos, CorCabelo, CorPele, Genero
from .math_captcha import MathCaptchaField

class SimpleRegistrationForm(forms.ModelForm):
    """Formulário simplificado para cadastro de pessoas, com CAPTCHA matemático."""
    
    # Campos adicionais que não estão no modelo
    contact_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'bg-gray-700 text-white p-2 rounded-lg w-full',
            'placeholder': 'Email para contato'
        })
    )
    
    contact_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-700 text-white p-2 rounded-lg w-full',
            'placeholder': 'Telefone/WhatsApp para contato'
        })
    )
    
    # Campo de CAPTCHA matemático
    math_captcha = MathCaptchaField(
        label='Verificação de segurança',
        help_text='Por favor, resolva esta operação matemática simples.',
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-700 text-white p-2 rounded-lg w-full',
            'placeholder': 'Digite a resposta'
        })
    )
    
    def clean_photo(self):
        """Validar o campo de foto para garantir que seja uma imagem válida"""
        photo = self.cleaned_data.get('photo')
        
        if photo:
            # Verificar o tamanho do arquivo (máximo de 5MB)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    'O tamanho máximo permitido para a foto é de 5MB.'
                )
            
            # Verificar a extensão do arquivo
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(photo.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    'Por favor, envie uma imagem válida. '
                    'Os formatos suportados são: JPG, JPEG, PNG e GIF.'
                )
                
        return photo
    
    class Meta:
        model = Person
        fields = [
            'name', 'photo',
            'professional_categories',
            'address', 'address_number', 'address_complement', 
            'neighborhood', 'city', 'state', 'zipcode',
            'altura', 'peso', 'manequim', 'cor_olhos', 'cor_cabelo', 'cor_pele', 'genero',
            'data_nascimento', 'document_id', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Nome completo'}),
            'photo': forms.FileInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full'}),
            'professional_categories': forms.SelectMultiple(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full'}),
            'address': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Endereço'}),
            'address_number': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Número'}),
            'address_complement': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Complemento'}),
            'neighborhood': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Bairro'}),
            'city': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Cidade'}),
            'state': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'UF'}),
            'zipcode': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'CEP'}),
            'altura': forms.NumberInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Altura (m)', 'step': '0.01'}),
            'peso': forms.NumberInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Peso (kg)', 'step': '0.1'}),
            'manequim': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'Manequim'}),
            'cor_olhos': forms.Select(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full'}),
            'cor_cabelo': forms.Select(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full'}),
            'cor_pele': forms.Select(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full'}),
            'genero': forms.Select(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'type': 'date'}),
            'document_id': forms.TextInput(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'placeholder': 'CPF ou RG'}),
            'notes': forms.Textarea(attrs={'class': 'bg-gray-700 text-white p-2 rounded-lg w-full', 'rows': 4, 'placeholder': 'Observações adicionais'}),
        }
