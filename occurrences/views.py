from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Occurrence
from .forms import OccurrenceForm

def occurrence_list(request):
    occurrences = Occurrence.objects.all()
    return render(request, 'occurrences/occurrence_list.html', {'occurrences': occurrences})

def occurrence_detail(request, occurrence_id):
    occurrence = get_object_or_404(Occurrence, pk=occurrence_id)
    return render(request, 'occurrences/occurrence_detail.html', {'occurrence': occurrence})

def occurrence_create(request):
    initial_data = {}
    
    # Verificar se estamos criando uma ocorrência a partir da tela de pessoa ou cliente
    related_to = request.GET.get('related_to')
    person_id = request.GET.get('person')
    client_id = request.GET.get('client')
    
    if related_to and (person_id or client_id):
        initial_data['related_to'] = related_to
        if related_to == 'person' and person_id:
            initial_data['person'] = person_id
        elif related_to == 'client' and client_id:
            initial_data['client'] = client_id
    
    if request.method == 'POST':
        form = OccurrenceForm(request.POST)
        if form.is_valid():
            occurrence = form.save()
            messages.success(request, 'Ocorrência registrada com sucesso!')
            
            # Redirecionar para a página de detalhes da pessoa ou cliente, se aplicável
            if occurrence.related_to == 'person' and occurrence.person:
                return redirect('people:detail', person_id=occurrence.person.id)
            elif occurrence.related_to == 'client' and occurrence.client:
                return redirect('clients:detail', client_id=occurrence.client.id)
            else:
                return redirect('occurrences:detail', occurrence_id=occurrence.id)
    else:
        form = OccurrenceForm(initial=initial_data)
        
        # Bloquear o campo related_to se for passado na URL
        if related_to:
            form.fields['related_to'].widget.attrs['readonly'] = True
            form.fields['related_to'].widget.attrs['disabled'] = True
            
            # Esconder o campo que não é relevante
            if related_to == 'person':
                form.fields['client'].widget.attrs['disabled'] = True
                form.fields['client'].required = False
            elif related_to == 'client':
                form.fields['person'].widget.attrs['disabled'] = True
                form.fields['person'].required = False
    
    return render(request, 'occurrences/occurrence_form.html', {
        'form': form,
        'title': 'Nova Ocorrência',
        'related_to': related_to  # Passar para o template para poder esconder campos
    })

def occurrence_update(request, occurrence_id):
    occurrence = get_object_or_404(Occurrence, pk=occurrence_id)
    
    if request.method == 'POST':
        form = OccurrenceForm(request.POST, instance=occurrence)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ocorrência atualizada com sucesso!')
            return redirect('occurrences:detail', occurrence_id=occurrence.id)
    else:
        form = OccurrenceForm(instance=occurrence)
        
        # Bloquear o campo related_to na edição
        form.fields['related_to'].widget.attrs['readonly'] = True
        form.fields['related_to'].widget.attrs['disabled'] = True
        
        # Esconder o campo que não é relevante
        if occurrence.related_to == 'person':
            form.fields['client'].widget.attrs['disabled'] = True
            form.fields['client'].required = False
        elif occurrence.related_to == 'client':
            form.fields['person'].widget.attrs['disabled'] = True
            form.fields['person'].required = False
    
    return render(request, 'occurrences/occurrence_form.html', {
        'form': form,
        'occurrence': occurrence,
        'title': 'Editar Ocorrência',
        'related_to': occurrence.related_to  # Passar para o template para poder esconder campos
    })

def occurrence_delete(request, occurrence_id):
    occurrence = get_object_or_404(Occurrence, pk=occurrence_id)
    
    if request.method == 'POST':
        # Guardar referência para redirecionar após exclusão
        related_to = occurrence.related_to
        person_id = occurrence.person.id if occurrence.person else None
        client_id = occurrence.client.id if occurrence.client else None
        
        occurrence.delete()
        messages.success(request, 'Ocorrência excluída com sucesso!')
        
        # Redirecionar para a página de detalhes da pessoa ou cliente, se aplicável
        if related_to == 'person' and person_id:
            return redirect('people:detail', person_id=person_id)
        elif related_to == 'client' and client_id:
            return redirect('clients:detail', client_id=client_id)
        else:
            return redirect('occurrences:list')
    
    return render(request, 'occurrences/occurrence_confirm_delete.html', {'occurrence': occurrence})

def occurrence_update_status(request, occurrence_id, new_status):
    occurrence = get_object_or_404(Occurrence, pk=occurrence_id)
    
    # Verificar se o status é válido
    valid_statuses = [status[0] for status in Occurrence.STATUS_CHOICES]
    if new_status not in valid_statuses:
        messages.error(request, f'Status inválido: {new_status}')
        return redirect('occurrences:detail', occurrence_id=occurrence.id)
    
    if request.method == 'POST':
        # Atualizar o status
        occurrence.status = new_status
        occurrence.save()
        
        status_display = dict(Occurrence.STATUS_CHOICES).get(new_status)
        messages.success(request, f'Status atualizado para: {status_display}')
    
    return redirect('occurrences:detail', occurrence_id=occurrence.id)
