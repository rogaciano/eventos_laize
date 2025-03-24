from django import forms
from .models import Client, ClientClass, Contact

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'client_class', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ClientClassForm(forms.ModelForm):
    class Meta:
        model = ClientClass
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 h-24 bg-white'
            }),
        }

class ContactForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=[
            ('whatsapp', 'WhatsApp'),
            ('email', 'Email'),
            ('instagram', 'Instagram'),
            ('other', 'Outro')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Contact
        fields = ['type', 'value', 'label']
        widgets = {
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valor do contato'}),
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição (ex: Pessoal, Trabalho)'}),
        }
