"""
Script para testar o envio de mensagens WhatsApp usando a API do Twilio.
Esta é uma alternativa à API personalizada que não está funcionando.
"""

import os
import django
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'eventos.settings'
django.setup()

def test_twilio_whatsapp():
    """
    Testa o envio de mensagem usando a API do Twilio para WhatsApp.
    """
    try:
        # Importar após configurar o Django
        from notifications.whatsapp_twilio import WhatsAppTwilioManager
        
        # Verificar configurações do Twilio
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER')
        
        if not account_sid or not auth_token or not from_number:
            print("❌ Configurações do Twilio incompletas!")
            print("Adicione as seguintes variáveis ao seu arquivo .env:")
            print("  TWILIO_ACCOUNT_SID=seu_account_sid")
            print("  TWILIO_AUTH_TOKEN=seu_auth_token")
            print("  TWILIO_WHATSAPP_NUMBER=seu_numero_whatsapp")
            print("\nVocê pode obter essas informações criando uma conta em https://www.twilio.com/")
            return
        
        # Número de telefone para teste
        default_number = os.getenv('TEST_WHATSAPP_NUMBER', '558199216560')
        test_number = input(f"Digite o número de telefone para teste (ou pressione Enter para usar {default_number}): ").strip()
        if not test_number:
            test_number = default_number
        
        # Mensagem de teste
        message = "Olá! Esta é uma mensagem de teste enviada via API do Twilio. 🚀"
        
        # Criar instância do gerenciador de WhatsApp
        whatsapp_manager = WhatsAppTwilioManager()
        
        if not whatsapp_manager.is_configured:
            print("❌ Gerenciador de WhatsApp não configurado corretamente!")
            return
        
        print(f"📱 Enviando mensagem para {test_number}...")
        print(f"De: {from_number}")
        
        # Enviar mensagem
        result = whatsapp_manager.send_message(test_number, message)
        
        if result.get('success', False):
            print("✅ Mensagem enviada com sucesso!")
            print(f"  - Status: {result.get('status')}")
            if 'response' in result:
                print(f"  - SID: {result['response'].get('sid')}")
                print(f"  - Status da mensagem: {result['response'].get('status')}")
        else:
            print("❌ Erro ao enviar mensagem:")
            print(f"  - {result.get('error', 'Erro desconhecido')}")
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {str(e)}")
        print("Você precisa instalar a biblioteca twilio:")
        print("  pip install twilio")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    print("=== TESTE DE ENVIO DE WHATSAPP COM TWILIO ===")
    print("Esta solução usa a API oficial do Twilio para WhatsApp Business.")
    print("Requer uma conta no Twilio e um número de WhatsApp Business aprovado.")
    print("\n")
    
    # Verificar se twilio está instalado
    try:
        import twilio
        print("✅ Biblioteca twilio encontrada.")
    except ImportError:
        print("❌ Biblioteca twilio não encontrada.")
        print("Execute o comando abaixo para instalar:")
        print("  pip install twilio")
        exit(1)
    
    # Executar teste
    test_twilio_whatsapp()
