from django.conf import settings
import logging
from .models import Person

logger = logging.getLogger(__name__)

def whatsapp_settings(request):
    """
    Context processor para disponibilizar as configurações do WhatsApp para todos os templates.
    """
    # Log para depuração
    logger.info(f"ENABLE_WHATSAPP value: {settings.ENABLE_WHATSAPP}")
    print(f"ENABLE_WHATSAPP value: {settings.ENABLE_WHATSAPP}")
    
    return {
        'ENABLE_WHATSAPP': settings.ENABLE_WHATSAPP,
    }

def pending_people_count(request):
    """
    Context processor para adicionar a contagem de pessoas pendentes a todos os templates
    """
    if request.user.is_authenticated:
        count = Person.objects.filter(status='pendente').count()
        return {'pending_people_count': count}
    return {'pending_people_count': 0}
