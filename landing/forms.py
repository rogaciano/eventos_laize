from django import forms
from .models import Service, Testimonial, Post, SiteSettings, Message
from people.models import Person, ProfessionalCategory, CorOlhos, CorCabelo, CorPele, Genero

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
            'placeholder': 'Seu nome'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
            'placeholder': 'Seu e-mail'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
            'placeholder': 'Seu telefone'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
            'placeholder': 'Assunto'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 h-32 bg-white text-black',
            'placeholder': 'Sua mensagem',
            'rows': 5
        })
    )

class RegistrationForm(forms.ModelForm):
    """Form for user registration on the landing page."""
    
    class Meta:
        model = Person
        fields = [
            'name', 'photo',
            'professional_categories',
            'address', 'address_number', 'address_complement', 
            'neighborhood', 'city', 'state', 'zipcode',
            'altura', 'peso', 'manequim', 'cor_olhos', 'cor_cabelo', 'cor_pele', 'genero',
            'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Seu nome completo'
            }),
            'address': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Logradouro'
            }),
            'address_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Número'
            }),
            'address_complement': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Complemento'
            }),
            'neighborhood': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Bairro'
            }),
            'city': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Cidade'
            }),
            'state': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Estado (UF)'
            }),
            'zipcode': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'CEP'
            }),
            'altura': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Ex: 1,75'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'step': '0.01', 
                'min': '0',
                'placeholder': 'Ex: 65.5'
            }),
            'manequim': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'placeholder': 'Ex: M, 42, etc.'
            }),
            'cor_olhos': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black'
            }),
            'cor_cabelo': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black'
            }),
            'cor_pele': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black'
            }),
            'genero': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black'
            }),
            'professional_categories': forms.SelectMultiple(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
                'data-placeholder': 'Selecione suas categorias profissionais'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 h-32 bg-white text-black',
                'placeholder': 'Observações adicionais, experiências, habilidades, etc.',
                'rows': 5
            }),
        }
    
    # Field for contact information
    contact_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
            'placeholder': 'Seu e-mail para contato'
        })
    )
    
    contact_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
            'placeholder': 'Seu telefone/WhatsApp'
        })
    )

class PostForm(forms.ModelForm):
    """Formulário para gerenciamento de posts do blog."""
    
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'image', 'is_published', 'published_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white',
                'placeholder': 'Título do post'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white',
                'placeholder': 'slug-do-post'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white',
                'placeholder': 'Conteúdo do post',
                'rows': 10
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-600 text-indigo-600 focus:ring-indigo-500'
            }),
            'published_at': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white',
                'type': 'datetime-local'
            }),
        }
