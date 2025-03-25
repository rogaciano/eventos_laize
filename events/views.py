from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
import json
from .models import Event, EventType, EventParticipant, Funcao, EventStatusHistory
from people.models import Person
from .forms import EventForm, EventTypeForm, EventParticipantForm, FuncaoForm, EventStatusHistoryForm
from django.db.models import ProtectedError, Q

# Event views
def event_list(request):
    events = Event.objects.all().order_by('-start_datetime')
    event_types = EventType.objects.all()
    
    # Processar filtros
    search = request.GET.get('search', '')
    type_id = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    if search:
        events = events.filter(
            Q(title__icontains=search) | 
            Q(client__name__icontains=search) |
            Q(location__icontains=search)
        )
    
    if type_id:
        events = events.filter(event_type_id=type_id)
    
    if status:
        events = events.filter(status=status)
    
    return render(request, 'events/event_list.html', {
        'events': events,
        'event_types': event_types
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participants = event.eventparticipant_set.all()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'participants': participants
    })

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            
            # Criar o primeiro registro de histórico de status
            EventStatusHistory.objects.create(
                event=event,
                new_status='cadastrado',
                description='Evento cadastrado no sistema',
                created_by=request.user.username if request.user.is_authenticated else 'Sistema'
            )
            
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventForm()
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Novo Evento'
    })

def event_update(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'event': event,
        'title': 'Editar Evento'
    })

def event_delete(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('events:list')
    
    return render(request, 'events/event_confirm_delete.html', {'event': event})

# Event Type views
def event_type_list(request):
    event_types = EventType.objects.all()
    return render(request, 'events/event_type_list.html', {'event_types': event_types})

def event_type_create(request):
    if request.method == 'POST':
        form = EventTypeForm(request.POST)
        if form.is_valid():
            event_type = form.save()
            messages.success(request, 'Tipo de evento criado com sucesso!')
            return redirect('events:type_list')
    else:
        form = EventTypeForm()
    
    return render(request, 'events/event_type_form.html', {
        'form': form,
        'title': 'Novo Tipo de Evento'
    })

def event_type_update(request, type_id):
    event_type = get_object_or_404(EventType, pk=type_id)
    
    if request.method == 'POST':
        form = EventTypeForm(request.POST, instance=event_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de evento atualizado com sucesso!')
            return redirect('events:type_list')
    else:
        form = EventTypeForm(instance=event_type)
    
    return render(request, 'events/event_type_form.html', {
        'form': form,
        'event_type': event_type,
        'title': 'Editar Tipo de Evento'
    })

def event_type_delete(request, type_id):
    event_type = get_object_or_404(EventType, pk=type_id)
    
    if request.method == 'POST':
        if Event.objects.filter(event_type=event_type).exists():
            messages.error(request, 'Não é possível excluir esse tipo de evento pois existem eventos associados a ele.')
            return redirect('events:type_list')
        
        event_type.delete()
        messages.success(request, 'Tipo de evento excluído com sucesso!')
        return redirect('events:type_list')
    
    return render(request, 'events/event_type_confirm_delete.html', {'event_type': event_type})

# Event Participant views
def add_participant(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventParticipantForm(request.POST)
        if form.is_valid():
            person = form.cleaned_data['person']
            
            # Verificar conflitos de horário
            conflicting_events = Event.objects.filter(
                eventparticipant__person=person,
                start_datetime__lt=event.end_datetime,
                end_datetime__gt=event.start_datetime
            ).exclude(id=event.id)
            
            if conflicting_events.exists():
                # Há conflito de horário
                conflict_details = []
                for conflicting_event in conflicting_events:
                    conflict_details.append(
                        f"{conflicting_event.title} "
                        f"({conflicting_event.start_datetime.strftime('%d/%m/%Y %H:%M')} - "
                        f"{conflicting_event.end_datetime.strftime('%d/%m/%Y %H:%M')})"
                    )
                
                conflict_message = "Conflito de horário detectado. Esta pessoa já está em outro(s) evento(s) neste horário:<br>"
                conflict_message += "<ul>"
                for detail in conflict_details:
                    conflict_message += f"<li>{detail}</li>"
                conflict_message += "</ul>"
                conflict_message += "Deseja adicionar mesmo assim?"
                
                # Passar os dados do formulário e a mensagem de conflito para a confirmação
                return render(request, 'events/participant_conflict.html', {
                    'form': form,
                    'event': event,
                    'conflict_message': conflict_message,
                    'person': person
                })
            
            # Se não houver conflito ou o usuário confirmou, salvar o participante
            participant = form.save(commit=False)
            participant.event = event
            participant.save()
            messages.success(request, 'Participante adicionado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        # Get people who are not already participants
        existing_participant_ids = event.eventparticipant_set.values_list('person_id', flat=True)
        form = EventParticipantForm()
        form.fields['person'].queryset = Person.objects.exclude(id__in=existing_participant_ids)
    
    return render(request, 'events/participant_form.html', {
        'form': form,
        'event': event
    })

def confirm_add_participant(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.event = event
            participant.save()
            messages.success(request, 'Participante adicionado com sucesso, mesmo com conflito de horário!')
            return redirect('events:detail', event_id=event.id)
    
    return redirect('events:add_participant', event_id=event_id)

def remove_participant(request, event_id, participant_id):
    event = get_object_or_404(Event, pk=event_id)
    participant = get_object_or_404(EventParticipant, pk=participant_id, event=event)
    
    if request.method == 'POST':
        participant.delete()
        messages.success(request, 'Participante removido com sucesso!')
        return redirect('events:detail', event_id=event.id)
    
    return render(request, 'events/participant_confirm_delete.html', {
        'event': event,
        'participant': participant
    })

def update_participant(request, event_id, participant_id):
    event = get_object_or_404(Event, pk=event_id)
    participant = get_object_or_404(EventParticipant, pk=participant_id, event=event)
    
    if request.method == 'POST':
        form = EventParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participante atualizado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventParticipantForm(instance=participant)
    
    return render(request, 'events/participant_form.html', {
        'form': form,
        'event': event,
        'participant': participant,
        'is_update': True
    })

def funcao_create(request):
    if request.method == 'POST':
        form = FuncaoForm(request.POST)
        if form.is_valid():
            funcao = form.save()
            return JsonResponse({
                'id': funcao.id,
                'nome': funcao.nome,
                'valor_padrao': str(funcao.valor_padrao) if funcao.valor_padrao else '',
                'success': True,
                'message': 'Função adicionada com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Erro ao adicionar função. Por favor, verifique os dados.'
            })
    else:
        # Como agora usamos um modal na mesma tela, não precisamos mais renderizar o template
        # Retornamos apenas um JSON vazio para requisições GET
        return JsonResponse({'success': False, 'message': 'Método não permitido'})

def funcao_valor_padrao(request, funcao_id):
    """Retorna o valor padrão de uma função."""
    try:
        funcao = Funcao.objects.get(id=funcao_id)
        return JsonResponse({
            'success': True,
            'valor_padrao': str(funcao.valor_padrao) if funcao.valor_padrao else ''
        })
    except Funcao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Função não encontrada'
        })

def funcao_list(request):
    """Lista todas as funções cadastradas."""
    funcoes = Funcao.objects.all().order_by('nome')
    return render(request, 'events/funcao_list.html', {'funcoes': funcoes})

def funcao_create_page(request):
    """Cria uma nova função a partir da página de listagem."""
    if request.method == 'POST':
        form = FuncaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Função adicionada com sucesso!')
            return redirect('events:funcao_list')
    else:
        form = FuncaoForm()
    
    return render(request, 'events/funcao_create.html', {'form': form})

def funcao_edit(request, funcao_id):
    """Edita uma função existente."""
    funcao = get_object_or_404(Funcao, id=funcao_id)
    
    if request.method == 'POST':
        form = FuncaoForm(request.POST, instance=funcao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Função atualizada com sucesso!')
            return redirect('events:funcao_list')
    else:
        form = FuncaoForm(instance=funcao)
    
    return render(request, 'events/funcao_edit.html', {'form': form, 'funcao': funcao})

def funcao_delete(request, funcao_id):
    """Exclui uma função."""
    funcao = get_object_or_404(Funcao, id=funcao_id)
    
    if request.method == 'POST':
        try:
            funcao.delete()
            messages.success(request, 'Função excluída com sucesso!')
        except ProtectedError:
            messages.error(request, 'Não é possível excluir esta função pois ela está sendo utilizada por participantes.')
        return redirect('events:funcao_list')
    
    return render(request, 'events/funcao_confirm_delete.html', {'funcao': funcao})

# Event Status History views
def event_status_history(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    history = event.status_history.all()
    
    return render(request, 'events/event_status_history.html', {
        'event': event,
        'history': history
    })

def change_event_status(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventStatusHistoryForm(request.POST)
        if form.is_valid():
            # Criar o registro de histórico
            status_history = form.save(commit=False)
            status_history.event = event
            status_history.old_status = event.status
            status_history.created_by = request.user.username if request.user.is_authenticated else 'Sistema'
            status_history.save()
            
            # Atualizar o status do evento
            event.status = form.cleaned_data['new_status']
            event.save()
            
            messages.success(request, 'Status do evento atualizado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        form = EventStatusHistoryForm(initial={'new_status': event.status})
    
    return render(request, 'events/change_event_status.html', {
        'form': form,
        'event': event
    })

# Calendário de eventos
def event_calendar(request):
    """
    Exibe um calendário mensal com todos os eventos.
    """
    return render(request, 'events/event_calendar.html')

def event_calendar_data(request):
    """
    Retorna os dados dos eventos em formato JSON para o calendário.
    """
    events = Event.objects.all()
    calendar_events = []
    
    for event in events:
        # Definir cores com base no status do evento
        color_map = {
            'cadastrado': '#6c757d',  # cinza
            'prospectado': '#17a2b8',  # ciano
            'agendado': '#007bff',  # azul
            'em_andamento': '#fd7e14',  # laranja
            'concluido': '#28a745',  # verde
            'cancelado': '#dc3545',  # vermelho
            'adiado': '#6610f2',  # roxo
            'pendente': '#ffc107',  # amarelo
            'orcamento': '#20c997',  # teal
            'pre_producao': '#e83e8c',  # rosa
            'pos_producao': '#6f42c1',  # indigo
            'arquivado': '#343a40',  # preto
        }
        
        color = color_map.get(event.status, '#007bff')
        
        # Obter participantes
        participants = event.eventparticipant_set.all()
        participant_list = [f"{p.person.name} ({p.role.nome if p.role else 'Sem função'})" for p in participants]
        
        calendar_events.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'color': color,
            'url': f'/sistema/events/{event.id}/',
            'extendedProps': {
                'client': event.client.name,
                'location': event.location or 'Não informado',
                'status': dict(Event.STATUS_CHOICES).get(event.status, ''),
                'participants': participant_list,
                'description': event.description or 'Sem descrição'
            }
        })
    
    return JsonResponse(calendar_events, safe=False)
