import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from events.models import Event, EventType, Funcao, EventParticipant
from events.models_cost import CostCategory, EventCost
from clients.models import Client
from people.models import Person


class Command(BaseCommand):
    help = 'Cria eventos de teste com participantes e custos'

    def add_arguments(self, parser):
        parser.add_argument('--num', type=int, default=10, help='Número de eventos a serem criados')

    @transaction.atomic
    def handle(self, *args, **options):
        num_events = options['num']
        
        # Verifica se existem dados necessários
        if not EventType.objects.exists():
            self.stdout.write(self.style.ERROR('Nenhum tipo de evento encontrado. Por favor, crie pelo menos um tipo de evento.'))
            return
        
        if not CostCategory.objects.exists():
            self.stdout.write(self.style.ERROR('Nenhuma categoria de custo encontrada. Por favor, crie pelo menos uma categoria de custo.'))
            return
        
        if not Client.objects.exists():
            self.stdout.write(self.style.ERROR('Nenhum cliente encontrado. Por favor, crie pelo menos um cliente.'))
            return
        
        if not Person.objects.exists():
            self.stdout.write(self.style.ERROR('Nenhuma pessoa encontrada. Por favor, crie pelo menos uma pessoa.'))
            return
        
        if not Funcao.objects.exists():
            self.stdout.write(self.style.ERROR('Nenhuma função encontrada. Por favor, crie pelo menos uma função.'))
            return
        
        # Obter dados existentes
        event_types = list(EventType.objects.all())
        cost_categories = list(CostCategory.objects.all())
        clients = list(Client.objects.all())
        people = list(Person.objects.all())
        funcoes = list(Funcao.objects.all())
        
        # Status possíveis para os eventos
        status_choices = [
            'cadastrado', 'prospectado', 'agendado', 'em_andamento', 
            'concluido', 'cancelado', 'adiado', 'pendente', 
            'orcamento', 'pre_producao', 'pos_producao'
        ]
        
        # Locais possíveis para os eventos
        locations = [
            'Centro de Convenções de Caruaru', 'Praça 18 de Maio', 'Shopping Caruaru',
            'Parque Maurício de Nassau', 'Teatro Rui Limeira Rosal', 'SESC Caruaru',
            'Polo Comercial de Caruaru', 'Universidade Federal de Pernambuco (UFPE)',
            'Associação Comercial e Industrial de Caruaru (ACIC)', 'Hotel WA'
        ]
        
        events_created = 0
        
        # Criar eventos
        for i in range(num_events):
            # Determinar se o evento é passado, presente ou futuro
            event_time_type = random.choice(['past', 'present', 'future'])
            
            now = timezone.now()
            
            if event_time_type == 'past':
                # Evento no passado (1 a 180 dias atrás)
                days_ago = random.randint(1, 180)
                start_date = now - timedelta(days=days_ago)
                status = random.choice(['concluido', 'cancelado', 'arquivado'])
            elif event_time_type == 'present':
                # Evento atual (hoje até 7 dias à frente)
                days_ahead = random.randint(0, 7)
                start_date = now + timedelta(days=days_ahead)
                status = random.choice(['agendado', 'em_andamento', 'pre_producao'])
            else:
                # Evento futuro (8 a 180 dias à frente)
                days_ahead = random.randint(8, 180)
                start_date = now + timedelta(days=days_ahead)
                status = random.choice(['cadastrado', 'prospectado', 'agendado', 'pendente', 'orcamento'])
            
            # Duração do evento (1 a 5 dias)
            duration_days = random.randint(1, 5)
            end_date = start_date + timedelta(days=duration_days)
            
            # Valor do evento
            value = Decimal(str(random.randint(5000, 50000)))
            
            # Criar o evento
            event = Event.objects.create(
                title=f"Evento Teste {i+1} - {random.choice(['Workshop', 'Feira', 'Congresso', 'Seminário', 'Exposição'])}",
                start_datetime=start_date,
                end_datetime=end_date,
                client=random.choice(clients),
                value=value,
                location=random.choice(locations),
                event_type=random.choice(event_types),
                status=status,
                description=f"Este é um evento de teste gerado automaticamente. Evento número {i+1} de {num_events}."
            )
            
            # Adicionar participantes (entre 3 e 15)
            num_participants = random.randint(3, 15)
            selected_people = random.sample(people, min(num_participants, len(people)))
            
            for person in selected_people:
                funcao = random.choice(funcoes)
                # Usar o valor padrão da função ou um valor aleatório
                if funcao.valor_padrao:
                    value = funcao.valor_padrao
                else:
                    value = Decimal(str(random.randint(80, 200)))
                
                EventParticipant.objects.create(
                    event=event,
                    person=person,
                    role=funcao,
                    value=value,
                    observations=f"Participante de teste para o evento {event.title}"
                )
            
            # Adicionar custos (entre 2 e 8)
            num_costs = random.randint(2, 8)
            
            for j in range(num_costs):
                cost_category = random.choice(cost_categories)
                
                # Determinar se é orçamento ou custo real
                cost_type = random.choice(['budget', 'actual'])
                
                # Valor do custo
                amount = Decimal(str(random.randint(100, 5000)))
                
                # Data do custo
                if cost_type == 'budget':
                    # Orçamento geralmente é feito antes do evento
                    cost_date = start_date - timedelta(days=random.randint(1, 30))
                else:
                    # Custo real pode ser antes ou durante o evento
                    if event_time_type == 'past':
                        cost_date = start_date + timedelta(days=random.randint(0, duration_days))
                    else:
                        cost_date = start_date - timedelta(days=random.randint(1, 7))
                
                # Status de pagamento
                paid = random.choice([True, False])
                if event_time_type == 'past' and cost_type == 'actual':
                    # Eventos passados têm maior probabilidade de custos pagos
                    paid = random.choices([True, False], weights=[0.8, 0.2])[0]
                
                EventCost.objects.create(
                    event=event,
                    category=cost_category,
                    description=f"Custo {j+1} para {event.title} - {cost_category.name}",
                    amount=amount,
                    cost_type=cost_type,
                    date=cost_date.date(),
                    paid=paid,
                    notes=f"Custo de teste para o evento {event.title}"
                )
            
            events_created += 1
            self.stdout.write(self.style.SUCCESS(f'Evento criado: {event.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total de {events_created} eventos criados com sucesso!'))
