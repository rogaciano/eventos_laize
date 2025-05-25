from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseBadRequest
from .models import Service, Testimonial, Post, SiteSettings, Message
from .forms import ContactForm, RegistrationForm, PostForm
from django.db.models import Q
from django.core.paginator import Paginator
from people.models import Person, PersonContact, ProfessionalCategory
from notifications.whatsapp import WhatsAppManager
from notifications.evolution_whatsapp import EvolutionWhatsAppService
# Importamos o módulo, mas não o usaremos
# from .recaptcha import verify_recaptcha
import logging

logger = logging.getLogger(__name__)

def get_site_settings():
    """Retorna as configurações do site ou cria um padrão se não existir"""
    settings, created = SiteSettings.objects.get_or_create(pk=1)
    return settings

# Outras funções da view permanecem iguais...

def contact(request):
    """View para a página de Contato"""
    site_settings = get_site_settings()
    form_sent = False
    form_error = False
    recaptcha_error = False
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Desabilitamos a verificação do reCAPTCHA
            # recaptcha_token = form.cleaned_data.get('recaptcha_token')
            # success, score, error = verify_recaptcha(recaptcha_token)
            success = True  # Assumimos sucesso sem verificar
            
            if success:
                # Salvar mensagem no banco de dados
                try:
                    message = Message.objects.create(
                        name=form.cleaned_data['name'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                        subject=form.cleaned_data['subject'],
                        message=form.cleaned_data['message']
                    )
                    form_sent = True
                    form = ContactForm()  # Limpar o formulário
                    
                    # Enviar notificação WhatsApp para o gestor usando o novo serviço Evolution
                    try:
                        evolution_service = EvolutionWhatsAppService()
                        evolution_service.notify_new_contact(message)
                    except Exception as e:
                        logger.error(f"Erro ao enviar notificação WhatsApp (Evolution): {e}")
                        
                except Exception as e:
                    logger.error(f"Erro ao salvar mensagem de contato: {e}")
                    form_error = True
            else:
                # Falha na verificação do reCAPTCHA (nunca chegará aqui com a modificação)
                logger.warning(f"reCAPTCHA verification failed: Desabilitado")
                recaptcha_error = True
                form_error = True
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'site_settings': site_settings,
        'form_sent': form_sent,
        'form_error': form_error,
        'recaptcha_error': recaptcha_error,
        'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY
    }
    return render(request, 'landing/contact.html', context)

def register(request):
    """View para a página de cadastro de pessoas"""
    site_settings = get_site_settings()
    form_sent = False
    form_error = False
    recaptcha_error = False
    
    # Obter categorias profissionais para o formulário
    professional_categories = ProfessionalCategory.objects.all()
    
    if request.method == 'POST':
        # Converter vírgula para ponto no campo altura
        post_data = request.POST.copy()
        if 'altura' in post_data and post_data['altura']:
            post_data['altura'] = post_data['altura'].replace(',', '.')
            
        form = RegistrationForm(post_data, request.FILES)
        if form.is_valid():
            # Desabilitamos a verificação do reCAPTCHA
            # recaptcha_token = form.cleaned_data.get('recaptcha_token')
            # success, score, error = verify_recaptcha(recaptcha_token)
            success = True  # Assumimos sucesso sem verificar
            
            if success:
                try:
                    # Salvar pessoa com status pendente
                    person = form.save(commit=False)
                    person.status = 'pendente'
                    person.origem_cadastro = 'externo'
                    person.save()
                    
                    # Salvar categorias profissionais
                    form.save_m2m()
                    
                    # Adicionar contatos
                    if form.cleaned_data['contact_email']:
                        PersonContact.objects.create(
                            person=person,
                            type='email',
                            value=form.cleaned_data['contact_email'],
                            label='Principal'
                        )
                    
                    if form.cleaned_data['contact_phone']:
                        PersonContact.objects.create(
                            person=person,
                            type='whatsapp',
                            value=form.cleaned_data['contact_phone'],
                            label='Principal'
                        )
                    
                    form_sent = True
                    form = RegistrationForm()  # Limpar o formulário
                    
                    # Enviar notificação WhatsApp para o gestor usando o novo serviço Evolution
                    try:
                        evolution_service = EvolutionWhatsAppService()
                        evolution_service.notify_new_registration(person)
                    except Exception as e:
                        logger.error(f"Erro ao enviar notificação WhatsApp (Evolution): {e}")
                    
                except Exception as e:
                    form_error = True
                    logger.error(f"Erro ao salvar registro: {e}")
            else:
                # Falha na verificação do reCAPTCHA (nunca chegará aqui com a modificação)
                logger.warning(f"reCAPTCHA verification failed on registration: Desabilitado")
                recaptcha_error = True
                form_error = True
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
        'site_settings': site_settings,
        'form_sent': form_sent,
        'form_error': form_error,
        'recaptcha_error': recaptcha_error,
        'professional_categories': professional_categories,
        'title': 'Cadastre-se',
        'subtitle': 'Faça parte do nosso time de profissionais',
        'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY
    }
    return render(request, 'landing/register.html', context)

# Outras funções da view permanecem iguais...
