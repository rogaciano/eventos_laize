import requests
import json
import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações a partir do arquivo .env
NUMERO_TESTE = "558199216560"  # Substitua pelo número de teste desejado
MENSAGEM_TESTE = "Teste de envio de mensagem via API Evolution WhatsApp"
API_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_ID = os.getenv("EVOLUTION_INSTANCE_ID")
API_URL = os.getenv("EVOLUTION_API_URL", "https://evo.n8newhatsapp.com.br")

def enviar_mensagem_whatsapp(numero, mensagem):
    """
    Função para enviar mensagem via Evolution WhatsApp
    
    :param numero: Número do destinatário (com código do país)
    :param mensagem: Texto da mensagem
    :return: Resposta da API em formato JSON
    """
    # URL com base nas variáveis de ambiente
    url = f"{API_URL}/message/sendText/{INSTANCE_ID}"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }
    
    # Payload conforme documentação
    payload = {
        "number": numero,
        "text": mensagem
    }
    
    print(f"Enviando mensagem para {numero}...")
    print(f"Conteúdo: {mensagem}")
    print(f"URL: {url}")
    print(f"API Key: {API_KEY}")
    print(f"Payload: {json.dumps(payload)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        try:
            response_json = response.json()
            print(f"Resposta JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
            return response_json
        except json.JSONDecodeError:
            print(f"Resposta não é JSON válido: {response.text}")
            return {"error": "Resposta não é JSON válido", "text": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("=== TESTE DE ENVIO DE WHATSAPP VIA EVOLUTION API ===")
    
    # Verificar se as variáveis de ambiente foram carregadas
    if not API_KEY or not INSTANCE_ID:
        print("ERRO: Variáveis de ambiente não configuradas corretamente.")
        print(f"API_KEY: {'Configurada' if API_KEY else 'Não configurada'}")
        print(f"INSTANCE_ID: {'Configurado' if INSTANCE_ID else 'Não configurado'}")
        sys.exit(1)
    
    # Usar valores fixos para teste
    print(f"Usando número: {NUMERO_TESTE}")
    print(f"Usando mensagem: {MENSAGEM_TESTE}")
    print(f"Instância: {INSTANCE_ID}")
    
    # Enviar mensagem
    print("\n=== Enviando mensagem... ===")
    resultado = enviar_mensagem_whatsapp(NUMERO_TESTE, MENSAGEM_TESTE)
    
    # Exibir resultado final
    print("\n=== Resultado final do envio ===")
    if isinstance(resultado, dict) and "error" in resultado:
        print(f"ERRO: {resultado.get('error')}")
    else:
        print("Mensagem enviada com sucesso!")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    print("\n=== Teste concluído ===")