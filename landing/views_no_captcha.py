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

def register(request):
    """View para a página de cadastro de pessoas"""
    site_settings = get_site_settings()
    form_sent = False
    form_error = False
    recaptcha_error = False
    
    # Obter categorias profissionais para o formulário
    professional_categories = ProfessionalCategory.objects.all()
    
    if request.method == 'POST':
        # Log para depuração
        logger.info(f"Recebido POST para cadastro: {request.POST.keys()}")
        logger.info(f"FILES recebidos: {request.FILES.keys() if request.FILES else 'Nenhum'}")
        
        # Converter vírgula para ponto no campo altura
        post_data = request.POST.copy()
        if 'altura' in post_data and post_data['altura']:
            post_data['altura'] = post_data['altura'].replace(',', '.')
            
        form = RegistrationForm(post_data, request.FILES)
        if form.is_valid():
            logger.info("Formulário válido, processando cadastro...")
        else:
            logger.error(f"Erros no formulário: {form.errors}")
            
        if form.is_valid():
            # Desabilitamos a verificação do reCAPTCHA
            # recaptcha_token = form.cleaned_data.get('recaptcha_token')
            # success, score, error = verify_recaptcha(recaptcha_token)
            success = True  # Assumimos sucesso sem verificar
            error = None
            
            if success:
                try:
                    logger.info("Iniciando salvamento da pessoa...")
                    # Salvar pessoa com status pendente
                    person = form.save(commit=False)
                    person.status = 'pendente'
                    person.origem_cadastro = 'externo'
                    logger.info(f"Salvando pessoa: {person.name}")
                    person.save()
                    logger.info(f"Pessoa salva com ID: {person.id}")
                    
                    # Salvar categorias profissionais
                    logger.info("Salvando categorias profissionais...")
                    form.save_m2m()
                    logger.info("Categorias profissionais salvas com sucesso")
                    
                    # Adicionar contatos
                    logger.info("Adicionando contatos...")
                    if form.cleaned_data['contact_email']:
                        logger.info(f"Adicionando email: {form.cleaned_data['contact_email']}")
                        PersonContact.objects.create(
                            person=person,
                            type='email',
                            value=form.cleaned_data['contact_email'],
                            label='Principal'
                        )
                        logger.info("Email adicionado com sucesso")
                    
                    if form.cleaned_data['contact_phone']:
                        logger.info(f"Adicionando telefone: {form.cleaned_data['contact_phone']}")
                        PersonContact.objects.create(
                            person=person,
                            type='whatsapp',
                            value=form.cleaned_data['contact_phone'],
                            label='Principal'
                        )
                        logger.info("Telefone adicionado com sucesso")
                    
                    logger.info("Definindo form_sent = True e limpando o formulário")
                    form_sent = True
                    form = RegistrationForm()  # Limpar o formulário
                    logger.info("Cadastro concluído com sucesso!")
                    
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
                logger.warning(f"reCAPTCHA verification failed on registration: {error}")
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
    
    # Log do contexto para depuração
    logger.info(f"Contexto passado para o template: form_sent={form_sent}, form_error={form_error}, recaptcha_error={recaptcha_error}")
    
    return render(request, 'landing/register.html', context)
