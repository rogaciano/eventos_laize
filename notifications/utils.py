import os
from django.conf import settings
from people.models import Person, PersonContact
from people.utils import send_whatsapp_message

def get_manager_whatsapp_contact():
    """
    Recupera o contato de WhatsApp do gestor configurado nas variáveis de ambiente.
    Retorna um objeto PersonContact se encontrado, None caso contrário.
    """
    manager_phone = os.getenv('MANAGER_WHATSAPP', None)
    manager_id = os.getenv('MANAGER_ID', None)
    
    if not manager_phone and not manager_id:
        return None
    
    # Se tiver o ID do gestor, busca a pessoa e seu contato de WhatsApp
    if manager_id:
        try:
            manager = Person.objects.get(id=manager_id)
            contact = manager.contacts.filter(type='whatsapp').first()
            if contact:
                return contact
        except Person.DoesNotExist:
            pass
    
    # Se tiver o telefone do gestor mas não encontrou a pessoa ou o contato,
    # tenta encontrar qualquer contato com esse número
    if manager_phone:
        # Formata o número para busca (remove caracteres não numéricos)
        formatted_phone = ''.join(filter(str.isdigit, manager_phone))
        contact = PersonContact.objects.filter(
            type='whatsapp',
            value__contains=formatted_phone
        ).first()
        
        return contact
    
    return None

def notify_manager_new_registration(person):
    """
    Envia uma notificação para o gestor quando uma nova pessoa se registra online.
    
    Args:
        person: Objeto Person recém-registrado
    
    Returns:
        True se a notificação foi enviada com sucesso, False caso contrário
    """
    if not settings.ENABLE_WHATSAPP:
        return False
    
    manager_contact = get_manager_whatsapp_contact()
    if not manager_contact:
        return False
    
    # Prepara a mensagem com os detalhes da pessoa
    message = f"""
*NOVO CADASTRO ONLINE*

Nome: {person.name}
Status: {person.get_status_display()}
"""
    
    # Adiciona contatos se disponíveis
    contacts = person.contacts.all()
    if contacts:
        message += "\n*Contatos:*\n"
        for contact in contacts:
            message += f"{contact.get_type_display()}: {contact.value}\n"
    
    # Adiciona categorias profissionais se disponíveis
    categories = person.professional_categories.all()
    if categories:
        message += "\n*Categorias Profissionais:*\n"
        message += ", ".join([cat.nome for cat in categories])
    
    # Adiciona link para visualizar o perfil completo
    message += f"\n\nPara ver o perfil completo, acesse o sistema."
    
    # Envia a mensagem
    whatsapp_message = send_whatsapp_message(manager_contact, message)
    
    return whatsapp_message and whatsapp_message.status == "sent"

def notify_manager_new_contact(contact_message):
    """
    Envia uma notificação para o gestor quando alguém entra em contato pelo formulário.
    
    Args:
        contact_message: Objeto de mensagem de contato
    
    Returns:
        True se a notificação foi enviada com sucesso, False caso contrário
    """
    if not settings.ENABLE_WHATSAPP:
        return False
    
    manager_contact = get_manager_whatsapp_contact()
    if not manager_contact:
        return False
    
    # Prepara a mensagem com os detalhes do contato
    message = f"""
*NOVA MENSAGEM DE CONTATO*

Nome: {contact_message.name}
Email: {contact_message.email}
Telefone: {contact_message.phone if hasattr(contact_message, 'phone') else 'Não informado'}

*Mensagem:*
{contact_message.message}

Data: {contact_message.created_at.strftime('%d/%m/%Y %H:%M')}
"""
    
    # Envia a mensagem
    whatsapp_message = send_whatsapp_message(manager_contact, message)
    
    return whatsapp_message and whatsapp_message.status == "sent"
