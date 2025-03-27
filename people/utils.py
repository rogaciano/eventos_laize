import requests
import json
from .models import WhatsAppMessage
from django.conf import settings

def send_whatsapp_message(contact, message):
    """
    Send a WhatsApp message using the API and store the message in the database.
    
    Args:
        contact: PersonContact object (must be of type 'whatsapp')
        message: String message to send
    
    Returns:
        WhatsAppMessage object
    """
    # Format phone number (remove any non-numeric characters)
    phone_number = ''.join(filter(str.isdigit, contact.value))
    
    # Ensure the phone number is valid
    if not phone_number:
        return None
    
    # Se o número não começar com 55 (código do Brasil), adiciona
    if not phone_number.startswith('55'):
        phone_number = '55' + phone_number
        
    # Remove o 9 inicial do número se ele tiver 13 dígitos (55 + DDD + 9 + número)
    if len(phone_number) == 13 and phone_number[4] == '9':
        phone_number = phone_number[:4] + phone_number[5:]
    
    url = settings.WHATSAPP_API_URL
    
    payload = {
        "chatId": f"{phone_number}@c.us",
        "text": message,
        "session": "default"
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Create WhatsAppMessage object
    whatsapp_message = WhatsAppMessage(
        person=contact.person,
        contact=contact,
        message=message,
        status="sending"
    )
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        response_data = response.json()
        
        # Update WhatsAppMessage with response data
        whatsapp_message.response_data = response_data
        
        # Set status based on response
        if response.status_code == 200:
            # Verifica se há uma chave 'key' na resposta, o que indica sucesso
            if 'key' in response_data:
                whatsapp_message.status = "sent"
            # Verifica se há uma mensagem de erro explícita
            elif 'error' in response_data:
                whatsapp_message.status = "failed"
            else:
                whatsapp_message.status = "unknown"
        else:
            whatsapp_message.status = "failed"
            
        whatsapp_message.save()
        return whatsapp_message
        
    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        whatsapp_message.status = "error"
        whatsapp_message.response_data = {"error": str(e)}
        whatsapp_message.save()
        return whatsapp_message
