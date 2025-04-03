"""
Script para testar o envio de mensagens WhatsApp usando pywhatkit.
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

def test_direct_whatsapp():
    """
    Testa o envio direto de mensagem usando pywhatkit.
    Não requer uma API externa, usa o WhatsApp Web.
    """
    try:
        # Importar após configurar o Django
        from notifications.whatsapp_direct import WhatsAppDirectManager
        
        # Número de telefone para teste
        default_number = os.getenv('TEST_WHATSAPP_NUMBER', '558199216560')
        test_number = input(f"Digite o número de telefone para teste (ou pressione Enter para usar {default_number}): ").strip()
        if not test_number:
            test_number = default_number
        
        # Mensagem de teste
        message = "Olá! Esta é uma mensagem de teste enviada via pywhatkit. 🚀"
        
        # Criar instância do gerenciador de WhatsApp
        whatsapp_manager = WhatsAppDirectManager()
        
        print(f"📱 Enviando mensagem para {test_number}...")
        print(f"⚠️ IMPORTANTE: O WhatsApp Web será aberto no seu navegador.")
        print(f"⚠️ Certifique-se de que o WhatsApp Web já está logado no seu navegador.")
        print(f"⚠️ Não feche o navegador durante o processo.")
        
        # Enviar mensagem
        result = whatsapp_manager.send_message(test_number, message)
        
        if result.get('success', False):
            print("✅ Mensagem enviada com sucesso!")
            print(f"  - Status: {result.get('status')}")
            if 'response' in result:
                print(f"  - Resposta: {result['response']}")
        else:
            print("❌ Erro ao enviar mensagem:")
            print(f"  - {result.get('error', 'Erro desconhecido')}")
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {str(e)}")
        print("Você precisa instalar a biblioteca pywhatkit:")
        print("  pip install pywhatkit")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    print("=== TESTE DE ENVIO DE WHATSAPP COM PYWHATKIT ===")
    print("Esta solução usa o WhatsApp Web e não requer uma API externa.")
    print("Certifique-se de que o WhatsApp Web já está logado no seu navegador.")
    print("\n")
    
    # Verificar se pywhatkit está instalado
    try:
        import pywhatkit
        print("✅ Biblioteca pywhatkit encontrada.")
    except ImportError:
        print("❌ Biblioteca pywhatkit não encontrada.")
        print("Execute o comando abaixo para instalar:")
        print("  pip install pywhatkit")
        exit(1)
    
    # Executar teste
    test_direct_whatsapp()
