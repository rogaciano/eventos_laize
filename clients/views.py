from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Client, ClientClass, Contact
from .forms import ClientForm, ClientClassForm, ContactForm

def client_list(request):
    clients = Client.objects.all()
    client_classes = ClientClass.objects.all()
    
    # Filtros
    search_query = request.GET.get('search', '')
    client_class_id = request.GET.get('client_class', '')
    
    if search_query:
        clients = clients.filter(name__icontains=search_query)
    
    if client_class_id:
        clients = clients.filter(client_class_id=client_class_id)
    
    return render(request, 'clients/client_list.html', {
        'clients': clients,
        'client_classes': client_classes
    })

def client_detail(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    contacts = client.contacts.all()
    events = client.events.all().order_by('-start_datetime')
    occurrences = client.occurrences.all()
    
    return render(request, 'clients/client_detail.html', {
        'client': client,
        'contacts': contacts,
        'events': events,
        'occurrences': occurrences
    })

def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('clients:detail', client_id=client.id)
    else:
        form = ClientForm()
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'title': 'Novo Cliente'
    })

def client_update(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clients:detail', client_id=client.id)
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'clients/client_form.html', {
        'form': form,
        'client': client,
        'title': 'Editar Cliente'
    })

def client_delete(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    
    if request.method == 'POST':
        if client.events.exists():
            messages.error(request, 'Não é possível excluir este cliente pois existem eventos associados a ele.')
            return redirect('clients:detail', client_id=client.id)
        
        client.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('clients:list')
    
    return render(request, 'clients/client_confirm_delete.html', {'client': client})

# Client Class views
def client_class_list(request):
    client_classes = ClientClass.objects.all()
    return render(request, 'clients/client_class_list.html', {'client_classes': client_classes})

def client_class_create(request):
    if request.method == 'POST':
        form = ClientClassForm(request.POST)
        if form.is_valid():
            client_class = form.save()
            messages.success(request, 'Classe de cliente criada com sucesso!')
            return redirect('clients:class_list')
    else:
        form = ClientClassForm()
    
    return render(request, 'clients/client_class_form.html', {
        'form': form,
        'title': 'Nova Classe de Cliente'
    })

def client_class_update(request, class_id):
    client_class = get_object_or_404(ClientClass, pk=class_id)
    
    if request.method == 'POST':
        form = ClientClassForm(request.POST, instance=client_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Classe de cliente atualizada com sucesso!')
            return redirect('clients:class_list')
    else:
        form = ClientClassForm(instance=client_class)
    
    return render(request, 'clients/client_class_form.html', {
        'form': form,
        'client_class': client_class,
        'title': 'Editar Classe de Cliente'
    })

def client_class_delete(request, class_id):
    client_class = get_object_or_404(ClientClass, pk=class_id)
    
    if request.method == 'POST':
        if Client.objects.filter(client_class=client_class).exists():
            messages.error(request, 'Não é possível excluir esta classe pois existem clientes associados a ela.')
            return redirect('clients:class_list')
        
        client_class.delete()
        messages.success(request, 'Classe de cliente excluída com sucesso!')
        return redirect('clients:class_list')
    
    return render(request, 'clients/client_class_confirm_delete.html', {'client_class': client_class})

# Contact views
def contact_create(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            client.contacts.add(contact)
            messages.success(request, 'Contato adicionado com sucesso!')
            return redirect('clients:detail', client_id=client.id)
    else:
        form = ContactForm()
    
    return render(request, 'clients/contact_form.html', {
        'form': form,
        'client': client,
        'title': 'Novo Contato'
    })

def contact_update(request, client_id, contact_id):
    client = get_object_or_404(Client, pk=client_id)
    contact = get_object_or_404(Contact, pk=contact_id)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contato atualizado com sucesso!')
            return redirect('clients:detail', client_id=client.id)
    else:
        form = ContactForm(instance=contact)
    
    return render(request, 'clients/contact_form.html', {
        'form': form,
        'client': client,
        'contact': contact,
        'title': 'Editar Contato'
    })

def contact_delete(request, client_id, contact_id):
    client = get_object_or_404(Client, pk=client_id)
    contact = get_object_or_404(Contact, pk=contact_id)
    
    if request.method == 'POST':
        client.contacts.remove(contact)
        contact.delete()
        messages.success(request, 'Contato removido com sucesso!')
        return redirect('clients:detail', client_id=client.id)
    
    return render(request, 'clients/contact_confirm_delete.html', {
        'client': client,
        'contact': contact
    })
