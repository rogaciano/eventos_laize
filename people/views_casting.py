from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from datetime import datetime

from .models import Person, CorOlhos, CorCabelo, CorPele, Genero, ProfessionalCategory, PersonSelection
from .models_casting import CastingCatalog
from .forms import PersonFilterForm

@login_required
def casting_catalog_list(request):
    """
    Lista todos os catálogos de casting
    """
    # Verificar permissão do usuário
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('dashboard:index')
        
    catalogs = CastingCatalog.objects.all()
    
    # Adicionar contagem de pessoas selecionadas para cada catálogo
    for catalog in catalogs:
        # Obter IDs das pessoas que atendem aos filtros do catálogo
        filtered_people_ids = catalog.get_filtered_people().values_list('id', flat=True)
        
        # Contar apenas seleções de pessoas que estão no catálogo filtrado
        catalog.selected_count = PersonSelection.objects.filter(
            catalog=catalog,
            person_id__in=filtered_people_ids
        ).count()
        
        # Adicionar contagem total de pessoas no catálogo
        catalog.total_people_count = len(filtered_people_ids)
    
    # Paginação
    paginator = Paginator(catalogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'catalogs': page_obj.object_list,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'people/casting_catalog_list.html', context)

@login_required
def casting_catalog_detail(request, pk):
    """
    Exibe os detalhes de um catálogo de casting e as pessoas que atendem aos critérios
    """
    # Verificar permissão do usuário
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('dashboard:index')
        
    catalog = get_object_or_404(CastingCatalog, pk=pk)
    
    # Obter pessoas filtradas
    persons = catalog.get_filtered_people()
    
    # Obter IDs de pessoas filtradas
    filtered_person_ids = list(persons.values_list('id', flat=True))
    
    # Obter IDs de pessoas selecionadas neste catálogo (apenas as que estão no filtro)
    selected_person_ids = list(PersonSelection.objects.filter(
        catalog=catalog,
        person_id__in=filtered_person_ids
    ).values_list('person_id', flat=True))
    
    # Filtrar apenas pessoas selecionadas se o parâmetro estiver presente
    show_selected_only = request.GET.get('selected_only') == '1'
    if show_selected_only:
        persons = persons.filter(id__in=selected_person_ids)
    
    # Contagem total de pessoas no catálogo
    total_persons_count = persons.count() if not show_selected_only else len(filtered_person_ids)
    
    # Contagem de pessoas selecionadas
    selected_persons_count = len(selected_person_ids)
    
    # Paginação
    paginator = Paginator(persons, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'catalog': catalog,
        'persons': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'selected_person_ids': selected_person_ids,
        'total_persons_count': total_persons_count,
        'selected_persons_count': selected_persons_count,
        'show_selected_only': show_selected_only,
    }
    
    return render(request, 'people/casting_catalog_detail.html', context)

@login_required
def casting_catalog_create(request):
    """
    Cria um novo catálogo de casting a partir dos filtros atuais
    """
    # Obter todos os modelos para os filtros
    eye_colors = CorOlhos.objects.all()
    hair_colors = CorCabelo.objects.all()
    skin_colors = CorPele.objects.all()
    genders = Genero.objects.all()
    professional_categories = ProfessionalCategory.objects.all()
    
    # Obter cidades e estados únicos para os filtros
    cities = Person.objects.exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    states = Person.objects.exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct().order_by('state')
    
    if request.method == 'POST':
        # Processar o formulário
        name = request.POST.get('name')
        description = request.POST.get('description')
        company = request.POST.get('company')
        
        if not name or not description:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return redirect(request.path)
        
        # Criar o catálogo
        catalog = CastingCatalog(
            name=name,
            description=description,
            company=company,
            # Salvar os filtros atuais
            min_height=request.POST.get('altura_min') if request.POST.get('altura_min') else None,
            max_height=request.POST.get('altura_max') if request.POST.get('altura_max') else None,
            min_weight=request.POST.get('peso_min') if request.POST.get('peso_min') else None,
            max_weight=request.POST.get('peso_max') if request.POST.get('peso_max') else None,
            min_age=request.POST.get('idade_min') if request.POST.get('idade_min') else None,
            max_age=request.POST.get('idade_max') if request.POST.get('idade_max') else None,
            manequim=request.POST.get('manequim'),
            min_efficiency=request.POST.get('efficiency_min') if request.POST.get('efficiency_min') else None,
            min_punctuality=request.POST.get('punctuality_min') if request.POST.get('punctuality_min') else None,
            min_proactivity=request.POST.get('proactivity_min') if request.POST.get('proactivity_min') else None,
            min_appearance=request.POST.get('appearance_min') if request.POST.get('appearance_min') else None,
            min_communication=request.POST.get('communication_min') if request.POST.get('communication_min') else None,
            search_query=request.POST.get('search'),
        )
        
        # Salvar o catálogo para poder adicionar os relacionamentos
        catalog.save()
        
        # Adicionar os relacionamentos
        if request.POST.getlist('cor_olhos'):
            # Filtrar valores vazios
            cor_olhos = [co for co in request.POST.getlist('cor_olhos') if co]
            catalog.eye_colors.set(cor_olhos)
        if request.POST.getlist('cor_cabelo'):
            # Filtrar valores vazios
            cor_cabelo = [cc for cc in request.POST.getlist('cor_cabelo') if cc]
            catalog.hair_colors.set(cor_cabelo)
        if request.POST.getlist('cor_pele'):
            # Filtrar valores vazios
            cor_pele = [cp for cp in request.POST.getlist('cor_pele') if cp]
            catalog.skin_colors.set(cor_pele)
        if request.POST.getlist('genero'):
            # Filtrar valores vazios
            generos = [g for g in request.POST.getlist('genero') if g]
            catalog.genders.set(generos)
        if request.POST.getlist('categorias'):
            # Filtrar valores vazios
            categorias = [cat for cat in request.POST.getlist('categorias') if cat]
            catalog.professional_categories.set(categorias)
        
        # Salvar cidades e estados como texto
        if request.POST.get('cidade'):
            catalog.cities = request.POST.get('cidade')
        if request.POST.get('estado'):
            catalog.states = request.POST.get('estado')
        
        # Salvar status
        if request.POST.getlist('status'):
            catalog.status_choices = ','.join(request.POST.getlist('status'))
        
        # Salvar a query completa em JSON para referência futura
        filter_data = {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken'}
        catalog.filter_json = json.dumps(filter_data)
        
        catalog.save()
        
        messages.success(request, f'Catálogo "{name}" criado com sucesso!')
        return redirect('people:casting_catalog_detail', pk=catalog.pk)
    
    # Obter os filtros atuais da URL
    initial_data = {k: v for k, v in request.GET.items()}
    
    context = {
        'eye_colors': eye_colors,
        'hair_colors': hair_colors,
        'skin_colors': skin_colors,
        'genders': genders,
        'professional_categories': professional_categories,
        'cities': cities,
        'states': states,
        'initial_data': initial_data,
    }
    
    return render(request, 'people/casting_catalog_create.html', context)

@login_required
def casting_catalog_edit(request, pk):
    """
    Edita um catálogo de casting existente
    """
    catalog = get_object_or_404(CastingCatalog, pk=pk)
    
    # Obter todos os modelos para os filtros
    eye_colors = CorOlhos.objects.all()
    hair_colors = CorCabelo.objects.all()
    skin_colors = CorPele.objects.all()
    genders = Genero.objects.all()
    professional_categories = ProfessionalCategory.objects.all()
    
    # Obter cidades e estados únicos para os filtros
    cities = Person.objects.exclude(city__isnull=True).exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    states = Person.objects.exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct().order_by('state')
    
    if request.method == 'POST':
        # Processar o formulário
        name = request.POST.get('name')
        description = request.POST.get('description')
        company = request.POST.get('company')
        
        if not name or not description:
            messages.error(request, 'Nome e descrição são obrigatórios.')
            return redirect(request.path)
        
        # Atualizar o catálogo
        catalog.name = name
        catalog.description = description
        catalog.company = company
        
        # Processar o campo is_active (checkbox)
        catalog.is_active = 'is_active' in request.POST
        
        # Atualizar os filtros
        catalog.min_height = request.POST.get('altura_min') if request.POST.get('altura_min') else None
        catalog.max_height = request.POST.get('altura_max') if request.POST.get('altura_max') else None
        catalog.min_weight = request.POST.get('peso_min') if request.POST.get('peso_min') else None
        catalog.max_weight = request.POST.get('peso_max') if request.POST.get('peso_max') else None
        catalog.min_age = request.POST.get('idade_min') if request.POST.get('idade_min') else None
        catalog.max_age = request.POST.get('idade_max') if request.POST.get('idade_max') else None
        catalog.manequim = request.POST.get('manequim')
        catalog.min_efficiency = request.POST.get('efficiency_min') if request.POST.get('efficiency_min') else None
        catalog.min_punctuality = request.POST.get('punctuality_min') if request.POST.get('punctuality_min') else None
        catalog.min_proactivity = request.POST.get('proactivity_min') if request.POST.get('proactivity_min') else None
        catalog.min_appearance = request.POST.get('appearance_min') if request.POST.get('appearance_min') else None
        catalog.min_communication = request.POST.get('communication_min') if request.POST.get('communication_min') else None
        catalog.search_query = request.POST.get('search')
        
        # Atualizar relacionamentos
        if 'cor_olhos' in request.POST:
            # Filtrar valores vazios
            cor_olhos = [co for co in request.POST.getlist('cor_olhos') if co]
            catalog.eye_colors.set(cor_olhos)
        else:
            catalog.eye_colors.clear()
            
        if 'cor_cabelo' in request.POST:
            # Filtrar valores vazios
            cor_cabelo = [cc for cc in request.POST.getlist('cor_cabelo') if cc]
            catalog.hair_colors.set(cor_cabelo)
        else:
            catalog.hair_colors.clear()
            
        if 'cor_pele' in request.POST:
            # Filtrar valores vazios
            cor_pele = [cp for cp in request.POST.getlist('cor_pele') if cp]
            catalog.skin_colors.set(cor_pele)
        else:
            catalog.skin_colors.clear()
            
        if 'genero' in request.POST:
            # Filtrar valores vazios
            generos = [g for g in request.POST.getlist('genero') if g]
            catalog.genders.set(generos)
        else:
            catalog.genders.clear()
            
        if 'categorias' in request.POST:
            # Filtrar valores vazios da lista de categorias
            categorias = [cat for cat in request.POST.getlist('categorias') if cat]
            catalog.professional_categories.set(categorias)
        else:
            catalog.professional_categories.clear()
        
        # Atualizar cidades e estados
        catalog.cities = request.POST.get('cidade', '')
        catalog.states = request.POST.get('estado', '')
        
        # Atualizar status
        if 'status' in request.POST:
            catalog.status_choices = ','.join(request.POST.getlist('status'))
        else:
            catalog.status_choices = ''
        
        # Atualizar origem do cadastro
        if 'origem_cadastro' in request.POST:
            catalog.origem_cadastro = ','.join(request.POST.getlist('origem_cadastro'))
        else:
            catalog.origem_cadastro = ''
        
        # Atualizar a query completa em JSON
        filter_data = {k: v for k, v in request.POST.items() if k != 'csrfmiddlewaretoken'}
        catalog.filter_json = json.dumps(filter_data)
        
        catalog.save()
        
        messages.success(request, f'Catálogo "{name}" atualizado com sucesso!')
        return redirect('people:casting_catalog_detail', pk=catalog.pk)
    
    # Preparar dados iniciais para o formulário
    initial_data = {
        'name': catalog.name,
        'description': catalog.description,
        'company': catalog.company,
        'search': catalog.search_query,
        'altura_min': catalog.min_height,
        'altura_max': catalog.max_height,
        'peso_min': catalog.min_weight,
        'peso_max': catalog.max_weight,
        'idade_min': catalog.min_age,
        'idade_max': catalog.max_age,
        'manequim': catalog.manequim,
        'efficiency_min': catalog.min_efficiency,
        'punctuality_min': catalog.min_punctuality,
        'proactivity_min': catalog.min_proactivity,
        'appearance_min': catalog.min_appearance,
        'communication_min': catalog.min_communication,
        'cidade': catalog.cities,
        'estado': catalog.states,
    }
    
    # Preparar listas de seleção múltipla
    selected_eye_colors = catalog.eye_colors.all().values_list('id', flat=True)
    selected_hair_colors = catalog.hair_colors.all().values_list('id', flat=True)
    selected_skin_colors = catalog.skin_colors.all().values_list('id', flat=True)
    selected_genders = catalog.genders.all().values_list('id', flat=True)
    selected_categories = catalog.professional_categories.all().values_list('id', flat=True)
    
    # Preparar status selecionados
    selected_status = catalog.status_choices.split(',') if catalog.status_choices else []
    
    # Preparar origem do cadastro selecionada
    selected_origem = catalog.origem_cadastro.split(',') if catalog.origem_cadastro else []
    
    # Adicionar IDs para facilitar a seleção no template
    catalog.eye_colors_ids = list(selected_eye_colors)
    catalog.hair_colors_ids = list(selected_hair_colors)
    catalog.skin_colors_ids = list(selected_skin_colors)
    catalog.genders_ids = list(selected_genders)
    catalog.categories_ids = list(selected_categories)
    catalog.status_list = selected_status
    catalog.origem_cadastro_list = selected_origem
    
    context = {
        'catalog': catalog,
        'eye_colors': eye_colors,
        'hair_colors': hair_colors,
        'skin_colors': skin_colors,
        'genders': genders,
        'categories': professional_categories,
        'cities': cities,
        'states': states,
        'initial_data': initial_data,
    }
    
    return render(request, 'people/casting_catalog_edit.html', context)

@login_required
def casting_catalog_delete(request, pk):
    """
    Exclui um catálogo de casting
    """
    catalog = get_object_or_404(CastingCatalog, pk=pk)
    
    if request.method == 'POST':
        name = catalog.name
        catalog.delete()
        messages.success(request, f'Catálogo "{name}" excluído com sucesso!')
        return redirect('people:casting_catalog_list')
    
    context = {
        'catalog': catalog,
    }
    
    return render(request, 'people/casting_catalog_delete.html', context)

@login_required
@require_POST
def casting_catalog_add_person(request, catalog_pk, person_pk):
    """
    Adiciona uma pessoa manualmente a um catálogo de casting
    """
    catalog = get_object_or_404(CastingCatalog, pk=catalog_pk)
    person = get_object_or_404(Person, pk=person_pk)
    
    # Adicionar a pessoa ao catálogo
    catalog.included_people.add(person)
    
    # Remover da lista de excluídos, se estiver lá
    catalog.excluded_people.remove(person)
    
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def casting_catalog_remove_person(request, catalog_pk, person_pk):
    """
    Remove uma pessoa manualmente de um catálogo de casting
    """
    catalog = get_object_or_404(CastingCatalog, pk=catalog_pk)
    person = get_object_or_404(Person, pk=person_pk)
    
    # Remover a pessoa do catálogo
    catalog.included_people.remove(person)
    
    # Adicionar à lista de excluídos se a pessoa atender aos critérios de filtro
    filtered_people = catalog.get_filtered_people()
    if person in filtered_people:
        catalog.excluded_people.add(person)
    
    return JsonResponse({'status': 'success'})

@login_required
def create_catalog_from_filter(request):
    """
    Cria um catálogo de casting a partir dos filtros aplicados na listagem de pessoas
    """
    # Obter os parâmetros de filtro da URL
    search_query = request.GET.get('search', '')
    cor_olhos_id = request.GET.get('cor_olhos', '')
    cor_cabelo_id = request.GET.get('cor_cabelo', '')
    cor_pele_id = request.GET.get('cor_pele', '')
    genero_id = request.GET.get('genero', '')
    cidade = request.GET.get('cidade', '')
    estado = request.GET.get('estado', '')
    manequim = request.GET.get('manequim', '')
    status = request.GET.get('status', '')
    professional_category_ids = request.GET.getlist('professional_categories', [])
    origem_cadastro = request.GET.get('origem_cadastro', '')
    
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
    
    # Criar um nome automático para o catálogo baseado nos filtros
    catalog_name = f"Catálogo {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    if search_query:
        catalog_name += f" - Busca: {search_query}"
    
    # Criar a descrição do catálogo
    description = "Catálogo criado automaticamente a partir dos seguintes filtros:\n"
    
    if search_query:
        description += f"- Busca por nome: {search_query}\n"
    if status:
        description += f"- Status: {status}\n"
    if origem_cadastro:
        description += f"- Origem do cadastro: {origem_cadastro}\n"
    if altura_min:
        description += f"- Altura mínima: {altura_min}m\n"
    if altura_max:
        description += f"- Altura máxima: {altura_max}m\n"
    if peso_min:
        description += f"- Peso mínimo: {peso_min}kg\n"
    if peso_max:
        description += f"- Peso máximo: {peso_max}kg\n"
    if idade_min:
        description += f"- Idade mínima: {idade_min} anos\n"
    if idade_max:
        description += f"- Idade máxima: {idade_max} anos\n"
    if manequim:
        description += f"- Manequim: {manequim}\n"
    if cidade:
        description += f"- Cidade: {cidade}\n"
    if estado:
        description += f"- Estado: {estado}\n"
    if efficiency_min:
        description += f"- Eficiência mínima: {efficiency_min}\n"
    if punctuality_min:
        description += f"- Pontualidade mínima: {punctuality_min}\n"
    if proactivity_min:
        description += f"- Proatividade mínima: {proactivity_min}\n"
    if appearance_min:
        description += f"- Aparência mínima: {appearance_min}\n"
    if communication_min:
        description += f"- Comunicação mínima: {communication_min}\n"
    
    # Criar o catálogo
    catalog = CastingCatalog(
        name=catalog_name,
        description=description,
        # Salvar os filtros atuais
        min_height=altura_min if altura_min else None,
        max_height=altura_max if altura_max else None,
        min_weight=peso_min if peso_min else None,
        max_weight=peso_max if peso_max else None,
        min_age=idade_min if idade_min else None,
        max_age=idade_max if idade_max else None,
        manequim=manequim,
        min_efficiency=efficiency_min if efficiency_min else None,
        min_punctuality=punctuality_min if punctuality_min else None,
        min_proactivity=proactivity_min if proactivity_min else None,
        min_appearance=appearance_min if appearance_min else None,
        min_communication=communication_min if communication_min else None,
        search_query=search_query,
        cities=cidade,
        states=estado,
        status_choices=status,
        origem_cadastro=origem_cadastro,
    )
    
    # Salvar o catálogo para poder adicionar os relacionamentos
    catalog.save()
    
    # Adicionar os relacionamentos
    if cor_olhos_id:
        catalog.eye_colors.add(cor_olhos_id)
    if cor_cabelo_id:
        catalog.hair_colors.add(cor_cabelo_id)
    if cor_pele_id:
        catalog.skin_colors.add(cor_pele_id)
    if genero_id:
        catalog.genders.add(genero_id)
    if professional_category_ids:
        catalog.professional_categories.set(professional_category_ids)
    
    # Obter as pessoas que atendem aos critérios de filtro
    from .views import person_list
    # Criar um objeto HttpRequest falso para passar para a função person_list
    dummy_request = type('obj', (object,), {'GET': request.GET, 'session': {}})
    
    # Chamar a função person_list para obter as pessoas filtradas
    # Isso evita duplicar a lógica de filtro
    context = person_list(dummy_request, return_queryset=True)
    filtered_persons = context['persons']
    
    # Adicionar todas as pessoas filtradas ao catálogo
    for person in filtered_persons:
        catalog.included_people.add(person)
    
    # Atualizar a query completa em JSON
    filter_data = {k: v for k, v in request.GET.items() if k != 'csrfmiddlewaretoken'}
    catalog.filter_json = json.dumps(filter_data)
    catalog.save()
    
    # Redirecionar para a página de detalhes do catálogo
    messages.success(request, f'Catálogo "{catalog_name}" criado com sucesso com {filtered_persons.count()} pessoas!')
    return redirect('people:casting_catalog_detail', pk=catalog.id)
