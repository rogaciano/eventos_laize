"""
Configurações específicas para o módulo de notificações.
Este arquivo contém configurações que são carregadas diretamente do .env
sem precisar modificar o settings.py principal.
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Função auxiliar para converter strings em booleanos
def str_to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).lower() in ('true', 't', '1', 'yes', 'y')

# Configurações do WhatsApp (Talkia)
ENABLE_WHATSAPP = str_to_bool(os.getenv('ENABLE_WHATSAPP', '0'))
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://webpicne.digisac.co/api/v1')
WHATSAPP_API_USER_ID = os.getenv('WHATSAPP_API_USER_ID', None)
WHATSAPP_API_TOKEN = os.getenv('WHATSAPP_API_TOKEN', None)

# Configurações do Evolution WhatsApp
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', None)
EVOLUTION_INSTANCE_ID = os.getenv('EVOLUTION_INSTANCE_ID', None)
EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'https://evo.n8newhatsapp.com.br')
EVOLUTION_ENABLE_WHATSAPP = str_to_bool(os.getenv('EVOLUTION_ENABLE_WHATSAPP', '0'))
EVOLUTION_NOTIFY_ON_REGISTRATION = str_to_bool(os.getenv('EVOLUTION_NOTIFY_ON_REGISTRATION', '0'))
EVOLUTION_NOTIFY_ON_CONTACT = str_to_bool(os.getenv('EVOLUTION_NOTIFY_ON_CONTACT', '0'))

# Configurações do gestor para notificações
MANAGER_WHATSAPP = os.getenv('MANAGER_WHATSAPP', None)
if MANAGER_WHATSAPP:
    # Limpar o número do gestor (remover comentários e espaços)
    MANAGER_WHATSAPP = ''.join(filter(str.isdigit, str(MANAGER_WHATSAPP)))

MANAGER_ID = os.getenv('MANAGER_ID', None)
NOTIFY_ON_REGISTRATION = str_to_bool(os.getenv('NOTIFY_ON_REGISTRATION', '0'))
NOTIFY_ON_CONTACT = str_to_bool(os.getenv('NOTIFY_ON_CONTACT', '0'))

# Configurações do Twilio para WhatsApp
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', None)
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', None)
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', None)
