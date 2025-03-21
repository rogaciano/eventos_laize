from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Person, PersonContact
from .forms import PersonForm, PersonContactForm
import os

def person_list(request):
    persons = Person.objects.all()
    return render(request, 'people/person_list.html', {'persons': persons})

def person_detail(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    contacts = person.contacts.all()
    # Get all events that this person participated in
    events = person.events.all().order_by('-start_datetime')
    
    return render(request, 'people/person_detail.html', {
        'person': person,
        'contacts': contacts,
        'events': events
    })

def person_create(request):
    if request.method == 'POST':
        # Converter vírgula para ponto no campo altura
        post_data = request.POST.copy()
        if 'altura' in post_data and post_data['altura']:
            post_data['altura'] = post_data['altura'].replace(',', '.')
        
        form = PersonForm(post_data, request.FILES)
        if form.is_valid():
            person = form.save()
            messages.success(request, 'Pessoa cadastrada com sucesso!')
            return redirect('people:detail', person_id=person.id)
    else:
        form = PersonForm()
    
    return render(request, 'people/person_form.html', {
        'form': form,
        'title': 'Nova Pessoa'
    })

def person_update(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    
    if request.method == 'POST':
        # Converter vírgula para ponto no campo altura
        post_data = request.POST.copy()
        if 'altura' in post_data and post_data['altura']:
            post_data['altura'] = post_data['altura'].replace(',', '.')
        
        # Verificar se o usuário quer remover a foto atual
        clear_photo = post_data.get('clear_photo')
        
        form = PersonForm(post_data, request.FILES, instance=person)
        if form.is_valid():
            # Salvar o formulário sem commit para poder modificar a foto se necessário
            person = form.save(commit=False)
            
            # Se o checkbox de limpar foto estiver marcado, remover a foto
            if clear_photo:
                if person.photo:
                    # Salvar o caminho da foto para excluir o arquivo depois
                    old_photo = person.photo.path if person.photo else None
                    person.photo = None
                    # Se tiver um arquivo físico, remover
                    if old_photo and os.path.isfile(old_photo):
                        os.remove(old_photo)
            
            # Salvar a pessoa com todas as alterações
            person.save()
            
            # Importante: salvar os campos many-to-many, se houver
            form.save_m2m()
            
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('people:detail', person_id=person.id)
    else:
        form = PersonForm(instance=person)
    
    return render(request, 'people/person_form.html', {
        'form': form,
        'person': person,
        'title': 'Editar Pessoa'
    })

def person_delete(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    
    if request.method == 'POST':
        person.delete()
        messages.success(request, 'Pessoa excluída com sucesso!')
        return redirect('people:list')
    
    return render(request, 'people/person_confirm_delete.html', {'person': person})

# Contact views
def person_contact_add(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    
    if request.method == 'POST':
        form = PersonContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.person = person
            contact.save()
            messages.success(request, 'Contato adicionado com sucesso!')
            return redirect('people:detail', person_id=person.id)
    else:
        form = PersonContactForm()
    
    return render(request, 'people/person_contact_form.html', {
        'form': form,
        'person': person,
        'title': 'Adicionar Contato'
    })

def person_contact_edit(request, person_id, contact_id):
    person = get_object_or_404(Person, pk=person_id)
    contact = get_object_or_404(PersonContact, pk=contact_id, person=person)
    
    if request.method == 'POST':
        form = PersonContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contato atualizado com sucesso!')
            return redirect('people:detail', person_id=person.id)
    else:
        form = PersonContactForm(instance=contact)
    
    return render(request, 'people/person_contact_form.html', {
        'form': form,
        'person': person,
        'contact': contact,
        'title': 'Editar Contato'
    })

def person_contact_delete(request, person_id, contact_id):
    person = get_object_or_404(Person, pk=person_id)
    contact = get_object_or_404(PersonContact, pk=contact_id, person=person)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contato excluído com sucesso!')
        return redirect('people:detail', person_id=person.id)
    
    return render(request, 'people/person_contact_confirm_delete.html', {
        'contact': contact,
        'person': person
    })
