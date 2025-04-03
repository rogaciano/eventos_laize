import os
import django
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Forçar a atualização das variáveis de ambiente no Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'eventos.settings'
os.environ['WHATSAPP_API_URL'] = os.getenv('WHATSAPP_API_URL')
os.environ['WHATSAPP_API_USER_ID'] = os.getenv('WHATSAPP_API_USER_ID')
os.environ['WHATSAPP_API_TOKEN'] = os.getenv('WHATSAPP_API_TOKEN')

# Configurar Django
django.setup()

from notifications.whatsapp import WhatsAppManager
from people.models import Person, PersonContact
from django.conf import settings

def test_direct_api_message():
    """
    Testa o envio direto de mensagem usando a API personalizada.
    Não requer um contato no banco de dados.
    """
    # Número de telefone para teste
    test_number = os.getenv('TEST_WHATSAPP_NUMBER', '558199216560')
    
    # Mensagem de teste
    message = "Olá! Esta é uma mensagem de teste enviada pela API personalizada. 🚀"
    
    # Criar instância do gerenciador de WhatsApp diretamente com as variáveis de ambiente
    whatsapp_manager = WhatsAppManager()
    
    # Forçar a atualização das configurações
    whatsapp_manager.api_url = os.environ.get('WHATSAPP_API_URL')
    whatsapp_manager.api_user_id = os.environ.get('WHATSAPP_API_USER_ID')
    whatsapp_manager.api_token = os.environ.get('WHATSAPP_API_TOKEN')
    
    # Verificar se a API está configurada
    if not whatsapp_manager.is_configured:
        print("⚠️ Configurações da API incompletas. Verifique as variáveis de ambiente:")
        print(f"  - WHATSAPP_API_URL: {'✓' if whatsapp_manager.api_url else '✗'} ({whatsapp_manager.api_url})")
        print(f"  - WHATSAPP_API_USER_ID: {'✓' if whatsapp_manager.api_user_id else '✗'} ({whatsapp_manager.api_user_id})")
        print(f"  - WHATSAPP_API_TOKEN: {'✓' if whatsapp_manager.api_token else '✗'}")
        return
    
    print(f"📱 Enviando mensagem para {test_number}...")
    print(f"API URL: {whatsapp_manager.api_url}")
    result = whatsapp_manager.send_message(test_number, message)
    
    if result.get('success', False):
        print("✅ Mensagem enviada com sucesso!")
        print(f"  - Status: {result.get('status')}")
        if 'response' in result:
            print(f"  - Resposta: {result['response']}")
    else:
        print("❌ Erro ao enviar mensagem:")
        print(f"  - {result.get('error')}")

def test_contact_message():
    """
    Testa o envio de mensagem para um contato existente no banco de dados.
    """
    # Buscar um contato de WhatsApp no banco de dados
    contact = PersonContact.objects.filter(type='whatsapp').first()
    
    if not contact:
        print("❌ Nenhum contato de WhatsApp encontrado no banco de dados.")
        return
    
    print(f"📱 Enviando mensagem para {contact.person.name} ({contact.value})...")
    
    # Mensagem de teste
    message = f"Olá {contact.person.name}! Esta é uma mensagem de teste enviada pelo sistema. 🚀"
    
    # Criar instância do gerenciador de WhatsApp
    whatsapp_manager = WhatsAppManager()
    whatsapp_manager.api_url = os.environ.get('WHATSAPP_API_URL')
    whatsapp_manager.api_user_id = os.environ.get('WHATSAPP_API_USER_ID')
    whatsapp_manager.api_token = os.environ.get('WHATSAPP_API_TOKEN')
    
    # Enviar mensagem
    whatsapp_message = whatsapp_manager.send_whatsapp_to_contact(contact, message)
    
    if whatsapp_message and whatsapp_message.status == "sent":
        print("✅ Mensagem enviada com sucesso!")
        print(f"  - ID: {whatsapp_message.id}")
        print(f"  - Status: {whatsapp_message.status}")
    else:
        print("❌ Erro ao enviar mensagem:")
        if whatsapp_message and whatsapp_message.response_data:
            print(f"  - {whatsapp_message.response_data.get('error', 'Erro desconhecido')}")
        else:
            print("  - Erro desconhecido")

def test_manager_notification():
    """
    Testa o envio de notificação para o gestor.
    """
    # Criar instância do gerenciador de WhatsApp
    whatsapp_manager = WhatsAppManager()
    whatsapp_manager.api_url = os.environ.get('WHATSAPP_API_URL')
    whatsapp_manager.api_user_id = os.environ.get('WHATSAPP_API_USER_ID')
    whatsapp_manager.api_token = os.environ.get('WHATSAPP_API_TOKEN')
    
    # Verificar se o gestor está configurado
    manager_contact = whatsapp_manager.get_manager_contact()
    
    if not manager_contact:
        print("❌ Contato do gestor não encontrado. Verifique as variáveis de ambiente:")
        print(f"  - MANAGER_WHATSAPP: {'✓' if whatsapp_manager.manager_whatsapp else '✗'}")
        print(f"  - MANAGER_ID: {'✓' if whatsapp_manager.manager_id else '✗'}")
        return
    
    print(f"📱 Enviando notificação para o gestor ({manager_contact.person.name})...")
    
    # Simular uma pessoa recém-cadastrada
    person = Person.objects.first()
    
    if not person:
        print("❌ Nenhuma pessoa encontrada no banco de dados para simular notificação.")
        return
    
    # Enviar notificação
    result = whatsapp_manager.notify_new_registration(person)
    
    if result:
        print("✅ Notificação enviada com sucesso!")
    else:
        print("❌ Erro ao enviar notificação.")

if __name__ == "__main__":
    print("=== TESTE DE ENVIO DE WHATSAPP COM API PERSONALIZADA ===")
    print(f"API URL (do .env): {os.environ.get('WHATSAPP_API_URL')}")
    print(f"User ID (do .env): {os.environ.get('WHATSAPP_API_USER_ID')}")
    print(f"Endpoint: /messages")
    print(f"Autenticação: Bearer Token")
    print("\n")
    
    # Executar diretamente a opção 1 (envio direto via API)
    print("Executando teste de envio direto via API...")
    test_direct_api_message()
    
    # Comentado o menu interativo
    """
    print("Escolha uma opção de teste:")
    print("1. Envio direto via API")
    print("2. Envio para contato do banco de dados")
    print("3. Notificação para o gestor")
    
    option = input("Opção (1-3): ")
    
    if option == "1":
        test_direct_api_message()
    elif option == "2":
        test_database_contact()
    elif option == "3":
        test_manager_notification()
    else:
        print("Opção inválida!")
    """