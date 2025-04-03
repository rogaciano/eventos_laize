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
    Testa o envio direto de mensagem usando a API de WhatsApp QR Code.
    """
    print("\n=== TESTE DE ENVIO DIRETO VIA API DE WHATSAPP QR CODE ===")
    
    # Criar instância do gerenciador
    manager = WhatsAppManager()
    
    # Verificar configuração
    if not manager.is_configured:
        print("❌ API não configurada corretamente!")
        print("Verifique as variáveis WHATSAPP_API_URL, WHATSAPP_API_USER_ID e WHATSAPP_API_TOKEN no arquivo .env")
        return
    
    # Obter número de telefone do destinatário
    default_number = os.getenv('TEST_WHATSAPP_NUMBER', '558199216560')
    to_number = input(f"Digite o número do destinatário (ou pressione Enter para usar {default_number}): ").strip()
    if not to_number:
        to_number = default_number
    
    # Enviar mensagem de teste
    print(f"\n📱 Enviando mensagem para {to_number}...")
    result = manager.send_message(
        to_number=to_number,
        message="Olá! Esta é uma mensagem de teste enviada via API de WhatsApp QR Code. 🚀"
    )
    
    # Verificar resultado
    if result.get('success', False):
        print("\n✅ Mensagem enviada com sucesso!")
        print(f"Detalhes: {result}")
    else:
        print("\n❌ Erro ao enviar mensagem:")
        print(f"Detalhes: {result}")

def test_contact_message():
    """
    Testa o envio de mensagem para um contato do banco de dados.
    """
    print("\n=== TESTE DE ENVIO PARA CONTATO DO BANCO DE DADOS ===")
    
    # Criar instância do gerenciador
    manager = WhatsAppManager()
    
    # Verificar configuração
    if not manager.is_configured:
        print("❌ API não configurada corretamente!")
        print("Verifique as variáveis WHATSAPP_API_URL, WHATSAPP_API_USER_ID e WHATSAPP_API_TOKEN no arquivo .env")
        return
    
    # Buscar contatos de WhatsApp no banco de dados
    contacts = PersonContact.objects.filter(type='whatsapp')
    if not contacts.exists():
        print("❌ Nenhum contato de WhatsApp encontrado no banco de dados!")
        return
    
    # Mostrar contatos disponíveis
    print("\nContatos disponíveis:")
    for i, contact in enumerate(contacts):
        print(f"{i+1}. {contact.person.name} - {contact.value}")
    
    # Selecionar contato
    while True:
        try:
            choice = input("\nSelecione o número do contato (ou pressione Enter para cancelar): ").strip()
            if not choice:
                return
            
            index = int(choice) - 1
            if 0 <= index < len(contacts):
                selected_contact = contacts[index]
                break
            else:
                print("❌ Número inválido! Tente novamente.")
        except ValueError:
            print("❌ Por favor, digite um número válido!")
    
    # Enviar mensagem de teste
    print(f"\n📱 Enviando mensagem para {selected_contact.person.name} ({selected_contact.value})...")
    
    # Criar mensagem personalizada
    message = f"""
Olá {selected_contact.person.name}!

Esta é uma mensagem de teste enviada via API de WhatsApp QR Code. 🚀

*Detalhes do contato:*
- ID: {selected_contact.id}
- Tipo: {selected_contact.get_type_display()}
- Valor: {selected_contact.value}

Mensagem enviada em: {django.utils.timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
    
    # Enviar mensagem
    result = manager.send_whatsapp_to_contact(selected_contact, message)
    
    # Verificar resultado
    if result and result.status == "sent":
        print("\n✅ Mensagem enviada com sucesso!")
        print(f"ID da mensagem: {result.id}")
        print(f"Status: {result.status}")
        print(f"Data de envio: {result.created_at}")
    else:
        print("\n❌ Erro ao enviar mensagem:")
        if result:
            print(f"Status: {result.status}")
            print(f"Resposta: {result.response_data}")
        else:
            print("Nenhum resultado retornado.")

def test_manager_notification():
    """
    Testa o envio de notificação para o gestor.
    """
    print("\n=== TESTE DE NOTIFICAÇÃO PARA O GESTOR ===")
    
    # Criar instância do gerenciador
    manager = WhatsAppManager()
    
    # Verificar configuração
    if not manager.is_configured:
        print("❌ API não configurada corretamente!")
        print("Verifique as variáveis WHATSAPP_API_URL, WHATSAPP_API_USER_ID e WHATSAPP_API_TOKEN no arquivo .env")
        return
    
    # Verificar configuração do gestor
    manager_contact = manager.get_manager_contact()
    if not manager_contact:
        print("❌ Contato do gestor não encontrado!")
        print("Verifique as variáveis MANAGER_WHATSAPP e MANAGER_ID no arquivo .env")
        print("Ou cadastre um contato de WhatsApp para o gestor no banco de dados.")
        return
    
    # Mostrar detalhes do gestor
    print(f"\nGestor encontrado: {manager_contact.person.name} ({manager_contact.value})")
    
    # Confirmar envio
    confirm = input("\nDeseja enviar uma notificação de teste para o gestor? (s/n): ").strip().lower()
    if confirm != 's':
        print("Operação cancelada.")
        return
    
    # Criar mensagem de teste
    message = f"""
*NOTIFICAÇÃO DE TESTE*

Esta é uma mensagem de teste do sistema de notificações via WhatsApp QR Code. 🚀

*Detalhes da configuração:*
- API URL: {settings.WHATSAPP_API_URL}
- Gestor: {manager_contact.person.name}
- Telefone: {manager_contact.value}

Mensagem enviada em: {django.utils.timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
    
    # Enviar mensagem
    result = manager.send_whatsapp_to_contact(manager_contact, message)
    
    # Verificar resultado
    if result and result.status == "sent":
        print("\n✅ Notificação enviada com sucesso!")
        print(f"ID da mensagem: {result.id}")
        print(f"Status: {result.status}")
    else:
        print("\n❌ Erro ao enviar notificação:")
        if result:
            print(f"Status: {result.status}")
            print(f"Resposta: {result.response_data}")
        else:
            print("Nenhum resultado retornado.")

if __name__ == "__main__":
    print("=== TESTE DE ENVIO DE WHATSAPP ===")
    print("Esta solução usa a API de WhatsApp QR Code para envio de mensagens.")
    print("URL da API:", os.environ.get('WHATSAPP_API_URL', 'Não configurada'))
    print("User ID:", os.environ.get('WHATSAPP_API_USER_ID', 'Não configurado'))
    print("Token:", 'Configurado' if os.environ.get('WHATSAPP_API_TOKEN') else 'Não configurado')
    print("\n")
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Testar envio direto via API")
        print("2. Testar envio para contato do banco de dados")
        print("3. Testar notificação para o gestor")
        print("0. Sair")
        
        option = input("\nOpção: ").strip()
        
        if option == '1':
            test_direct_api_message()
        elif option == '2':
            test_contact_message()
        elif option == '3':
            test_manager_notification()
        elif option == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida! Tente novamente.")