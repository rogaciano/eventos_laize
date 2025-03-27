from django.conf import settings
import logging

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
