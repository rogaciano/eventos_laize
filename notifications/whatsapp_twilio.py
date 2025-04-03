"""
Módulo para envio de mensagens WhatsApp usando a API do Twilio.
Esta é uma alternativa à API personalizada que não está funcionando.
"""

import os
from twilio.rest import Client
from django.conf import settings
from people.models import Person, PersonContact, WhatsAppMessage

class WhatsAppTwilioManager:
    """
    Gerenciador para envio de mensagens WhatsApp usando a API do Twilio.
    Requer uma conta no Twilio e um número de WhatsApp Business.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador com as configurações do settings.py
        """
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', os.environ.get('TWILIO_ACCOUNT_SID'))
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', os.environ.get('TWILIO_AUTH_TOKEN'))
        self.from_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', os.environ.get('TWILIO_WHATSAPP_NUMBER'))
        self.manager_whatsapp = getattr(settings, 'MANAGER_WHATSAPP', None)
        self.manager_id = getattr(settings, 'MANAGER_ID', None)
        self.notify_on_registration = getattr(settings, 'NOTIFY_ON_REGISTRATION', False)
        self.notify_on_contact = getattr(settings, 'NOTIFY_ON_CONTACT', False)
        
        self.client = None
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
    
    @property
    def is_configured(self):
        """
        Verifica se as configurações necessárias estão presentes.
        """
        return self.client is not None and self.from_number is not None
    
    def format_phone_number(self, phone_number):
        """
        Formata o número de telefone para o formato esperado pelo Twilio.
        Remove caracteres não numéricos e adiciona o código do país se necessário.
        
        Args:
            phone_number: Número de telefone a ser formatado
            
        Returns:
            Número formatado para o Twilio (formato: whatsapp:+XXXXXXXXXXX)
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
        print(f"DEBUG - Número formatado: whatsapp:+{digits_only}")
        
        return f"whatsapp:+{digits_only}"
    
    def send_message(self, to_number, message):
        """
        Envia uma mensagem WhatsApp usando a API do Twilio.
        
        Args:
            to_number: Número de telefone do destinatário
            message: Texto da mensagem
            
        Returns:
            Dicionário com o resultado da operação
        """
        if not self.is_configured:
            return {'success': False, 'error': 'API do Twilio não configurada corretamente'}
        
        try:
            # Formatar números
            from_formatted = self.format_phone_number(self.from_number)
            to_formatted = self.format_phone_number(to_number)
            
            print(f"Enviando mensagem de {from_formatted} para {to_formatted}...")
            
            # Enviar mensagem via Twilio
            message_obj = self.client.messages.create(
                from_=from_formatted,
                body=message,
                to=to_formatted
            )
            
            print(f"Mensagem enviada com sucesso! SID: {message_obj.sid}")
            
            return {
                'success': True,
                'status': 'sent',
                'response': {
                    'sid': message_obj.sid,
                    'status': message_obj.status,
                    'date_created': str(message_obj.date_created)
                }
            }
            
        except Exception as e:
            print(f"Erro ao enviar mensagem: {str(e)}")
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
        
        # Enviar mensagem via Twilio
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
