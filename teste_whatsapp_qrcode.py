"""
Script para testar o envio de mensagens WhatsApp usando a API de WhatsApp QR Code.
Esta é uma alternativa à API personalizada anterior.

Endpoint: https://app.talkiachat.com.br/external_api/mensagens/whatsapp_qr_code/enviar
Método: GET
Parâmetros:
- telefone_remetente: Número do remetente (formato internacional)
- telefone_destinatario: Número do destinatário (formato internacional)
- conteudo_mensagem: Texto da mensagem
Autenticação: Bearer Token
"""

import os
import requests
import django
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'eventos.settings'
django.setup()

def format_phone_number(phone_number):
    """
    Formata o número de telefone para o formato internacional.
    Remove caracteres não numéricos e adiciona o código do país se necessário.
    
    Args:
        phone_number: Número de telefone a ser formatado
        
    Returns:
        Número formatado (formato: 5511999999999)
    """
    # Remover todos os caracteres não numéricos
    digits_only = ''.join(filter(str.isdigit, phone_number))
    
    # Se não começar com 55 (Brasil), adicionar
    if not digits_only.startswith('55'):
        digits_only = '55' + digits_only
        
    # Garantir que o número tenha pelo menos 10 dígitos (DDD + número)
    if len(digits_only) < 12:
        print(f"AVISO: Número de telefone {phone_number} parece estar incompleto após formatação: {digits_only}")
        
    print(f"DEBUG - Número original: {phone_number}")
    print(f"DEBUG - Número formatado: {digits_only}")
    
    return digits_only

def test_whatsapp_qrcode_api():
    """
    Testa o envio de mensagem usando a API de WhatsApp QR Code.
    """
    # Obter configurações da API
    api_url = os.environ.get('WHATSAPP_API_URL')
    api_token = os.environ.get('WHATSAPP_API_TOKEN')
    
    if not api_url or not api_token:
        print("❌ Configurações da API incompletas!")
        print("Verifique as variáveis WHATSAPP_API_URL e WHATSAPP_API_TOKEN no arquivo .env")
        return
    
    # Número de telefone do remetente (seu número)
    sender_number = os.getenv('MANAGER_WHATSAPP', '5581999216560')
    print(f"Usando número do remetente: {sender_number}")
    
    # Número de telefone do destinatário
    default_recipient = os.getenv('TEST_WHATSAPP_NUMBER', '558199216560')
    recipient_number = input(f"Digite o número do destinatário (ou pressione Enter para usar {default_recipient}): ").strip()
    if not recipient_number:
        recipient_number = default_recipient
    
    # Formatar números
    sender_formatted = format_phone_number(sender_number)
    recipient_formatted = format_phone_number(recipient_number)
    
    # Mensagem de teste
    message = "Olá! Esta é uma mensagem de teste enviada via API de WhatsApp QR Code. 🚀"
    
    # Preparar parâmetros da requisição
    params = {
        'telefone_remetente': sender_formatted,
        'telefone_destinatario': recipient_formatted,
        'conteudo_mensagem': message
    }
    
    # Configurar headers com token de autenticação
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    
    print(f"\n📱 Enviando mensagem de {sender_formatted} para {recipient_formatted}...")
    print(f"URL da API: {api_url}")
    print(f"Mensagem: {message}")
    print(f"Headers: {headers}")
    print(f"Parâmetros: {params}")
    
    try:
        # Enviar requisição para a API
        response = requests.get(api_url, headers=headers, params=params)
        
        # Verificar resposta
        print(f"\nStatus code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Mensagem enviada com sucesso!")
            try:
                response_data = response.json()
                print(f"Detalhes: {response_data}")
            except:
                print("Resposta não é um JSON válido.")
        else:
            print("\n❌ Erro ao enviar mensagem:")
            if response.status_code == 400:
                print("  - Dados insuficientes ou inválidos")
            elif response.status_code == 404:
                print("  - Integração não encontrada")
            elif response.status_code == 500:
                print("  - Erro interno do servidor")
            else:
                print(f"  - Erro desconhecido (código {response.status_code})")
            
            try:
                error_data = response.json()
                print(f"Detalhes do erro: {error_data}")
            except:
                print(f"Resposta de erro: {response.text}")
    
    except Exception as e:
        print(f"\n❌ Erro ao fazer requisição: {str(e)}")

if __name__ == "__main__":
    print("=== TESTE DE ENVIO DE WHATSAPP COM API QR CODE ===")
    print("Esta solução usa a API de WhatsApp QR Code para envio de mensagens.")
    print("URL da API:", os.environ.get('WHATSAPP_API_URL', 'Não configurada'))
    print("\n")
    
    # Executar teste
    test_whatsapp_qrcode_api()
