from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
import json
from .models import Event, EventType, EventParticipant, Funcao, EventStatusHistory, EventGallery
from people.models import Person
from .forms import EventForm, EventTypeForm, EventParticipantForm, FuncaoForm, EventStatusHistoryForm, EventGalleryForm, EventCostForm, EventBudgetItemForm, BudgetSettingsForm, CompanySettingsForm, DefaultBudgetSettingsForm
from .models_cost import EventCost, CostCategory
from .models_budget import EventBudgetItem, BudgetSettings, DefaultBudgetSettings
from .models_company import CompanySettings
from django.db.models import ProtectedError, Q, Count, Sum
from django.core.paginator import Paginator
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.utils import timezone

# Event views
def event_list(request):
    """View para listar eventos"""
    # Filtros
    search_query = request.GET.get('search', '')
    event_type_id = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    # Query base
    events = Event.objects.all().order_by('-start_datetime')
    
    # Aplicar filtros
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(client__name__icontains=search_query)
        )
    
    if event_type_id:
        events = events.filter(event_type_id=event_type_id)
    
    if status:
        events = events.filter(status=status)
    
    # Prefetch related para otimizar consultas
    events = events.select_related('client', 'event_type')
    
    # Obter todos os eventos que têm fotos na galeria
    events_with_gallery = set(EventGallery.objects.values_list('event_id', flat=True).distinct())
    
    # Contar o número de fotos por evento
    gallery_counts = {}
    for event_id, count in EventGallery.objects.values_list('event_id').annotate(count=Count('id')):
        gallery_counts[event_id] = count
    
    # Paginação
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Adicionar informações da galeria aos eventos
    for event in page_obj:
        event.has_gallery = event.id in events_with_gallery
        event.gallery_count = gallery_counts.get(event.id, 0)
    
    # Tipos de evento para o filtro
    event_types = EventType.objects.all().order_by('name')
    
    context = {
        'events': page_obj,
        'event_types': event_types,
        'page_obj': page_obj,
    }
    return render(request, 'events/event_list.html', context)

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
            
            # Verificar se a pessoa está ativa
            if person.status != 'ativo':
                messages.error(request, f'Não é possível adicionar {person.name} ao evento. Apenas pessoas com status "Ativo" podem ser adicionadas.')
                return redirect('events:add_participant', event_id=event.id)
            
            # Verificar conflitos de horário
            conflicting_events = Event.objects.filter(
                eventparticipant__person=person,
                start_datetime__lt=event.end_datetime,
                end_datetime__gt=event.start_datetime
            ).exclude(id=event.id)
            
            if conflicting_events.exists():
                # Há conflito de horário
                conflicting_event = conflicting_events.first()
                
                # Passar os dados do formulário e a informação do conflito para a confirmação
                return render(request, 'events/participant_conflict.html', {
                    'form': form,
                    'event': event,
                    'conflicting_event': conflicting_event,
                    'person': person
                })
            
            # Se não houver conflito ou o usuário confirmou, salvar o participante
            participant = form.save(commit=False)
            participant.event = event
            participant.save()
            messages.success(request, 'Participante adicionado com sucesso!')
            return redirect('events:detail', event_id=event.id)
    else:
        # Get people who are not already participants and estão ativos
        existing_participant_ids = event.eventparticipant_set.values_list('person_id', flat=True)
        form = EventParticipantForm()
        form.fields['person'].queryset = Person.objects.filter(status='ativo').exclude(id__in=existing_participant_ids)
    
    return render(request, 'events/participant_form.html', {
        'form': form,
        'event': event
    })

def confirm_add_participant(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventParticipantForm(request.POST)
        if form.is_valid():
            person = form.cleaned_data['person']
            
            # Verificar se a pessoa está ativa
            if person.status != 'ativo':
                messages.error(request, f'Não é possível adicionar {person.name} ao evento. Apenas pessoas com status "Ativo" podem ser adicionadas.')
                return redirect('events:detail', event_id=event.id)
            
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

# Cost views
def event_costs(request, event_id):
    """View para exibir os custos de um evento"""
    event = get_object_or_404(Event, pk=event_id)
    costs = EventCost.objects.filter(event=event).order_by('-created_at')
    
    context = {
        'event': event,
        'costs': costs,
        'title': f'Custos: {event.title}',
        'subtitle': 'Gerenciar custos do evento'
    }
    return render(request, 'events/event_costs.html', context)

def event_cost_add(request, event_id):
    """View para adicionar um novo custo ao evento"""
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventCostForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.event = event
            cost.save()
            messages.success(request, "Custo adicionado com sucesso!")
            return redirect('events:event_costs', event_id=event.id)
    else:
        form = EventCostForm()
    
    context = {
        'form': form,
        'event': event,
        'title': f'Adicionar Custo: {event.title}',
        'subtitle': 'Adicionar novo custo ao evento'
    }
    return render(request, 'events/event_cost_form.html', context)

def event_cost_edit(request, event_id, cost_id):
    """View para editar um custo de evento"""
    event = get_object_or_404(Event, pk=event_id)
    cost = get_object_or_404(EventCost, pk=cost_id, event=event)
    
    if request.method == 'POST':
        form = EventCostForm(request.POST, instance=cost)
        if form.is_valid():
            form.save()
            messages.success(request, "Custo atualizado com sucesso!")
            return redirect('events:event_costs', event_id=event.id)
    else:
        form = EventCostForm(instance=cost)
    
    context = {
        'form': form,
        'event': event,
        'cost': cost,
        'title': f'Editar Custo: {event.title}',
        'subtitle': 'Atualizar informações do custo'
    }
    return render(request, 'events/event_cost_form.html', context)

def event_cost_delete(request, event_id, cost_id):
    """View para excluir um custo de evento"""
    event = get_object_or_404(Event, pk=event_id)
    cost = get_object_or_404(EventCost, pk=cost_id, event=event)
    
    if request.method == 'POST':
        cost.delete()
        messages.success(request, "Custo excluído com sucesso!")
        return redirect('events:event_costs', event_id=event.id)
    
    return render(request, 'events/event_cost_confirm_delete.html', {
        'event': event,
        'cost': cost,
        'title': 'Excluir Custo',
        'subtitle': f'Confirmar exclusão do custo: {cost.description}'
    })

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

# Gallery views
def event_gallery(request, event_id):
    """View para exibir e gerenciar a galeria de fotos de um evento"""
    event = get_object_or_404(Event, pk=event_id)
    gallery_items = EventGallery.objects.filter(event=event).order_by('order', 'created_at')
    
    context = {
        'event': event,
        'gallery_items': gallery_items,
        'title': f'Galeria de Fotos: {event.title}',
        'subtitle': 'Gerenciar fotos da galeria'
    }
    return render(request, 'events/event_gallery.html', context)

def event_gallery_add(request, event_id):
    """View para adicionar uma nova foto à galeria"""
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_item = form.save(commit=False)
            gallery_item.event = event
            gallery_item.save()
            messages.success(request, "Foto adicionada à galeria com sucesso!")
            return redirect('events:event_gallery', event_id=event.id)
    else:
        form = EventGalleryForm()
    
    context = {
        'form': form,
        'event': event,
        'title': f'Adicionar Foto: {event.title}',
        'subtitle': 'Adicionar nova foto à galeria'
    }
    return render(request, 'events/event_gallery_form.html', context)

def event_gallery_edit(request, event_id, gallery_id):
    """View para editar uma foto da galeria"""
    event = get_object_or_404(Event, pk=event_id)
    gallery_item = get_object_or_404(EventGallery, pk=gallery_id, event=event)
    
    if request.method == 'POST':
        form = EventGalleryForm(request.POST, request.FILES, instance=gallery_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Foto da galeria atualizada com sucesso!")
            return redirect('events:event_gallery', event_id=event.id)
    else:
        form = EventGalleryForm(instance=gallery_item)
    
    context = {
        'form': form,
        'event': event,
        'gallery_item': gallery_item,
        'title': f'Editar Foto: {event.title}',
        'subtitle': 'Atualizar informações da foto'
    }
    return render(request, 'events/event_gallery_form.html', context)

def event_gallery_delete(request, event_id, gallery_id):
    """View para excluir uma foto da galeria"""
    event = get_object_or_404(Event, pk=event_id)
    gallery_item = get_object_or_404(EventGallery, pk=gallery_id, event=event)
    
    if request.method == 'POST':
        gallery_item.delete()
        messages.success(request, "Foto removida da galeria com sucesso!")
        return redirect('events:event_gallery', event_id=event.id)
    
    context = {
        'event': event,
        'gallery_item': gallery_item,
        'title': f'Excluir Foto: {event.title}',
        'subtitle': 'Confirmar exclusão da foto'
    }
    return render(request, 'events/event_gallery_confirm_delete.html', context)

# Budget views
def event_budget(request, event_id):
    """View para gerenciar orçamento de um evento"""
    event = get_object_or_404(Event, pk=event_id)
    budget_items = EventBudgetItem.objects.filter(event=event).order_by('date', 'start_time')
    
    # Obter ou criar configurações de orçamento
    budget_settings, created = BudgetSettings.objects.get_or_create(event=event)
    
    # Calcular o total do orçamento corretamente
    total = sum(item.quantity * item.unit_value for item in budget_items)
    
    context = {
        'event': event,
        'budget_items': budget_items,
        'budget_settings': budget_settings,
        'total': total,
    }
    return render(request, 'events/event_budget.html', context)


def event_budget_item_add(request, event_id):
    """View para adicionar um item ao orçamento"""
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventBudgetItemForm(request.POST)
        if form.is_valid():
            budget_item = form.save(commit=False)
            budget_item.event = event
            budget_item.save()
            messages.success(request, 'Item adicionado ao orçamento com sucesso!')
            return redirect('events:event_budget', event_id=event.id)
    else:
        # Gerar código automático baseado na quantidade de itens existentes
        next_code = EventBudgetItem.objects.filter(event=event).count() + 1
        form = EventBudgetItemForm(initial={'code': f'0{next_code}'})
    
    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'events/event_budget_item_form.html', context)


def event_budget_item_edit(request, event_id, item_id):
    """View para editar um item do orçamento"""
    event = get_object_or_404(Event, pk=event_id)
    budget_item = get_object_or_404(EventBudgetItem, pk=item_id, event=event)
    
    if request.method == 'POST':
        form = EventBudgetItemForm(request.POST, instance=budget_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item do orçamento atualizado com sucesso!')
            return redirect('events:event_budget', event_id=event.id)
    else:
        # Preparar dados iniciais para garantir que a data seja exibida corretamente
        initial_data = {
            'code': budget_item.code,
            'description': budget_item.description,
            'date': budget_item.date,
            'start_time': budget_item.start_time,
            'end_time': budget_item.end_time,
            'quantity': budget_item.quantity,
            'unit_value': budget_item.unit_value,
        }
        form = EventBudgetItemForm(instance=budget_item, initial=initial_data)
    
    context = {
        'event': event,
        'form': form,
        'budget_item': budget_item,
    }
    return render(request, 'events/event_budget_item_form.html', context)


def event_budget_item_delete(request, event_id, item_id):
    """View para excluir um item do orçamento"""
    event = get_object_or_404(Event, pk=event_id)
    budget_item = get_object_or_404(EventBudgetItem, pk=item_id, event=event)
    
    if request.method == 'POST':
        budget_item.delete()
        messages.success(request, 'Item do orçamento excluído com sucesso!')
        return redirect('events:event_budget', event_id=event.id)
    
    context = {
        'event': event,
        'budget_item': budget_item,
    }
    return render(request, 'events/event_budget_item_confirm_delete.html', context)


def event_budget_settings(request, event_id):
    """View para configurar as opções do orçamento"""
    event = get_object_or_404(Event, pk=event_id)
    
    # Obter ou criar configurações de orçamento
    try:
        budget_settings = BudgetSettings.objects.get(event=event)
        is_new = False
    except BudgetSettings.DoesNotExist:
        # Criar a partir das configurações padrão
        budget_settings = BudgetSettings.create_from_default(event)
        is_new = True
    
    # Obter as configurações padrão
    default_settings = DefaultBudgetSettings.get_default()
    
    # Verificar se algum campo está vazio e preencher com valor padrão
    fields_updated = False
    
    if not budget_settings.payment_terms and default_settings.payment_terms:
        budget_settings.payment_terms = default_settings.payment_terms
        fields_updated = True
    
    if not budget_settings.validity_days and default_settings.validity_days:
        budget_settings.validity_days = default_settings.validity_days
        fields_updated = True
    
    if not budget_settings.client_responsibilities and default_settings.client_responsibilities:
        budget_settings.client_responsibilities = default_settings.client_responsibilities
        fields_updated = True
    
    if not budget_settings.additional_notes and default_settings.additional_notes:
        budget_settings.additional_notes = default_settings.additional_notes
        fields_updated = True
    
    # Se algum campo foi atualizado com valores padrão, salvar as alterações
    if fields_updated or is_new:
        budget_settings.save()
    
    if request.method == 'POST':
        form = BudgetSettingsForm(request.POST, instance=budget_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações do orçamento atualizadas com sucesso!')
            return redirect('events:event_budget', event_id=event.id)
    else:
        form = BudgetSettingsForm(instance=budget_settings)
    
    context = {
        'event': event,
        'form': form,
        'using_default_values': fields_updated,
    }
    return render(request, 'events/event_budget_settings_form.html', context)


def event_budget_pdf(request, event_id):
    """View para gerar o PDF do orçamento"""
    from django.http import HttpResponse
    from django.template.loader import get_template
    from xhtml2pdf import pisa
    from io import BytesIO
    from django.conf import settings
    import os
    
    event = get_object_or_404(Event, pk=event_id)
    budget_items = EventBudgetItem.objects.filter(event=event).order_by('date', 'start_time')
    budget_settings, created = BudgetSettings.objects.get_or_create(event=event)
    company = CompanySettings.get_default()
    
    # Obter configurações padrão para dados bancários se não estiverem definidos no orçamento específico
    default_settings = DefaultBudgetSettings.get_default()
    if not hasattr(budget_settings, 'bank_details') or not budget_settings.bank_details:
        budget_settings.bank_details = default_settings.bank_details
    
    # Calcular o total do orçamento corretamente
    total = sum(item.quantity * item.unit_value for item in budget_items)
    
    # Caminho absoluto para a logo
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'brand', 'logo_orcamento.jpg')
    logo_exists = os.path.exists(logo_path)
    
    # Preparar o contexto para o template
    context = {
        'event': event,
        'budget_items': budget_items,
        'budget_settings': budget_settings,
        'company': company,
        'total': total,
        'today': timezone.now().date(),
        'STATIC_ROOT': settings.STATICFILES_DIRS[0],
        'logo_path': logo_path if logo_exists else None,
    }
    
    # Função para lidar com URLs em xhtml2pdf
    def link_callback(uri, rel):
        """
        Converte URLs de HTML para caminhos absolutos para o PDF
        """
        # Caminho base para arquivos estáticos
        sUrl = settings.STATIC_ROOT
        
        # Se a URI é um caminho absoluto de arquivo
        if uri.startswith('/'):
            path = os.path.join(settings.BASE_DIR, uri[1:])
            return path
        
        # Se a URI é um caminho relativo
        if uri.startswith('static/'):
            path = os.path.join(settings.STATICFILES_DIRS[0], uri[7:])
            return path
            
        # Se a URI é um caminho para a logo
        if uri.startswith('file:///'):
            return uri[8:]
            
        # Se a URI é um caminho para media
        if uri.startswith('media/'):
            path = os.path.join(settings.MEDIA_ROOT, uri[6:])
            return path
            
        return uri
    
    # Renderizar o template HTML
    template = get_template('events/event_budget_pdf.html')
    html = template.render(context)
    
    # Criar o arquivo PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{event.id}.pdf"'
        return response
    
    return HttpResponse('Erro ao gerar PDF', status=400)

# Default Budget Settings views
def default_budget_settings(request):
    """View para gerenciar as configurações padrão de orçamentos"""
    default_settings = DefaultBudgetSettings.get_default()
    
    if request.method == 'POST':
        form = DefaultBudgetSettingsForm(request.POST, instance=default_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações padrão de orçamento atualizadas com sucesso!')
            return redirect('events:default_budget_settings')
    else:
        form = DefaultBudgetSettingsForm(instance=default_settings)
    
    context = {
        'form': form,
        'default_settings': default_settings,
    }
    return render(request, 'events/default_budget_settings.html', context)

# Company Settings views
def company_settings(request):
    """View para gerenciar as configurações da empresa"""
    company = CompanySettings.get_default()
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações da empresa atualizadas com sucesso!')
            return redirect('events:company_settings')
    else:
        form = CompanySettingsForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'events/company_settings.html', context)
