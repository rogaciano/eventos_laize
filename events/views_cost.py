from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder
import json
import decimal
from .models import Event
from .models_cost import CostCategory, EventCost
from .forms_cost import CostCategoryForm, EventCostForm


class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


# Categorias de Custos
def cost_category_list(request):
    categories = CostCategory.objects.all().order_by('name')
    return render(request, 'events/cost_category_list.html', {'categories': categories})


def cost_category_create(request):
    if request.method == 'POST':
        form = CostCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, 'Categoria de custo criada com sucesso!')
            return redirect('events:cost_category_list')
    else:
        form = CostCategoryForm()
    
    return render(request, 'events/cost_category_form.html', {
        'form': form,
        'title': 'Nova Categoria de Custo'
    })


def cost_category_update(request, category_id):
    category = get_object_or_404(CostCategory, pk=category_id)
    
    if request.method == 'POST':
        form = CostCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria de custo atualizada com sucesso!')
            return redirect('events:cost_category_list')
    else:
        form = CostCategoryForm(instance=category)
    
    return render(request, 'events/cost_category_form.html', {
        'form': form,
        'category': category,
        'title': 'Editar Categoria de Custo'
    })


def cost_category_delete(request, category_id):
    category = get_object_or_404(CostCategory, pk=category_id)
    
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Categoria de custo excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Não foi possível excluir a categoria: {str(e)}')
        return redirect('events:cost_category_list')
    
    return render(request, 'events/cost_category_confirm_delete.html', {'category': category})


# Custos de Eventos
def event_costs(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    costs = EventCost.objects.filter(event=event).order_by('-date')
    
    # Calcular totais
    budget_total = event.get_total_costs(cost_type='budget')
    actual_total = event.get_total_costs(cost_type='actual')
    participant_costs = event.get_total_participant_costs()
    total_expenses = event.get_total_expenses()
    
    # Calcular lucro e margem
    profit = event.get_profit()
    profit_margin = event.get_profit_margin()
    
    return render(request, 'events/event_costs.html', {
        'event': event,
        'costs': costs,
        'budget_total': budget_total,
        'actual_total': actual_total,
        'participant_costs': participant_costs,
        'total_expenses': total_expenses,
        'profit': profit,
        'profit_margin': profit_margin
    })


def add_event_cost(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = EventCostForm(request.POST, request.FILES)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.event = event
            cost.save()
            messages.success(request, 'Custo adicionado com sucesso!')
            return redirect('events:event_costs', event_id=event.id)
    else:
        form = EventCostForm()
    
    return render(request, 'events/event_cost_form.html', {
        'form': form,
        'event': event,
        'title': 'Adicionar Custo'
    })


def update_event_cost(request, event_id, cost_id):
    event = get_object_or_404(Event, pk=event_id)
    cost = get_object_or_404(EventCost, pk=cost_id, event=event)
    
    if request.method == 'POST':
        form = EventCostForm(request.POST, request.FILES, instance=cost)
        if form.is_valid():
            form.save()
            messages.success(request, 'Custo atualizado com sucesso!')
            return redirect('events:event_costs', event_id=event.id)
    else:
        form = EventCostForm(instance=cost)
    
    return render(request, 'events/event_cost_form.html', {
        'form': form,
        'event': event,
        'cost': cost,
        'title': 'Editar Custo'
    })


def delete_event_cost(request, event_id, cost_id):
    event = get_object_or_404(Event, pk=event_id)
    cost = get_object_or_404(EventCost, pk=cost_id, event=event)
    
    if request.method == 'POST':
        cost.delete()
        messages.success(request, 'Custo excluído com sucesso!')
        return redirect('events:event_costs', event_id=event.id)
    
    return render(request, 'events/event_cost_confirm_delete.html', {
        'event': event,
        'cost': cost
    })


# Relatórios financeiros
def financial_report(request):
    events = Event.objects.filter(status='concluido').order_by('-end_datetime')
    
    # Filtrar por período se fornecido
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        events = events.filter(end_datetime__gte=start_date)
    
    if end_date:
        events = events.filter(end_datetime__lte=end_date)
    
    # Preparar dados para o relatório
    report_data = []
    total_revenue = decimal.Decimal('0.00')
    total_expenses = decimal.Decimal('0.00')
    total_profit = decimal.Decimal('0.00')
    
    for event in events:
        revenue = event.value or decimal.Decimal('0.00')
        expenses = event.get_total_expenses()
        profit = event.get_profit() or decimal.Decimal('0.00')
        margin = event.get_profit_margin() or 0
        
        report_data.append({
            'id': event.id,
            'title': event.title,
            'client': event.client.name,
            'date': event.end_datetime.strftime('%d/%m/%Y'),
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'margin': margin
        })
        
        total_revenue += revenue
        total_expenses += expenses
        total_profit += profit
    
    # Calcular margem média
    avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return render(request, 'events/financial_report.html', {
        'report_data': report_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'total_profit': total_profit,
        'avg_margin': avg_margin,
        'start_date': start_date,
        'end_date': end_date
    })


def export_financial_data(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    # Preparar dados para exportação
    costs = EventCost.objects.filter(event=event).order_by('-date')
    participants = event.eventparticipant_set.all()
    
    data = {
        'event': {
            'id': event.id,
            'title': event.title,
            'client': event.client.name,
            'start_date': event.start_datetime.strftime('%d/%m/%Y'),
            'end_date': event.end_datetime.strftime('%d/%m/%Y'),
            'value': float(event.value) if event.value else 0,
        },
        'costs': [
            {
                'category': cost.category.name,
                'description': cost.description,
                'amount': float(cost.amount),
                'type': cost.get_cost_type_display(),
                'date': cost.date.strftime('%d/%m/%Y'),
                'paid': cost.paid
            } for cost in costs
        ],
        'participants': [
            {
                'name': p.person.name,
                'role': p.role.nome if p.role else '',
                'value': float(p.value) if p.value else 0
            } for p in participants
        ],
        'summary': {
            'budget_total': float(event.get_total_costs(cost_type='budget')),
            'actual_total': float(event.get_total_costs(cost_type='actual')),
            'participant_costs': float(event.get_total_participant_costs()),
            'total_expenses': float(event.get_total_expenses()),
            'profit': float(event.get_profit()) if event.get_profit() else 0,
            'profit_margin': float(event.get_profit_margin()) if event.get_profit_margin() else 0
        }
    }
    
    response = JsonResponse(data, encoder=DecimalEncoder)
    response['Content-Disposition'] = f'attachment; filename="{event.title.replace(" ", "_")}_financial_data.json"'
    return response
