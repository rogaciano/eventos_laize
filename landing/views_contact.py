from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
import logging
import time

from .forms_contact import SimpleContactForm
from .models import Message, SiteSettings
from notifications.evolution_whatsapp import EvolutionWhatsAppService

logger = logging.getLogger(__name__)

# ── Lista de palavras típicas de spam (inglês/golpes) ────────────────────────
SPAM_KEYWORDS = [
    # Golpes financeiros / investimentos
    'they pay us', 'we pay you', 'earn money', 'make money', 'passive income',
    'bitcoin', 'crypto', 'investment opportunity', 'financial freedom',
    '$3,000', '$5,000', '$10,000', 'per month', 'monthly income',
    'work from home', 'no experience needed', 'click here', 'click now',
    # Spam de marketing / SEO
    'seo services', 'boost your website', 'increase traffic', 'google ranking',
    'website visibility', 'digital marketing agency', 'backlinks',
    'web traffic', 'search engine', 'rank higher',
    # Pharma / adulto
    'viagra', 'cialis', 'pharmacy', 'weight loss', 'diet pills',
    # Outros padrões comuns
    'dear friend', 'dear sir', 'dear madam', 'invitation to further',
    'business proposal', 'mutual benefit', 'confidential',
    'congratulations you have won', 'lottery', 'inheritance',
    'content to their website', 'done-for-you', 'ai find',
    'flips for you', 'tech headaches', 'product creation',
    'online effort', 'further discussion', 'exchange bureau',
]

# Tempo mínimo (em segundos) para preencher o formulário legitimamente
MIN_FILL_TIME = 3

# Rate limiting: max submissões por IP em uma janela de tempo
RATE_LIMIT_MAX = 3        # máximo de envios permitidos
RATE_LIMIT_WINDOW = 120   # segundos (2 minutos)


def get_site_settings():
    """Retorna as configurações do site ou cria um padrão se não existir"""
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj


def get_client_ip(request):
    """Obtém o IP real do cliente, considerando proxies reversos"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def is_rate_limited(ip):
    """
    Verifica e incrementa o contador de submissões por IP.
    Retorna True se o IP ultrapassou o limite.
    """
    cache_key = f'contact_form_rate_{ip}'
    count = cache.get(cache_key, 0)
    if count >= RATE_LIMIT_MAX:
        logger.warning(f"[SPAM] Rate limit atingido para IP: {ip} ({count} envios)")
        return True
    # Incrementa o contador (mantém o TTL existente se já existir)
    cache.set(cache_key, count + 1, RATE_LIMIT_WINDOW)
    return False


def contains_spam(text):
    """
    Verifica se o texto contém palavras típicas de spam.
    Retorna a palavra encontrada ou None.
    """
    lower = text.lower()
    for keyword in SPAM_KEYWORDS:
        if keyword.lower() in lower:
            return keyword
    return None


def simple_contact(request):
    """
    View de contato com múltiplas camadas de proteção anti-bot:
      1. Honeypot (campo 'website' invisível ao usuário)
      2. Timestamp mínimo de preenchimento (< 3s = bot)
      3. Rate limiting por IP (max 3 envios em 2 min)
      4. Filtro de palavras de spam em nome/assunto/mensagem
      5. CAPTCHA matemático (mantido como camada adicional)
    """
    site_settings = get_site_settings()
    form_sent = False
    form_error = False

    if request.method == 'POST':
        ip = get_client_ip(request)
        logger.info(f"[CONTATO] POST recebido de IP: {ip}")

        form = SimpleContactForm(request.POST)
        # Necessário para que o MathCaptchaField acesse a sessão
        form.fields['math_captcha'].widget.attrs['request'] = request

        # ── Camada 1: Honeypot ────────────────────────────────────────────────
        honeypot_value = request.POST.get('website', '').strip()
        if honeypot_value:
            logger.warning(f"[SPAM] Honeypot ativado por IP {ip} — valor: '{honeypot_value}'")
            # Simula sucesso para não revelar ao bot que foi detectado
            form_sent = True
        
        # ── Camada 2: Timestamp (submissão muito rápida = bot) ─────────────────
        elif _is_submitted_too_fast(request):
            logger.warning(f"[SPAM] Submissão muito rápida de IP {ip}")
            form_sent = True  # Silently reject

        # ── Camada 3: Rate Limiting por IP ────────────────────────────────────
        elif is_rate_limited(ip):
            logger.warning(f"[SPAM] Rate limit atingido para IP {ip}")
            form_sent = True  # Silently reject

        # ── Camadas 4 e 5: Validação real do formulário + filtro de spam ───────
        elif form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']

            # Verificar palavras de spam no conteúdo
            spam_found = (
                contains_spam(name) or
                contains_spam(subject) or
                contains_spam(message_text) or
                contains_spam(email)
            )

            if spam_found:
                logger.warning(
                    f"[SPAM] Conteúdo spam detectado de IP {ip} — "
                    f"palavra: '{spam_found}' | assunto: '{subject[:60]}'"
                )
                form_sent = True  # Silently reject — não salva no banco
            else:
                try:
                    message = Message.objects.create(
                        name=name,
                        email=email,
                        phone=form.cleaned_data['phone'],
                        subject=subject,
                        message=message_text,
                    )
                    logger.info(f"[CONTATO] Mensagem legítima salva — ID: {message.id}")
                    form_sent = True
                    form = SimpleContactForm()

                    # Notificação WhatsApp
                    try:
                        evolution_service = EvolutionWhatsAppService()
                        evolution_service.notify_new_contact(message)
                    except Exception as e:
                        logger.error(f"Erro ao enviar notificação WhatsApp: {e}")

                except Exception as e:
                    form_error = True
                    logger.error(f"Erro ao salvar mensagem: {e}", exc_info=True)
        else:
            logger.info(f"[CONTATO] Formulário inválido de IP {ip}: {form.errors}")

    else:
        form = SimpleContactForm()
        form.fields['math_captcha'].widget.attrs['request'] = request

    # Gera sempre uma nova pergunta matemática (GET e erros de POST)
    math_question = form.fields['math_captcha'].get_math_question(request)

    context = {
        'form': form,
        'site_settings': site_settings,
        'form_sent': form_sent,
        'form_error': form_error,
        'title': 'Contato',
        'subtitle': 'Entre em contato conosco',
        'math_question': math_question,
    }

    logger.info(f"[CONTATO] Renderizando template — form_sent={form_sent}, form_error={form_error}")
    return render(request, 'landing/contact_simple.html', context)


def _is_submitted_too_fast(request):
    """
    Retorna True se o formulário foi submetido em menos de MIN_FILL_TIME segundos.
    O campo 'form_load_time' contém o timestamp Unix (em ms) de quando a página abriu.
    """
    load_time_str = request.POST.get('form_load_time', '').strip()
    if not load_time_str:
        # Se o campo não veio, pode ser um bot que não executa JavaScript
        logger.warning("[SPAM] Campo form_load_time ausente — possível bot sem JS")
        return True
    try:
        load_time_ms = int(load_time_str)
        elapsed_seconds = (time.time() * 1000 - load_time_ms) / 1000
        if elapsed_seconds < MIN_FILL_TIME:
            logger.warning(f"[SPAM] Formulário preenchido em {elapsed_seconds:.2f}s (mínimo: {MIN_FILL_TIME}s)")
            return True
    except (ValueError, TypeError):
        logger.warning(f"[SPAM] form_load_time inválido: '{load_time_str}'")
        return True
    return False
