import requests
import json
import os
import logging
from notifications import settings as notification_settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class EvolutionWhatsAppService:
    """
    Serviço para envio de mensagens WhatsApp usando a API Evolution.
    """
    
    def __init__(self):
        """
        Inicializa o serviço com as configurações da API.
        """
        # Configurações da API Evolution
        self.api_key = notification_settings.EVOLUTION_API_KEY
        self.instance_id = notification_settings.EVOLUTION_INSTANCE_ID
        self.api_url = notification_settings.EVOLUTION_API_URL
        
        # Configurações do gestor
        self.manager_whatsapp = notification_settings.MANAGER_WHATSAPP
        
        # Flags de notificação específicas do Evolution
        self.enable_whatsapp = notification_settings.EVOLUTION_ENABLE_WHATSAPP
        self.notify_on_registration = notification_settings.EVOLUTION_NOTIFY_ON_REGISTRATION
        self.notify_on_contact = notification_settings.EVOLUTION_NOTIFY_ON_CONTACT
        
        # Se não houver configurações específicas, usar as configurações gerais
        if not hasattr(notification_settings, 'EVOLUTION_NOTIFY_ON_REGISTRATION'):
            self.notify_on_registration = notification_settings.NOTIFY_ON_REGISTRATION
            
        if not hasattr(notification_settings, 'EVOLUTION_NOTIFY_ON_CONTACT'):
            self.notify_on_contact = notification_settings.NOTIFY_ON_CONTACT
            
        if not hasattr(notification_settings, 'EVOLUTION_ENABLE_WHATSAPP'):
            self.enable_whatsapp = notification_settings.ENABLE_WHATSAPP
        
        # Logs para debug
        logger.debug(f"Evolution WhatsApp Service inicializado")
        logger.debug(f"API Key: {self.api_key}")
        logger.debug(f"Instance ID: {self.instance_id}")
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"Enable WhatsApp: {self.enable_whatsapp}")
        logger.debug(f"Notify on Registration: {self.notify_on_registration}")
        logger.debug(f"Notify on Contact: {self.notify_on_contact}")
        logger.debug(f"Manager WhatsApp: {self.manager_whatsapp}")
        
        # Logs para impressão durante o teste
        print(f"Evolution WhatsApp Service inicializado")
        print(f"API Key: {self.api_key}")
        print(f"Instance ID: {self.instance_id}")
        print(f"API URL: {self.api_url}")
        print(f"Enable WhatsApp: {self.enable_whatsapp}")
        print(f"Notify on Registration: {self.notify_on_registration}")
        print(f"Notify on Contact: {self.notify_on_contact}")
        print(f"Manager WhatsApp: {self.manager_whatsapp}")
    
    @property
    def is_configured(self):
        """
        Verifica se todas as configurações necessárias estão presentes.
        """
        return all([self.api_url, self.api_key, self.instance_id, self.enable_whatsapp, self.manager_whatsapp])
    
    def format_phone_number(self, phone_number):
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
        
        # Se começar com 0, remover
        if digits_only.startswith('0'):
            digits_only = digits_only[1:]
        
        # Se não tiver o código do país (55 para Brasil), adicionar
        if not digits_only.startswith('55'):
            digits_only = '55' + digits_only
        
        # Se o número já tiver o código do país e o 9 do celular, retornar como está
        if len(digits_only) >= 13:
            return digits_only
        
        # Se tiver o código do país mas não tiver o 9 do celular (para números brasileiros)
        if digits_only.startswith('55') and len(digits_only) == 12:
            # Verificar se é celular (começa com 9 após o DDD)
            if digits_only[4] != '9':
                # Adicionar o 9 após o DDD para celulares brasileiros
                digits_only = digits_only[:4] + '9' + digits_only[4:]
        
        return digits_only
    
    def send_message(self, phone_number, message):
        """
        Envia uma mensagem WhatsApp usando a API Evolution.
        
        Args:
            phone_number: Número de telefone do destinatário
            message: Texto da mensagem
            
        Returns:
            Dicionário com o resultado da operação
        """
        if not self.is_configured:
            logger.error("API Evolution WhatsApp não configurada corretamente")
            return {
                'success': False,
                'status': 'not_configured',
                'error': 'API Evolution WhatsApp não configurada corretamente'
            }
        
        # Formatar o número de telefone
        formatted_number = self.format_phone_number(phone_number)
        
        # Construir URL
        url = f"{self.api_url}/message/sendText/{self.instance_id}"
        
        # Construir headers
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        # Construir payload
        payload = {
            "number": formatted_number,
            "text": message
        }
        
        try:
            logger.info(f"Enviando mensagem WhatsApp para {formatted_number}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Headers: {headers}")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Processar resposta
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    logger.info(f"Mensagem enviada com sucesso para {formatted_number}")
                    return {
                        'success': True,
                        'status': 'sent',
                        'response': response_data
                    }
                except:
                    return {
                        'success': True,
                        'status': 'sent',
                        'response': {'raw_text': response.text}
                    }
            else:
                error_message = f"Erro {response.status_code}: "
                try:
                    error_data = response.json()
                    error_message += str(error_data)
                except:
                    error_message += response.text if response.text else "Sem detalhes do erro"
                
                logger.error(f"Erro ao enviar mensagem WhatsApp: {error_message}")
                return {
                    'success': False,
                    'status': 'error',
                    'error': error_message
                }
                
        except requests.exceptions.Timeout:
            logger.error("Timeout ao conectar com a API Evolution WhatsApp")
            return {
                'success': False,
                'status': 'timeout',
                'error': 'Timeout ao conectar com a API. O servidor demorou muito para responder.'
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão com a API Evolution WhatsApp: {str(e)}")
            return {
                'success': False,
                'status': 'connection_error',
                'error': f'Erro de conexão com a API: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'error': str(e)
            }
    
    def notify_new_contact(self, message):
        """
        Notifica o gestor sobre um novo contato recebido pela landing page.
        
        Args:
            message: Objeto Message do contato recebido
            
        Returns:
            Resultado do envio da mensagem
        """
        if not self.enable_whatsapp or not self.notify_on_contact or not self.manager_whatsapp:
            logger.info("Notificação de contato desativada ou número do gestor não configurado")
            return {
                'success': False,
                'status': 'disabled',
                'error': 'Notificação de contato desativada ou número do gestor não configurado'
            }
        
        # Construir a mensagem
        notification_text = (
            f"🔔 *NOVO CONTATO RECEBIDO* 🔔\n\n"
            f"*Nome:* {message.name}\n"
            f"*Email:* {message.email}\n"
            f"*Telefone:* {message.phone if message.phone else 'Não informado'}\n"
            f"*Assunto:* {message.subject}\n\n"
            f"*Mensagem:*\n{message.message}\n\n"
            f"Recebido em: {message.created_at.strftime('%d/%m/%Y %H:%M')}"
        )
        
        # Enviar a notificação
        return self.send_message(self.manager_whatsapp, notification_text)
    
    def notify_new_registration(self, person):
        """
        Notifica o gestor sobre um novo cadastro de pessoa recebido pela landing page.
        
        Args:
            person: Objeto Person do cadastro recebido
            
        Returns:
            Resultado do envio da mensagem
        """
        if not self.enable_whatsapp or not self.notify_on_registration or not self.manager_whatsapp:
            logger.info("Notificação de cadastro desativada ou número do gestor não configurado")
            return {
                'success': False,
                'status': 'disabled',
                'error': 'Notificação de cadastro desativada ou número do gestor não configurado'
            }
        
        # Obter contatos da pessoa
        email_contact = person.contacts.filter(type='email').first()
        phone_contact = person.contacts.filter(type='whatsapp').first()
        
        email = email_contact.value if email_contact else "Não informado"
        phone = phone_contact.value if phone_contact else "Não informado"
        
        # Obter categorias profissionais
        categories = ", ".join([cat.nome for cat in person.professional_categories.all()]) if person.professional_categories.exists() else "Não informado"
        
        # Construir a mensagem
        notification_text = (
            f"🔔 *NOVO CADASTRO RECEBIDO* 🔔\n\n"
            f"*Nome:* {person.name}\n"
            f"*Telefone:* {phone}\n"
            f"*Categoria(s):* {categories}\n"
            f"*Cidade:* {person.city if person.city else 'Não informada'}\n"
            f"*Bairro:* {person.neighborhood if person.neighborhood else 'Não informado'}\n"
        )
        
        # Adicionar observações se existirem
        if person.notes:
            notification_text += f"\n*Observações:*\n{person.notes}\n"
        
        notification_text += f"\nRecebido em: {timezone.now().strftime('%d/%m/%Y %H:%M')}\n\nAcesse o sistema para mais detalhes."
        
        # Enviar a notificação
        return self.send_message(self.manager_whatsapp, notification_text)
