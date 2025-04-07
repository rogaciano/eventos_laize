import os
import sys
import django
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventos.settings')
django.setup()

# Importar após configurar o ambiente Django
from notifications.evolution_whatsapp import EvolutionWhatsAppService
from landing.models import Message
from django.utils import timezone
from django.conf import settings

def test_contact_notification():
    """
    Testa o envio de notificação para um novo contato
    """
    print("=== TESTE DE NOTIFICAÇÃO DE CONTATO ===")
    
    # Criar uma mensagem de teste
    message = Message(
        name="Usuário de Teste",
        email="teste@example.com",
        phone="5581999216560",
        subject="Teste de Notificação",
        message="Esta é uma mensagem de teste para verificar a integração com a API Evolution WhatsApp.",
        created_at=timezone.now()
    )
    
    # Enviar notificação
    service = EvolutionWhatsAppService()
    
    # Verificar configurações do Django
    print("\n=== CONFIGURAÇÕES DO DJANGO ===")
    print(f"EVOLUTION_API_KEY: {getattr(settings, 'EVOLUTION_API_KEY', 'Não definido')}")
    print(f"EVOLUTION_INSTANCE_ID: {getattr(settings, 'EVOLUTION_INSTANCE_ID', 'Não definido')}")
    print(f"EVOLUTION_API_URL: {getattr(settings, 'EVOLUTION_API_URL', 'Não definido')}")
    print(f"EVOLUTION_ENABLE_WHATSAPP: {getattr(settings, 'EVOLUTION_ENABLE_WHATSAPP', 'Não definido')}")
    print(f"EVOLUTION_NOTIFY_ON_CONTACT: {getattr(settings, 'EVOLUTION_NOTIFY_ON_CONTACT', 'Não definido')}")
    print(f"MANAGER_WHATSAPP: {getattr(settings, 'MANAGER_WHATSAPP', 'Não definido')}")
    
    # Verificar configurações do serviço
    print("\n=== CONFIGURAÇÕES DO SERVIÇO ===")
    print(f"API URL: {service.api_url}")
    print(f"API Key: {service.api_key}")
    print(f"Instance ID: {service.instance_id}")
    print(f"Enable WhatsApp: {service.enable_whatsapp}")
    print(f"Notify on Contact: {service.notify_on_contact}")
    print(f"Número do gestor: {service.manager_whatsapp}")
    print(f"Serviço configurado: {service.is_configured}")
    
    # Testar envio direto
    print("\n=== TESTE DE ENVIO DIRETO ===")
    if service.manager_whatsapp:
        print(f"Enviando mensagem direta para {service.manager_whatsapp}...")
        direct_result = service.send_message(
            service.manager_whatsapp,
            " *TESTE DE ENVIO DIRETO* \n\nEsta é uma mensagem de teste direto da API Evolution WhatsApp."
        )
        print(f"Resultado: {direct_result}")
    else:
        print("Número do gestor não configurado. Não é possível enviar mensagem direta.")
    
    # Enviar notificação
    print("\n=== TESTE DE NOTIFICAÇÃO ===")
    print("Enviando notificação...")
    result = service.notify_new_contact(message)
    
    # Exibir resultado
    print("\n=== RESULTADO ===")
    print(f"Sucesso: {'Sim' if result.get('success') else 'Não'}")
    print(f"Status: {result.get('status')}")
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")
    else:
        print("Mensagem enviada com sucesso!")
        print(f"Detalhes da resposta: {result.get('response')}")

if __name__ == "__main__":
    # Executar teste
    test_contact_notification()
