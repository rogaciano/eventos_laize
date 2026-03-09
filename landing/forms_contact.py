from django import forms
from .models import Message
from .math_captcha import MathCaptchaField

class SimpleContactForm(forms.Form):
    """Formulário de contato com CAPTCHA matemático e proteções anti-bot."""
    
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
    
    # Campo de CAPTCHA matemático
    math_captcha = MathCaptchaField(
        label='Verificação de segurança',
        help_text='Por favor, resolva esta operação matemática simples.',
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 border-2 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50 bg-white text-black',
            'placeholder': 'Digite a resposta'
        })
    )
    
    # ── Anti-bot: Campo honeypot ──────────────────────────────────────────────
    # Humanos não vêem este campo (escondido por CSS no template).
    # Bots preenchem todos os campos automaticamente — se vier preenchido = bot.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'off',
        })
    )
    
    # ── Anti-bot: Timestamp de carregamento ───────────────────────────────────
    # O JavaScript preenche este campo com o horário Unix que a página abriu.
    # Submissões em menos de 3 segundos são bloqueadas (bots são instantâneos).
    form_load_time = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
