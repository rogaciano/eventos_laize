import requests
import json

def send_whatsapp_message(phone_number, message):
    url = "http://149.28.249.146:3000/api/sendText"
    
    payload = {
        "chatId": f"{phone_number}@c.us",
        "text": message,
        "session": "default"  # Adicionando o parâmetro de sessão
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return {"error": str(e)}

# Exemplo de uso
numero = "558192328190" # "558199216560"
mensagem = "Olá! Esta mensagem foi enviada do meu código Python. Não é mais Laravel!!!!"

result = send_whatsapp_message(numero, mensagem)
print(result)