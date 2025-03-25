from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Person, PersonContact, CorOlhos, CorCabelo, CorPele, Genero
from .forms import PersonForm, PersonContactForm
import os

def person_list(request):
    # Verificar se estamos retornando de uma página de detalhes
    if request.GET.get('from_detail') == 'true' and 'filter_params' in request.session:
        # Recuperar os parâmetros de filtro da sessão
        filter_params = request.session.get('filter_params', {})
        # Redirecionar para a mesma página com os parâmetros de filtro
        return redirect(f"{reverse('people:list')}?{filter_params}")
    
    # Salvar todos os parâmetros de filtro na sessão
    filter_params = request.GET.urlencode()
    request.session['filter_params'] = filter_params
    
    search_query = request.GET.get('search', '')
    cor_olhos_id = request.GET.get('cor_olhos', '')
    cor_cabelo_id = request.GET.get('cor_cabelo', '')
    cor_pele_id = request.GET.get('cor_pele', '')
    genero_id = request.GET.get('genero', '')
    cidade = request.GET.get('cidade', '')
    estado = request.GET.get('estado', '')
    manequim = request.GET.get('manequim', '')
    
    # Filtros de intervalo para características numéricas
    altura_min = request.GET.get('altura_min', '')
    altura_max = request.GET.get('altura_max', '')
    peso_min = request.GET.get('peso_min', '')
    peso_max = request.GET.get('peso_max', '')
    idade_min = request.GET.get('idade_min', '')
    idade_max = request.GET.get('idade_max', '')
    
    # Filtros para avaliações
    efficiency_min = request.GET.get('efficiency_min', '')
    punctuality_min = request.GET.get('punctuality_min', '')
    proactivity_min = request.GET.get('proactivity_min', '')
    appearance_min = request.GET.get('appearance_min', '')
    communication_min = request.GET.get('communication_min', '')
    
    # Iniciar com todos os registros
    persons = Person.objects.all()
    
    # Aplicar filtros conforme fornecidos
    if search_query:
        persons = persons.filter(name__icontains=search_query)
    
    if cor_olhos_id:
        persons = persons.filter(cor_olhos_id=cor_olhos_id)
    
    if cor_cabelo_id:
        persons = persons.filter(cor_cabelo_id=cor_cabelo_id)
    
    if cor_pele_id:
        persons = persons.filter(cor_pele_id=cor_pele_id)
    
    if genero_id:
        persons = persons.filter(genero_id=genero_id)
    
    if cidade:
        persons = persons.filter(city__icontains=cidade)
    
    if estado:
        persons = persons.filter(state__iexact=estado)
    
    if manequim:
        persons = persons.filter(manequim__iexact=manequim)
    
    # Aplicar filtros de intervalo para características numéricas
    if altura_min:
        try:
            altura_min = float(altura_min.replace(',', '.'))
            persons = persons.filter(altura__gte=altura_min)
        except (ValueError, TypeError):
            pass
    
    if altura_max:
        try:
            altura_max = float(altura_max.replace(',', '.'))
            persons = persons.filter(altura__lte=altura_max)
        except (ValueError, TypeError):
            pass
    
    if peso_min:
        try:
            peso_min = float(peso_min.replace(',', '.'))
            persons = persons.filter(peso__gte=peso_min)
        except (ValueError, TypeError):
            pass
    
    if peso_max:
        try:
            peso_max = float(peso_max.replace(',', '.'))
            persons = persons.filter(peso__lte=peso_max)
        except (ValueError, TypeError):
            pass
    
    # Para idade, precisamos calcular com base na data de nascimento
    from datetime import date
    hoje = date.today()
    
    if idade_min:
        try:
            idade_min = int(idade_min)
            # Data máxima de nascimento para ter pelo menos idade_min anos
            data_max = date(hoje.year - idade_min, hoje.month, hoje.day)
            persons = persons.filter(data_nascimento__lte=data_max)
        except (ValueError, TypeError):
            pass
    
    if idade_max:
        try:
            idade_max = int(idade_max)
            # Data mínima de nascimento para ter no máximo idade_max anos
            data_min = date(hoje.year - idade_max - 1, hoje.month, hoje.day)
            data_min = date(hoje.year - idade_max, hoje.month, hoje.day)
            persons = persons.filter(data_nascimento__gte=data_min)
        except (ValueError, TypeError):
            pass
    
    # Filtros para avaliações
    if efficiency_min:
        try:
            efficiency_min = int(efficiency_min)
            persons = persons.filter(efficiency__gte=efficiency_min)
        except (ValueError, TypeError):
            pass
    
    if punctuality_min:
        try:
            punctuality_min = int(punctuality_min)
            persons = persons.filter(punctuality__gte=punctuality_min)
        except (ValueError, TypeError):
            pass
    
    if proactivity_min:
        try:
            proactivity_min = int(proactivity_min)
            persons = persons.filter(proactivity__gte=proactivity_min)
        except (ValueError, TypeError):
            pass
    
    if appearance_min:
        try:
            appearance_min = int(appearance_min)
            persons = persons.filter(appearance__gte=appearance_min)
        except (ValueError, TypeError):
            pass
    
    if communication_min:
        try:
            communication_min = int(communication_min)
            persons = persons.filter(communication__gte=communication_min)
        except (ValueError, TypeError):
            pass
    
    # Obter listas para os dropdowns de filtro
    cores_olhos = CorOlhos.objects.all()
    cores_cabelo = CorCabelo.objects.all()
    cores_pele = CorPele.objects.all()
    generos = Genero.objects.all()
    
    # Obter lista única de cidades e estados para os dropdowns
    cidades = Person.objects.exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    estados = Person.objects.exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct().order_by('state')
    
    # Lista de manequins para o dropdown
    manequins = Person.objects.exclude(manequim__isnull=True).exclude(manequim='').values_list('manequim', flat=True).distinct().order_by('manequim')
    
    context = {
        'persons': persons,
        'search_query': search_query,
        'cores_olhos': cores_olhos,
        'cores_cabelo': cores_cabelo,
        'cores_pele': cores_pele,
        'generos': generos,
        'cidades': cidades,
        'estados': estados,
        'manequins': manequins,
        'cor_olhos_id': cor_olhos_id,
        'cor_cabelo_id': cor_cabelo_id,
        'cor_pele_id': cor_pele_id,
        'genero_id': genero_id,
        'cidade': cidade,
        'estado': estado,
        'manequim': manequim,
        'altura_min': altura_min,
        'altura_max': altura_max,
        'peso_min': peso_min,
        'peso_max': peso_max,
        'idade_min': idade_min,
        'idade_max': idade_max,
        'efficiency_min': efficiency_min,
        'punctuality_min': punctuality_min,
        'proactivity_min': proactivity_min,
        'appearance_min': appearance_min,
        'communication_min': communication_min,
    }
    
    return render(request, 'people/person_list.html', context)

def person_detail(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    # Adicionar um parâmetro para indicar que estamos voltando da página de detalhes
    back_url = f"{reverse('people:list')}?from_detail=true"
    contacts = person.contacts.all()
    # Get all events that this person participated in
    events = person.events.all().order_by('-start_datetime')
    
    return render(request, 'people/person_detail.html', {
        'person': person,
        'contacts': contacts,
        'events': events,
        'back_url': back_url
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
