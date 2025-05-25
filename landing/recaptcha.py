import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def verify_recaptcha(recaptcha_response):
    """
    Verifica a resposta do reCAPTCHA com a API do Google
    
    Args:
        recaptcha_response: Token recebido do cliente
        
    Returns:
        tuple: (sucesso, pontuação, erro)
            - sucesso: True se a verificação for bem-sucedida e a pontuação for aceitável
            - pontuação: Valor entre 0.0 e 1.0 que indica a probabilidade de ser um humano
            - erro: Mensagem de erro, se houver
    """
    # Verificar se o reCAPTCHA está em modo estrito
    if not settings.RECAPTCHA_STRICT:
        if not recaptcha_response:
            logger.warning("reCAPTCHA token não fornecido, mas RECAPTCHA_STRICT está desativado")
            return True, 1.0, None
    elif not recaptcha_response:
        return False, 0, "Resposta do reCAPTCHA não fornecida"
    
    try:
        # Dados para enviar ao Google
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        
        # Fazer a requisição para a API do Google
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data
        )
        
        # Analisar a resposta
        result = response.json()
        
        # Verificar se a requisição foi bem-sucedida
        if result.get('success'):
            # Verificar a pontuação (score)
            score = result.get('score', 0)
            
            # Verificar se a pontuação é aceitável
            if score >= settings.RECAPTCHA_REQUIRED_SCORE:
                return True, score, None
            else:
                logger.warning(f"reCAPTCHA score too low: {score}")
                return False, score, f"Pontuação de segurança muito baixa: {score}"
        else:
            error_codes = result.get('error-codes', [])
            logger.error(f"reCAPTCHA verification failed: {error_codes}")
            return False, 0, f"Verificação do reCAPTCHA falhou: {error_codes}"
            
    except requests.RequestException as e:
        # Erro de conexão ou timeout
        logger.exception(f"Erro de conexão ao verificar reCAPTCHA: {e}")
        # Se não estiver em modo estrito, permitir o envio mesmo com erro de conexão
        if not settings.RECAPTCHA_STRICT:
            logger.warning("Permitindo envio mesmo com erro de conexão ao reCAPTCHA pois RECAPTCHA_STRICT está desativado")
            return True, 0.5, None
        return False, 0, f"Erro de conexão ao verificar reCAPTCHA: {str(e)}"
    except json.JSONDecodeError as e:
        # Erro ao decodificar a resposta JSON
        logger.exception(f"Erro ao decodificar resposta do reCAPTCHA: {e}")
        if not settings.RECAPTCHA_STRICT:
            logger.warning("Permitindo envio mesmo com erro na resposta do reCAPTCHA pois RECAPTCHA_STRICT está desativado")
            return True, 0.5, None
        return False, 0, f"Erro ao processar resposta do reCAPTCHA: {str(e)}"
    except Exception as e:
        # Outros erros inesperados
        logger.exception(f"Erro inesperado ao verificar reCAPTCHA: {e}")
        if not settings.RECAPTCHA_STRICT:
            logger.warning("Permitindo envio mesmo com erro inesperado no reCAPTCHA pois RECAPTCHA_STRICT está desativado")
            return True, 0.5, None
        return False, 0, f"Erro ao verificar reCAPTCHA: {str(e)}"
