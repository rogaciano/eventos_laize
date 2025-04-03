import requests
import json
import os
from django.conf import settings
from people.models import Person, PersonContact, WhatsAppMessage

class WhatsAppManager:
    """
    Gerenciador de envio de mensagens WhatsApp usando a API personalizada.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador com as configurações da API.
        """
        from django.conf import settings
        
        # Configurações da API
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', None)
        self.api_user_id = getattr(settings, 'WHATSAPP_API_USER_ID', None)
        self.api_token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
        
        # Configurações do gestor
        self.manager_whatsapp = getattr(settings, 'MANAGER_WHATSAPP', None)
        self.manager_id = getattr(settings, 'MANAGER_ID', None)
        
        # Flags de notificação
        self.notify_on_registration = getattr(settings, 'NOTIFY_ON_REGISTRATION', False)
        self.notify_on_contact = getattr(settings, 'NOTIFY_ON_CONTACT', False)
    
    @property
    def is_configured(self):
        """
        Verifica se todas as configurações necessárias estão presentes.
        """
        return all([self.api_url, self.api_user_id, self.api_token])
        
    def format_phone_number(self, phone_number):
        """
        Formata o número de telefone para o formato esperado pela API.
        Remove caracteres não numéricos e adiciona o código do país se necessário.
        
        Args:
            phone_number: Número de telefone a ser formatado
            
        Returns:
            Número formatado
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
    
    def send_message(self, to_number, message):
        """
        Envia uma mensagem WhatsApp usando a API personalizada.
        
        Args:
            to_number: Número de telefone do destinatário
            message: Texto da mensagem
            
        Returns:
            Objeto de resposta da API ou None em caso de erro
        """
        if not self.is_configured:
            return {'error': 'API não configurada corretamente'}
        
        try:
            # Formatar número
            contact_id = self.format_phone_number(to_number)
            
            # Preparar URL - não adicionar /api/v1/messages pois já está na URL base
            url = f"{self.api_url}/messages"
            print(f"DEBUG - URL completa: {url}")
            print(f"DEBUG - API URL: {self.api_url}")
            print(f"DEBUG - User ID: {self.api_user_id}")
            print(f"DEBUG - Token: {'Configurado' if self.api_token else 'Não configurado'}")
            
            # Criar payload como objeto Python e converter para JSON
            payload_data = {
                "text": message,
                "type": "chat",
                "contactId": contact_id,
                "userId": self.api_user_id,
                "dontOpenTicket": "true",
                "origin": "bot"
            }
            
            # Converter para JSON corretamente
            payload = json.dumps(payload_data)
            print(f"DEBUG - Payload: {payload}")
            
            # Configurar headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_token}'
            }
            print(f"DEBUG - Headers: {headers}")
            
            # Enviar requisição
            print(f"DEBUG - Enviando requisição para: {url}")
            try:
                response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
                print(f"DEBUG - Status code: {response.status_code}")
                print(f"DEBUG - Resposta: {response.text}")
                
                # Verificar o status code
                if response.status_code == 200:
                    return {
                        'success': True,
                        'status': 'sent',
                        'response': response.json() if response.text else {}
                    }
                else:
                    error_message = f"Erro {response.status_code}: "
                    try:
                        error_data = response.json()
                        error_message += str(error_data)
                    except:
                        error_message += response.text if response.text else "Sem detalhes do erro"
                    
                    print(f"DEBUG - Erro: {error_message}")
                    return {
                        'success': False,
                        'status': 'error',
                        'error': error_message
                    }
            except requests.exceptions.Timeout:
                print(f"DEBUG - Erro: Timeout ao conectar com a API")
                return {
                    'success': False,
                    'status': 'timeout',
                    'error': 'Timeout ao conectar com a API. O servidor demorou muito para responder.'
                }
            except requests.exceptions.ConnectionError as e:
                print(f"DEBUG - Erro de conexão: {str(e)}")
                return {
                    'success': False,
                    'status': 'connection_error',
                    'error': f'Erro de conexão com a API: {str(e)}'
                }
            except Exception as e:
                print(f"DEBUG - Erro desconhecido: {str(e)}")
                return {
                    'success': False,
                    'status': 'error',
                    'error': str(e)
                }
        except Exception as e:
            print(f"DEBUG - Erro ao preparar requisição: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'error': str(e)
            }
    
    def send_whatsapp_to_contact(self, contact, message):
        """
        Envia uma mensagem WhatsApp para um contato e registra no banco de dados.
        
        Args:
            contact: Objeto PersonContact (deve ser do tipo 'whatsapp')
            message: Texto da mensagem
            
        Returns:
            Objeto WhatsAppMessage
        """
        if contact.type != 'whatsapp':
            return None
        
        # Criar registro da mensagem no banco de dados
        whatsapp_message = WhatsAppMessage(
            person=contact.person,
            contact=contact,
            message=message,
            status="sending"
        )
        
        # Enviar mensagem via API
        response = self.send_message(contact.value, message)
        
        # Atualizar o registro com a resposta
        whatsapp_message.response_data = response
        
        # Definir o status com base na resposta
        if response.get('success', False):
            whatsapp_message.status = "sent"
        else:
            whatsapp_message.status = "failed"
        
        # Salvar o registro
        whatsapp_message.save()
        
        return whatsapp_message
    
    def get_manager_contact(self):
        """
        Obtém o contato do gestor para envio de notificações.
        
        Returns:
            Objeto PersonContact do gestor ou None
        """
        # Se tiver o ID do gestor, buscar a pessoa e seu contato de WhatsApp
        if self.manager_id:
            try:
                manager = Person.objects.get(id=self.manager_id)
                contact = manager.contacts.filter(type='whatsapp').first()
                if contact:
                    return contact
            except Person.DoesNotExist:
                pass
        
        # Se tiver o número do gestor, buscar qualquer contato com esse número
        if self.manager_whatsapp:
            # Formatar o número para busca
            formatted_phone = ''.join(filter(str.isdigit, self.manager_whatsapp))
            contact = PersonContact.objects.filter(
                type='whatsapp',
                value__contains=formatted_phone
            ).first()
            
            return contact
        
        return None
    
    def notify_new_registration(self, person):
        """
        Envia uma notificação para o gestor quando uma nova pessoa se registra.
        
        Args:
            person: Objeto Person recém-registrado
            
        Returns:
            True se a notificação foi enviada com sucesso, False caso contrário
        """
        if not self.notify_on_registration or not settings.ENABLE_WHATSAPP:
            return False
        
        manager_contact = self.get_manager_contact()
        if not manager_contact:
            return False
        
        # Preparar a mensagem com os detalhes da pessoa
        message = f"""
*NOVO CADASTRO ONLINE*

Nome: {person.name}
Status: {person.get_status_display()}
"""
        
        # Adicionar contatos se disponíveis
        contacts = person.contacts.all()
        if contacts:
            message += "\n*Contatos:*\n"
            for contact in contacts:
                message += f"{contact.get_type_display()}: {contact.value}\n"
        
        # Adicionar categorias profissionais se disponíveis
        categories = person.professional_categories.all()
        if categories:
            message += "\n*Categorias Profissionais:*\n"
            message += ", ".join([cat.nome for cat in categories])
        
        # Adicionar link para visualizar o perfil completo
        message += f"\n\nPara ver o perfil completo, acesse o sistema."
        
        # Enviar a mensagem
        whatsapp_message = self.send_whatsapp_to_contact(manager_contact, message)
        
        return whatsapp_message and whatsapp_message.status == "sent"
    
    def notify_new_contact(self, contact_message):
        """
        Envia uma notificação para o gestor quando alguém envia uma mensagem de contato.
        
        Args:
            contact_message: Objeto de mensagem de contato
            
        Returns:
            True se a notificação foi enviada com sucesso, False caso contrário
        """
        if not self.notify_on_contact or not settings.ENABLE_WHATSAPP:
            return False
        
        manager_contact = self.get_manager_contact()
        if not manager_contact:
            return False
        
        # Preparar a mensagem com os detalhes do contato
        message = f"""
*NOVA MENSAGEM DE CONTATO*

Nome: {contact_message.name}
Email: {contact_message.email}
Telefone: {contact_message.phone if hasattr(contact_message, 'phone') and contact_message.phone else 'Não informado'}

*Mensagem:*
{contact_message.message}

Data: {contact_message.created_at.strftime('%d/%m/%Y %H:%M')}
"""
        
        # Enviar a mensagem
        whatsapp_message = self.send_whatsapp_to_contact(manager_contact, message)
        
        return whatsapp_message and whatsapp_message.status == "sent"


# Função auxiliar para envio de mensagem WhatsApp
def send_whatsapp_message(contact, message):
    """
    Função auxiliar para enviar uma mensagem WhatsApp.
    Mantém a mesma assinatura da função original para compatibilidade.
    
    Args:
        contact: Objeto PersonContact (deve ser do tipo 'whatsapp')
        message: Texto da mensagem
        
    Returns:
        Objeto WhatsAppMessage
    """
    manager = WhatsAppManager()
    return manager.send_whatsapp_to_contact(contact, message)
