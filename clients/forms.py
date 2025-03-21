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
        fields = ['name']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['type', 'value', 'label']
