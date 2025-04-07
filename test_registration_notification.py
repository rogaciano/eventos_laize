import os
import sys
import django
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventos.settings')
django.setup()

# Importar após configurar o ambiente Django
from notifications.evolution_whatsapp import EvolutionWhatsAppService
from people.models import Person, PersonContact, ProfessionalCategory
from django.utils import timezone

def test_registration_notification():
    """
    Testa o envio de notificação para um novo cadastro na equipe
    """
    print("=== TESTE DE NOTIFICAÇÃO DE CADASTRO ===")
    
    # Criar uma categoria profissional para teste (se não existir)
    category, created = ProfessionalCategory.objects.get_or_create(
        nome="Modelo Fotográfico",
        defaults={"descricao": "Categoria para teste de notificação"}
    )
    
    # Criar uma pessoa de teste
    person = Person(
        name="Candidato de Teste",
        status="pendente",
        origem_cadastro="externo",
        city="Recife",
        neighborhood="Boa Viagem",
        notes="Tenho experiência com eventos corporativos e estou disponível para trabalhos nos finais de semana.",
        altura=1.75,
    )
    person.save()
    
    # Adicionar categoria profissional
    person.professional_categories.add(category)
    
    # Adicionar contatos
    email_contact = PersonContact.objects.create(
        person=person,
        type='email',
        value='teste@example.com',
        label='Principal'
    )
    
    phone_contact = PersonContact.objects.create(
        person=person,
        type='whatsapp',
        value='5581999216560',
        label='Principal'
    )
    
    # Enviar notificação
    service = EvolutionWhatsAppService()
    
    # Verificar configurações do serviço
    print("\n=== CONFIGURAÇÕES DO SERVIÇO ===")
    print(f"API URL: {service.api_url}")
    print(f"API Key: {service.api_key}")
    print(f"Instance ID: {service.instance_id}")
    print(f"Enable WhatsApp: {service.enable_whatsapp}")
    print(f"Notify on Registration: {service.notify_on_registration}")
    print(f"Número do gestor: {service.manager_whatsapp}")
    print(f"Serviço configurado: {service.is_configured}")
    
    # Enviar notificação
    print("\n=== TESTE DE NOTIFICAÇÃO ===")
    print("Enviando notificação...")
    result = service.notify_new_registration(person)
    
    # Exibir resultado
    print("\n=== RESULTADO ===")
    print(f"Sucesso: {'Sim' if result.get('success') else 'Não'}")
    print(f"Status: {result.get('status')}")
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")
    else:
        print("Mensagem enviada com sucesso!")
        print(f"Detalhes da resposta: {result.get('response')}")
    
    # Limpar dados de teste
    print("\n=== LIMPANDO DADOS DE TESTE ===")
    phone_contact.delete()
    email_contact.delete()
    person.delete()
    print("Dados de teste removidos com sucesso!")

if __name__ == "__main__":
    # Executar teste
    test_registration_notification()
