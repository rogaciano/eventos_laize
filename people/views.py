from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, date
import json
import os
import logging

from .models import Person, PersonContact, CorOlhos, CorCabelo, CorPele, Genero, WhatsAppMessage, ProfessionalCategory, PersonGallery, PersonView, PersonComment
from .models_casting import CastingCatalog
from events.models import Event
from .forms import PersonForm, PersonContactForm, ProfessionalCategoryForm, PersonGalleryForm
from .utils import send_whatsapp_message

logger = logging.getLogger(__name__)

def person_list(request, return_queryset=False):
    # Verificar se estamos retornando de uma página de detalhes
    if not return_queryset and request.GET.get('from_detail') == 'true' and 'filter_params' in request.session:
        # Recuperar os parâmetros de filtro da sessão
        filter_params = request.session.get('filter_params', {})
        # Redirecionar para a mesma página com os parâmetros de filtro
        return redirect(f"{reverse('people:list')}?{filter_params}")
    
    # Salvar todos os parâmetros de filtro na sessão (apenas se não for chamada para retornar queryset)
    if not return_queryset:
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
    status = request.GET.get('status', '')
    professional_category_ids = request.GET.getlist('professional_categories', [])
    
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
    
    if status:
        persons = persons.filter(status=status)
    
    if professional_category_ids:
        # Filtrar pessoas que pertencem a pelo menos uma das categorias selecionadas
        persons = persons.filter(professional_categories__id__in=professional_category_ids).distinct()
    
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
    
    # Obter o catálogo ativo (se houver)
    active_catalog = None
    catalog_id = request.GET.get('catalog')
    if catalog_id:
        try:
            active_catalog = CastingCatalog.objects.get(pk=catalog_id)
        except CastingCatalog.DoesNotExist:
            pass
    
    # Se houver um catálogo ativo, obter as pessoas selecionadas
    selected_person_ids = []
    if active_catalog:
        session_key = request.session.session_key
        selected_person_ids = list(PersonSelection.objects.filter(
            catalog=active_catalog,
            session_key=session_key
        ).values_list('person_id', flat=True))
        
        # Criar uma lista ordenada com selecionados primeiro
        if selected_person_ids:
            # Criar uma lista de pessoas selecionadas
            selected_persons = list(persons.filter(id__in=selected_person_ids))
            # Criar uma lista de pessoas não selecionadas
            unselected_persons = list(persons.exclude(id__in=selected_person_ids))
            # Combinar as duas listas
            persons = selected_persons + unselected_persons
    
    if return_queryset:
        return {'persons': persons}
    
    # Obter listas para os dropdowns de filtro
    cores_olhos = CorOlhos.objects.all()
    cores_cabelo = CorCabelo.objects.all()
    cores_pele = CorPele.objects.all()
    generos = Genero.objects.all()
    professional_categories = ProfessionalCategory.objects.all()
    
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
        'professional_categories': professional_categories,
        'cidades': cidades,
        'estados': estados,
        'manequins': manequins,
        'cor_olhos_id': cor_olhos_id,
        'cor_cabelo_id': cor_cabelo_id,
        'cor_pele_id': cor_pele_id,
        'genero_id': genero_id,
        'professional_category_ids': professional_category_ids,
        'cidade': cidade,
        'estado': estado,
        'manequim': manequim,
        'status': status,
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
    from django.conf import settings
    
    person = get_object_or_404(Person, pk=person_id)
    # Adicionar um parâmetro para indicar que estamos voltando da página de detalhes
    back_url = f"{reverse('people:list')}?from_detail=true"
    contacts = person.contacts.all()
    # Get all events that this person participated in
    events = person.events.all().order_by('-start_datetime')
    
    # Registrar a visualização do perfil
    ip_address = request.META.get('REMOTE_ADDR', '')
    session_key = request.session.session_key
    
    # Criar registro de visualização
    PersonView.objects.create(
        person=person,
        user=request.user if request.user.is_authenticated else None,
        ip_address=ip_address,
        session_key=session_key
    )
    
    # Obter estatísticas de visualização
    total_views = PersonView.objects.filter(person=person).count()
    unique_views = PersonView.objects.filter(person=person).values('session_key').distinct().count()
    last_view = PersonView.objects.filter(person=person).exclude(
        session_key=session_key
    ).order_by('-timestamp').first()
    
    # Processar comentários/perguntas
    if request.method == 'POST' and 'comment_text' in request.POST:
        comment_text = request.POST.get('comment_text', '').strip()
        is_question = request.POST.get('is_question', '') == 'on'
        
        if comment_text:
            PersonComment.objects.create(
                person=person,
                user=request.user if request.user.is_authenticated else None,
                comment_text=comment_text,
                is_question=is_question
            )
            messages.success(request, 'Seu comentário foi enviado com sucesso!')
            return redirect('people:detail', person_id=person_id)
    
    # Obter comentários existentes
    person_comments = PersonComment.objects.filter(person=person).order_by('-created_at')
    
    # Debug para verificar o valor da variável ENABLE_WHATSAPP
    print(f"ENABLE_WHATSAPP in view: {settings.ENABLE_WHATSAPP}")
    
    return render(request, 'people/person_detail.html', {
        'person': person,
        'contacts': contacts,
        'events': events,
        'back_url': back_url,
        'ENABLE_WHATSAPP': settings.ENABLE_WHATSAPP,
        'total_views': total_views,
        'unique_views': unique_views,
        'last_view': last_view,
        'person_comments': person_comments
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
            
            # Processar novas categorias profissionais
            new_categories = request.POST.getlist('new_categories', [])
            if new_categories:
                for category_name in new_categories:
                    # Criar nova categoria se não existir
                    category, created = ProfessionalCategory.objects.get_or_create(
                        nome=category_name,
                        defaults={'descricao': f'Categoria criada automaticamente a partir do cadastro de {person.name}'}
                    )
                    # Adicionar à pessoa
                    person.professional_categories.add(category)
            
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
            
            # Processar novas categorias profissionais
            new_categories = request.POST.getlist('new_categories', [])
            if new_categories:
                for category_name in new_categories:
                    # Criar nova categoria se não existir
                    category, created = ProfessionalCategory.objects.get_or_create(
                        nome=category_name,
                        defaults={'descricao': f'Categoria criada automaticamente a partir da edição de {person.name}'}
                    )
                    # Adicionar à pessoa
                    person.professional_categories.add(category)
            
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

from django.http import HttpResponse
from datetime import date, datetime
from io import BytesIO
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable

# Classe para adicionar cabeçalho e rodapé com numeração de páginas
class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_footer(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_footer(self, page_count):
        # Data e hora atual
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y %H:%M:%S")
        
        # Adicionar data e hora no canto superior esquerdo
        self.setFont("Helvetica", 8)
        self.drawString(0.5*cm, 29*cm, f"Data/Hora: {date_time}")
        
        # Adicionar número de página no rodapé
        page = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(20*cm, 1*cm, page)

def generate_person_report_pdf(request):
    # Obter os parâmetros de filtro da sessão, se disponíveis
    filter_params = request.session.get('filter_params', '')
    
    # Iniciar com todos os registros ou aplicar filtros
    persons = Person.objects.all()
    
    # Aplicar os mesmos filtros que na view person_list
    search_query = request.GET.get('search', '')
    cor_olhos_id = request.GET.get('cor_olhos', '')
    cor_cabelo_id = request.GET.get('cor_cabelo', '')
    cor_pele_id = request.GET.get('cor_pele', '')
    genero_id = request.GET.get('genero', '')
    cidade = request.GET.get('cidade', '')
    estado = request.GET.get('estado', '')
    manequim = request.GET.get('manequim', '')
    professional_category_id = request.GET.get('professional_category', '')
    
    # Filtros de intervalo para características numéricas
    altura_min = request.GET.get('altura_min', '')
    altura_max = request.GET.get('altura_max', '')
    peso_min = request.GET.get('peso_min', '')
    peso_max = request.GET.get('peso_max', '')
    idade_min = request.GET.get('idade_min', '')
    idade_max = request.GET.get('idade_max', '')
    
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
    
    if professional_category_id:
        persons = persons.filter(professional_category_id=professional_category_id)
    
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
            data_min = date(hoje.year - idade_max, hoje.month, hoje.day)
            persons = persons.filter(data_nascimento__gte=data_min)
        except (ValueError, TypeError):
            pass
    
    # Criar um buffer para o PDF
    buffer = BytesIO()
    
    # Criar o documento PDF com o canvas personalizado para cabeçalho e rodapé
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        topMargin=1.2*cm,  # Aumentado para dar espaço ao cabeçalho
        bottomMargin=1.2*cm,  # Aumentado para dar espaço ao rodapé
        leftMargin=0.5*cm, 
        rightMargin=0.5*cm
    )
    
    # Definir estilos
    styles = getSampleStyleSheet()
    
    # Criar estilo personalizado para o título
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=0.3*cm
    )
    
    # Criar estilo personalizado para o nome da pessoa
    name_style = ParagraphStyle(
        'PersonName',
        parent=styles['Heading2'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=0.2*cm
    )
    
    # Criar estilo personalizado para o cabeçalho da seção
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=9,
        alignment=TA_LEFT,
        spaceAfter=0.1*cm
    )
    
    # Criar estilo para o texto normal
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=8
    )
    
    # Lista para armazenar os elementos do PDF
    elements = []
    
    # Adicionar título do relatório
    elements.append(Paragraph("Relatório de Pessoas", title_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # Criar uma tabela para organizar as pessoas em 2 colunas
    person_data = []
    row = []
    count = 0
    
    # Para cada pessoa, adicionar suas informações
    for person in persons:
        # Criar uma tabela para cada pessoa
        person_elements = []
        
        # Adicionar nome da pessoa
        person_elements.append(Paragraph(person.name, name_style))
        
        # Criar uma tabela com duas colunas: foto e características
        data = []
        
        # Primeira coluna: foto
        if person.photo:
            try:
                # Obter o caminho completo da imagem
                img_path = person.photo.path
                # Verificar se o arquivo existe
                if os.path.exists(img_path):
                    # Redimensionar a imagem para caber no PDF
                    img = Image(img_path)
                    img.drawHeight = 3*cm
                    img.drawWidth = 3*cm
                    photo_cell = img
                else:
                    photo_cell = Paragraph("Foto não disponível", normal_style)
            except:
                photo_cell = Paragraph("Erro ao carregar foto", normal_style)
        else:
            photo_cell = Paragraph("Sem foto", normal_style)
        
        # Segunda coluna: características físicas
        characteristics = []
        
        # Adicionar cabeçalho da seção
        characteristics.append(Paragraph("Características Físicas", section_style))
        
        # Adicionar características em pares
        char_data = []
        
        # Nascimento e Idade
        if person.data_nascimento:
            nascimento = person.data_nascimento.strftime("%d/%m/%Y")
            char_data.append([
                Paragraph(f"<b>Nascimento:</b> {nascimento}", normal_style),
                Paragraph(f"<b>Idade:</b> {person.idade} anos" if person.idade else "<b>Idade:</b> -", normal_style)
            ])
        
        # Telefone (WhatsApp)
        whatsapp_contact = person.contacts.filter(type='whatsapp').first()
        telefone = whatsapp_contact.value if whatsapp_contact else "-"
        char_data.append([
            Paragraph(f"<b>Telefone:</b> {telefone}", normal_style),
            Paragraph("", normal_style)  # Célula vazia para manter o layout
        ])
        
        # Altura e Peso
        char_data.append([
            Paragraph(f"<b>Altura:</b> {person.altura} m" if person.altura else "<b>Altura:</b> -", normal_style),
            Paragraph(f"<b>Peso:</b> {person.peso} kg" if person.peso else "<b>Peso:</b> -", normal_style)
        ])
        
        # Manequim e Gênero
        char_data.append([
            Paragraph(f"<b>Manequim:</b> {person.manequim}" if person.manequim else "<b>Manequim:</b> -", normal_style),
            Paragraph(f"<b>Gênero:</b> {person.genero.nome}" if person.genero else "<b>Gênero:</b> -", normal_style)
        ])
        
        # Cor da pele e Cor dos olhos
        char_data.append([
            Paragraph(f"<b>Cor da pele:</b> {person.cor_pele.nome}" if person.cor_pele else "<b>Cor da pele:</b> -", normal_style),
            Paragraph(f"<b>Cor dos olhos:</b> {person.cor_olhos.nome}" if person.cor_olhos else "<b>Cor dos olhos:</b> -", normal_style)
        ])
        
        # Cor do cabelo
        char_data.append([
            Paragraph(f"<b>Cor do cabelo:</b> {person.cor_cabelo.nome}" if person.cor_cabelo else "<b>Cor do cabelo:</b> -", normal_style),
            Paragraph("", normal_style)  # Célula vazia para manter o layout
        ])
        
        # Criar tabela de características
        char_table = Table(char_data, colWidths=[3.5*cm, 3.5*cm])
        char_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))
        
        characteristics.append(char_table)
        
        # Adicionar foto e características à tabela principal
        data.append([photo_cell, characteristics])
        
        # Criar tabela principal para a pessoa
        person_table = Table(data, colWidths=[3.5*cm, 7.5*cm])
        person_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        
        # Adicionar a tabela da pessoa à lista de elementos da pessoa
        person_elements.append(person_table)
        
        # Criar um container para a pessoa
        person_container = Table([[el] for el in person_elements], colWidths=[11.5*cm])
        
        # Adicionar à linha atual
        row.append(person_container)
        count += 1
        
        # Se tiver 2 pessoas na linha, adicionar à tabela principal e começar uma nova linha
        if count % 2 == 0:
            person_data.append(row)
            row = []
    
    # Se sobrar pessoas na última linha, adicionar à tabela principal
    if row:
        # Preencher com células vazias se necessário
        while len(row) < 2:
            row.append("")
        person_data.append(row)
    
    # Criar a tabela principal com 2 colunas
    if person_data:
        main_table = Table(person_data, colWidths=[10.5*cm, 10.5*cm])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(main_table)
    
    # Construir o PDF com o canvas personalizado
    doc.build(elements, canvasmaker=FooterCanvas)
    
    # Obter o valor do buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Criar a resposta HTTP com o PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_pessoas.pdf"'
    response.write(pdf)
    
    return response

def send_whatsapp(request, person_id, contact_id=None):
    """
    View to send a WhatsApp message to a person's contact.
    If contact_id is provided, that specific contact will be used.
    Otherwise, the first WhatsApp contact for the person will be used.
    """
    person = get_object_or_404(Person, pk=person_id)
    
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        contact_id = request.POST.get('contact_id')
        
        if not message:
            messages.error(request, "A mensagem não pode estar vazia.")
            return redirect('people:detail', person_id=person_id)
        
        if contact_id:
            contact = get_object_or_404(PersonContact, pk=contact_id, person=person)
        else:
            # Try to find a WhatsApp contact
            contact = person.contacts.filter(type='whatsapp').first()
            
        if not contact or contact.type != 'whatsapp':
            messages.error(request, "Nenhum contato de WhatsApp encontrado para esta pessoa.")
            return redirect('people:detail', person_id=person_id)
        
        # Send the message
        whatsapp_message = send_whatsapp_message(contact, message)
        
        if whatsapp_message and whatsapp_message.response_data and 'key' in whatsapp_message.response_data:
            messages.success(request, "Mensagem enviada com sucesso!")
        else:
            messages.error(request, "Erro ao enviar mensagem. Verifique os logs para mais detalhes.")
        
        return redirect('people:detail', person_id=person_id)
    
    # GET request - display form
    whatsapp_contacts = person.contacts.filter(type='whatsapp')
    
    return render(request, 'people/send_whatsapp.html', {
        'person': person,
        'whatsapp_contacts': whatsapp_contacts,
        'selected_contact_id': contact_id
    })

def whatsapp_history(request, person_id):
    """
    View to display WhatsApp message history for a person
    """
    person = get_object_or_404(Person, pk=person_id)
    messages_history = person.whatsapp_messages.all().order_by('-sent_at')
    
    return render(request, 'people/whatsapp_history.html', {
        'person': person,
        'messages_history': messages_history
    })

def send_whatsapp_ajax(request, person_id):
    """
    AJAX view to send a WhatsApp message and return JSON response
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    person = get_object_or_404(Person, pk=person_id)
    message = request.POST.get('message', '').strip()
    contact_id = request.POST.get('contact_id')
    
    if not message:
        return JsonResponse({'success': False, 'error': 'A mensagem não pode estar vazia'})
    
    if contact_id:
        try:
            contact = PersonContact.objects.get(pk=contact_id, person=person)
        except PersonContact.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Contato não encontrado'})
    else:
        # Try to find a WhatsApp contact
        contact = person.contacts.filter(type='whatsapp').first()
        
    if not contact or contact.type != 'whatsapp':
        return JsonResponse({'success': False, 'error': 'Nenhum contato de WhatsApp encontrado'})
    
    # Send the message
    whatsapp_message = send_whatsapp_message(contact, message)
    
    if whatsapp_message and whatsapp_message.response_data and 'key' in whatsapp_message.response_data:
        return JsonResponse({
            'success': True, 
            'message': 'Mensagem enviada com sucesso!',
            'message_id': whatsapp_message.id,
            'sent_at': whatsapp_message.sent_at.strftime('%d/%m/%Y %H:%M')
        })
    else:
        error_msg = 'Erro ao enviar mensagem'
        if whatsapp_message and whatsapp_message.response_data:
            error_msg = whatsapp_message.response_data.get('error', error_msg)
        
        return JsonResponse({'success': False, 'error': error_msg})

@csrf_exempt
def whatsapp_webhook(request):
    """
    Webhook to receive status updates from WhatsApp API
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Log the webhook data for debugging
        logger.info(f"WhatsApp webhook received: {data}")
        
        # Check if this is a message status update
        if 'ack' in data and 'id' in data:
            message_id = data['id']
            status_code = data['ack']
            
            # Map WhatsApp status codes to our status values
            status_map = {
                1: 'sent',      # Message sent to WhatsApp server
                2: 'delivered', # Message delivered to recipient's device
                3: 'read'       # Message read by recipient
            }
            
            status = status_map.get(status_code, 'unknown')
            
            # Try to find the message in our database by the WhatsApp message ID
            try:
                # Look for the message ID in the response_data JSON
                messages = WhatsAppMessage.objects.filter(
                    response_data__key__id=message_id
                )
                
                if messages.exists():
                    for message in messages:
                        message.status = status
                        message.save()
                        logger.info(f"Updated message {message.id} status to {status}")
                    
                    return JsonResponse({'status': 'success', 'message': 'Status updated'})
                else:
                    logger.warning(f"Message with ID {message_id} not found")
            except Exception as e:
                logger.error(f"Error updating message status: {e}")
        
        return JsonResponse({'status': 'success', 'message': 'Webhook received'})
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# Views para Categorias Profissionais
def professional_category_list(request):
    categories = ProfessionalCategory.objects.all().order_by('nome')
    return render(request, 'people/professional_category_list.html', {
        'categories': categories
    })

def update_person_status(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        reason = request.POST.get('reason')
        
        # Verificar se o status é válido
        valid_statuses = [status[0] for status in Person.STATUS_CHOICES]
        if new_status not in valid_statuses:
            messages.error(request, f'Status inválido: {new_status}')
            return redirect('people:detail', person_id=person.id)
        
        # Obter o nome do status para exibição
        status_display = dict(Person.STATUS_CHOICES).get(new_status)
        
        # Salvar o status anterior para o registro de ocorrência
        old_status_display = dict(Person.STATUS_CHOICES).get(person.status)
        
        # Atualizar o status da pessoa
        person.status = new_status
        person.save()
        
        # Criar uma ocorrência para registrar a mudança de status
        from occurrences.models import Occurrence
        
        # Obter o nome do usuário que fez a alteração
        user_name = request.user.username if request.user.is_authenticated else 'Usuário não autenticado'
        
        description = f"Status alterado de '{old_status_display}' para '{status_display}'.\n\nMotivo: {reason}"
        
        Occurrence.objects.create(
            related_to='person',
            person=person,
            description=description,
            status='resolved',  # Já marcamos como resolvido
            created_by=user_name  # Registrar o usuário que fez a alteração
        )
        
        messages.success(request, f'Status atualizado para: {status_display}')
        
    return redirect('people:detail', person_id=person.id)

def professional_category_create(request):
    if request.method == 'POST':
        form = ProfessionalCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria profissional criada com sucesso!')
            return redirect('people:professional_category_list')
    else:
        form = ProfessionalCategoryForm()
    
    return render(request, 'people/professional_category_form.html', {
        'form': form,
        'title': 'Nova Categoria Profissional'
    })

def professional_category_update(request, category_id):
    category = get_object_or_404(ProfessionalCategory, id=category_id)
    
    if request.method == 'POST':
        form = ProfessionalCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria profissional atualizada com sucesso!')
            return redirect('people:professional_category_list')
    else:
        form = ProfessionalCategoryForm(instance=category)
    
    return render(request, 'people/professional_category_form.html', {
        'form': form,
        'category': category,
        'title': 'Editar Categoria Profissional'
    })

def professional_category_delete(request, category_id):
    category = get_object_or_404(ProfessionalCategory, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Categoria profissional excluída com sucesso!")
        return redirect('people:professional_category_list')
    
    return render(request, 'people/professional_category_confirm_delete.html', {
        'category': category,
        'title': 'Excluir Categoria',
        'subtitle': f'Confirmar exclusão de: {category.nome}'
    })

# Gallery views
def person_gallery(request, person_id):
    """View para exibir e gerenciar a galeria de fotos de uma pessoa"""
    person = get_object_or_404(Person, pk=person_id)
    gallery_items = PersonGallery.objects.filter(person=person).order_by('order', 'created_at')
    
    # Verificar se a origem é da listagem ou da página de detalhes
    source = request.GET.get('source', 'detail')
    
    context = {
        'person': person,
        'gallery_items': gallery_items,
        'title': f'Galeria de Fotos: {person.name}',
        'subtitle': 'Gerenciar fotos da galeria',
        'source': source  # Adiciona a origem à context
    }
    return render(request, 'people/person_gallery.html', context)

def person_gallery_add(request, person_id):
    """View para adicionar uma nova foto à galeria"""
    person = get_object_or_404(Person, pk=person_id)
    
    # Preservar a origem
    source = request.GET.get('source', 'detail')
    
    if request.method == 'POST':
        form = PersonGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_item = form.save(commit=False)
            gallery_item.person = person
            gallery_item.save()
            messages.success(request, "Foto adicionada à galeria com sucesso!")
            return redirect(f'{reverse("people:person_gallery", args=[person.id])}?source={source}')
    else:
        form = PersonGalleryForm()
    
    context = {
        'form': form,
        'person': person,
        'title': f'Adicionar Foto: {person.name}',
        'subtitle': 'Adicionar nova foto à galeria',
        'source': source  # Adiciona a origem à context
    }
    return render(request, 'people/person_gallery_form.html', context)

def person_gallery_edit(request, person_id, gallery_id):
    """View para editar uma foto da galeria"""
    person = get_object_or_404(Person, pk=person_id)
    gallery_item = get_object_or_404(PersonGallery, pk=gallery_id, person=person)
    
    # Preservar a origem
    source = request.GET.get('source', 'detail')
    
    if request.method == 'POST':
        form = PersonGalleryForm(request.POST, request.FILES, instance=gallery_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Foto da galeria atualizada com sucesso!")
            return redirect(f'{reverse("people:person_gallery", args=[person.id])}?source={source}')
    else:
        form = PersonGalleryForm(instance=gallery_item)
    
    context = {
        'form': form,
        'person': person,
        'gallery_item': gallery_item,
        'title': f'Editar Foto: {person.name}',
        'subtitle': 'Atualizar informações da foto',
        'source': source  # Adiciona a origem à context
    }
    return render(request, 'people/person_gallery_form.html', context)

def person_gallery_delete(request, person_id, gallery_id):
    """View para excluir uma foto da galeria"""
    person = get_object_or_404(Person, pk=person_id)
    gallery_item = get_object_or_404(PersonGallery, pk=gallery_id, person=person)
    
    # Preservar a origem
    source = request.GET.get('source', 'detail')
    
    if request.method == 'POST':
        gallery_item.delete()
        messages.success(request, "Foto removida da galeria com sucesso!")
        return redirect(f'{reverse("people:person_gallery", args=[person.id])}?source={source}')
    
    context = {
        'person': person,
        'gallery_item': gallery_item,
        'title': f'Excluir Foto: {person.name}',
        'subtitle': 'Confirmar exclusão da foto',
        'source': source  # Adiciona a origem à context
    }
    return render(request, 'people/person_gallery_confirm_delete.html', context)

# Views para gerenciar comentários e perguntas
def person_comments_list(request, person_id=None):
    """
    View para listar todos os comentários e perguntas, com opção de filtrar por pessoa.
    """
    if person_id:
        person = get_object_or_404(Person, pk=person_id)
        comments = PersonComment.objects.filter(person=person).order_by('-created_at')
        title = f"Comentários e Perguntas sobre {person.name}"
    else:
        person = None
        comments = PersonComment.objects.all().order_by('-created_at')
        title = "Todos os Comentários e Perguntas"
    
    # Filtros
    filter_type = request.GET.get('type', '')
    filter_answered = request.GET.get('answered', '')
    
    if filter_type == 'question':
        comments = comments.filter(is_question=True)
    elif filter_type == 'comment':
        comments = comments.filter(is_question=False)
    
    if filter_answered == 'yes':
        comments = comments.filter(is_answered=True)
    elif filter_answered == 'no':
        comments = comments.filter(is_answered=False)
    
    return render(request, 'people/comments_list.html', {
        'person_id': person_id,
        'comments': comments,
        'person': person,
        'title': title,
        'filters': {'type': filter_type, 'status': filter_answered},
    })

def person_comment_answer(request, comment_id):
    """
    View para responder a uma pergunta.
    """
    comment = get_object_or_404(PersonComment, pk=comment_id)
    
    if request.method == 'POST':
        answer_text = request.POST.get('answer_text', '').strip()
        
        if answer_text:
            comment.answer_text = answer_text
            comment.is_answered = True
            comment.answered_at = timezone.now()
            comment.save()
            
            messages.success(request, 'Resposta enviada com sucesso!')
            
            # Redirecionar de volta para a lista de comentários da pessoa
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('people:comments_list', person_id=comment.person.id)
    
    # URL para retornar após responder
    next_url = request.GET.get('next', reverse('people:comments_list', kwargs={'person_id': comment.person.id}))
    
    return render(request, 'people/person_comment_answer.html', {
        'comment': comment,
        'next_url': next_url
    })

def person_comment_delete(request, comment_id):
    """
    View para excluir um comentário ou pergunta.
    """
    comment = get_object_or_404(PersonComment, pk=comment_id)
    person_id = comment.person.id
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comentário excluído com sucesso!')
        
        # Redirecionar de volta para a lista de comentários da pessoa
        if 'next' in request.POST:
            return redirect(request.POST.get('next'))
        return redirect('people:comments_list', person_id=person_id)
    
    # URL para retornar após excluir
    next_url = request.GET.get('next', reverse('people:comments_list', kwargs={'person_id': person_id}))
    
    return render(request, 'people/comment_delete.html', {
        'comment': comment,
        'next_url': next_url
    })

def person_comments_count(request, person_id):
    """
    View para retornar a contagem de comentários de uma pessoa.
    """
    person = get_object_or_404(Person, pk=person_id)
    count = PersonComment.objects.filter(person=person).count()
    
    return JsonResponse({
        'count': count,
        'person_id': person_id
    })

def person_views_report(request):
    """
    View para exibir relatório de visualizações de perfis.
    """
    # Obter estatísticas gerais
    total_views = PersonView.objects.count()
    unique_users = PersonView.objects.values('user').distinct().count()
    unique_sessions = PersonView.objects.values('session_key').distinct().count()
    
    # Pessoas mais visualizadas
    most_viewed = Person.objects.annotate(
        view_count=Count('views')
    ).order_by('-view_count')[:20]
    
    # Visualizações recentes
    recent_views = PersonView.objects.select_related('person', 'user').order_by('-timestamp')[:50]
    
    # Filtros
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    person_filter = request.GET.get('person', '')
    
    filtered_views = PersonView.objects.all()
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            filtered_views = filtered_views.filter(timestamp__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            filtered_views = filtered_views.filter(timestamp__lte=date_to)
        except ValueError:
            pass
    
    if person_filter:
        filtered_views = filtered_views.filter(person__name__icontains=person_filter)
    
    return render(request, 'people/views_report.html', {
        'total_views': total_views,
        'unique_users': unique_users,
        'unique_sessions': unique_sessions,
        'most_viewed': most_viewed,
        'recent_views': recent_views,
        'filtered_views': filtered_views,
        'date_from': date_from,
        'date_to': date_to,
        'person_filter': person_filter
    })
