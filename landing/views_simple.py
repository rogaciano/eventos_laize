from django.shortcuts import render, redirect
from django.conf import settings
import logging
from .forms_simple import SimpleRegistrationForm
from people.models import Person, PersonContact, ProfessionalCategory
from .models import SiteSettings
from notifications.evolution_whatsapp import EvolutionWhatsAppService

logger = logging.getLogger(__name__)

def get_site_settings():
    """Retorna as configurações do site ou cria um padrão se não existir"""
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj

def simple_register(request):
    """
    Versão simplificada da view de registro sem reCAPTCHA
    para identificar e resolver problemas de cadastro
    """
    site_settings = get_site_settings()
    form_sent = False
    form_error = False
    
    # Obter categorias profissionais para o formulário
    professional_categories = ProfessionalCategory.objects.all()
    
    if request.method == 'POST':
        logger.info(f"Recebido POST para cadastro simples: {request.POST.keys()}")
        logger.info(f"FILES recebidos: {request.FILES.keys() if request.FILES else 'Nenhum'}")
        
        # Converter vírgula para ponto no campo altura
        post_data = request.POST.copy()
        if 'altura' in post_data and post_data['altura']:
            post_data['altura'] = post_data['altura'].replace(',', '.')
            
        # Criar o formulário com os dados do POST
        form = SimpleRegistrationForm(post_data, request.FILES)
        
        # Adicionar a requisição ao widget para acessar a sessão
        form.fields['math_captcha'].widget.attrs['request'] = request
        
        # Verificar se o formulário é válido
        if form.is_valid():
            logger.info("Formulário válido, processando cadastro...")
            
            try:
                # Salvar pessoa com status pendente
                logger.info("Iniciando salvamento da pessoa...")
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
                if form.cleaned_data.get('contact_email'):
                    logger.info(f"Adicionando email: {form.cleaned_data['contact_email']}")
                    PersonContact.objects.create(
                        person=person,
                        type='email',
                        value=form.cleaned_data['contact_email'],
                        label='Principal'
                    )
                    logger.info("Email adicionado com sucesso")
                
                if form.cleaned_data.get('contact_phone'):
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
                form = SimpleRegistrationForm()  # Limpar o formulário
                logger.info("Cadastro concluído com sucesso!")
                
                # Enviar notificação WhatsApp para o gestor
                try:
                    evolution_service = EvolutionWhatsAppService()
                    evolution_service.notify_new_registration(person)
                except Exception as e:
                    logger.error(f"Erro ao enviar notificação WhatsApp (Evolution): {e}")
                
            except Exception as e:
                form_error = True
                logger.error(f"Erro ao salvar registro: {e}", exc_info=True)
        else:
            logger.error(f"Erros no formulário: {form.errors}")
    else:
        form = SimpleRegistrationForm()
        # Adicionar a requisição ao widget para acessar a sessão
        form.fields['math_captcha'].widget.attrs['request'] = request
        # Gerar a pergunta matemática
        math_question = form.fields['math_captcha'].get_math_question(request)
    
    # Sempre gerar uma nova pergunta matemática, independentemente do método
    # Isso garante que a pergunta seja exibida mesmo após um erro
    math_question = form.fields['math_captcha'].get_math_question(request)
    
    context = {
        'form': form,
        'site_settings': site_settings,
        'form_sent': form_sent,
        'form_error': form_error,
        'professional_categories': professional_categories,
        'title': 'Cadastre-se',
        'subtitle': 'Faça parte do nosso time de profissionais',
        'math_question': math_question
    }
    
    # Log do contexto para depuração
    logger.info(f"Contexto passado para o template: form_sent={form_sent}, form_error={form_error}")
    
    return render(request, 'landing/register_simple.html', context)
