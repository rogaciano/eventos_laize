"""
Módulo para envio de mensagens WhatsApp usando pywhatkit.
Esta é uma alternativa à API personalizada que não está funcionando.
"""

import os
import time
import pywhatkit
import datetime
from django.conf import settings
from people.models import Person, PersonContact, WhatsAppMessage

class WhatsAppDirectManager:
    """
    Gerenciador para envio de mensagens WhatsApp usando pywhatkit.
    Não requer API externa, usa o WhatsApp Web.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador com as configurações do settings.py
        """
        self.manager_whatsapp = getattr(settings, 'MANAGER_WHATSAPP', None)
        self.manager_id = getattr(settings, 'MANAGER_ID', None)
        self.notify_on_registration = getattr(settings, 'NOTIFY_ON_REGISTRATION', False)
        self.notify_on_contact = getattr(settings, 'NOTIFY_ON_CONTACT', False)
        self.wait_time = 15  # Tempo de espera em segundos antes de fechar
        self.close_tab = True  # Fechar a aba após enviar
    
    def format_phone_number(self, phone_number):
        """
        Formata o número de telefone para o formato esperado pelo pywhatkit.
        Remove caracteres não numéricos e adiciona o código do país se necessário.
        
        Args:
            phone_number: Número de telefone a ser formatado
            
        Returns:
            Número formatado
        """
        # Remover todos os caracteres não numéricos
        digits_only = ''.join(filter(str.isdigit, phone_number))
        
        # Se não começar com +, adicionar +
        if not digits_only.startswith('55'):
            digits_only = '55' + digits_only
            
        # Garantir que o número tenha pelo menos 10 dígitos (DDD + número)
        if len(digits_only) < 12:
            print(f"AVISO: Número de telefone {phone_number} parece estar incompleto após formatação: {digits_only}")
            
        print(f"DEBUG - Número original: {phone_number}")
        print(f"DEBUG - Número formatado: +{digits_only}")
        
        return f"+{digits_only}"
    
    def send_message(self, to_number, message):
        """
        Envia uma mensagem WhatsApp usando pywhatkit.
        
        Args:
            to_number: Número de telefone do destinatário
            message: Texto da mensagem
            
        Returns:
            Dicionário com o resultado da operação
        """
        try:
            # Formatar número
            formatted_number = self.format_phone_number(to_number)
            
            # Obter hora atual
            now = datetime.datetime.now()
            
            # Enviar mensagem (vai abrir o WhatsApp Web)
            print(f"Enviando mensagem para {formatted_number}...")
            pywhatkit.sendwhatmsg_instantly(
                phone_no=formatted_number,
                message=message,
                wait_time=self.wait_time,
                tab_close=self.close_tab
            )
            
            return {
                'success': True,
                'status': 'sent',
                'response': {'message': 'Mensagem enviada com sucesso via WhatsApp Web'}
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
        
        # Enviar mensagem via pywhatkit
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
        if not self.notify_on_registration:
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
        if not self.notify_on_contact:
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
