"""
Script simples para testar o envio de mensagens WhatsApp usando a API de WhatsApp QR Code.
Este script não depende do Django, apenas faz uma chamada direta à API.
"""

import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=True)

def format_phone_number(phone_number):
    """
    Formata o número de telefone para o formato internacional.
    Remove caracteres não numéricos e adiciona o código do país se necessário.
    """
    # Remover todos os caracteres não numéricos
    digits_only = ''.join(filter(str.isdigit, phone_number))
    
    # Se não começar com 55 (Brasil), adicionar
    if not digits_only.startswith('55'):
        digits_only = '55' + digits_only
        
    print(f"DEBUG - Número original: {phone_number}")
    print(f"DEBUG - Número formatado: {digits_only}")
    
    return digits_only

def test_whatsapp_api():
    """
    Testa o envio direto de mensagem usando a API de WhatsApp QR Code.
    """
    # Obter configurações da API diretamente do arquivo .env
    api_url = os.getenv('WHATSAPP_API_URL')
    api_token = os.getenv('WHATSAPP_API_TOKEN')
    
    print(f"DEBUG - URL da API: {api_url}")
    print(f"DEBUG - Token: {'Configurado' if api_token else 'Não configurado'}")
    
    if not api_url or not api_token:
        print("❌ Configurações da API incompletas!")
        print("Verifique as variáveis WHATSAPP_API_URL e WHATSAPP_API_TOKEN no arquivo .env")
        return
    
    # Número de telefone do remetente (seu número)
    sender_number = os.getenv('MANAGER_WHATSAPP', '5581999216560')
    print(f"DEBUG - Remetente: {sender_number}")
    
    # Número de telefone do destinatário
    recipient_number = input(f"Digite o número do destinatário: ")
    if not recipient_number:
        print("❌ Número do destinatário é obrigatório!")
        return
    
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
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
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
    print("=== TESTE SIMPLES DE ENVIO DE WHATSAPP COM API QR CODE ===")
    
    # Mostrar configurações atuais
    print("Configurações carregadas do arquivo .env:")
    print(f"WHATSAPP_API_URL: {os.getenv('WHATSAPP_API_URL')}")
    print(f"WHATSAPP_API_TOKEN: {'Configurado' if os.getenv('WHATSAPP_API_TOKEN') else 'Não configurado'}")
    print(f"MANAGER_WHATSAPP: {os.getenv('MANAGER_WHATSAPP')}")
    print("\n")
    
    # Executar teste
    test_whatsapp_api()
