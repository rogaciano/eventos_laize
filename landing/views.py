from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Service, Testimonial, Post, SiteSettings, Message
from .forms import ContactForm, RegistrationForm, PostForm
from django.db.models import Q
from django.core.paginator import Paginator
from people.models import Person, PersonContact, ProfessionalCategory
from notifications.whatsapp import WhatsAppManager

def get_site_settings():
    """Retorna as configurações do site ou cria um padrão se não existir"""
    settings, created = SiteSettings.objects.get_or_create(pk=1)
    return settings

def home(request):
    """View para a página inicial"""
    services = Service.objects.all()[:6]
    testimonials = Testimonial.objects.filter(active=True)[:3]
    recent_posts = Post.objects.filter(is_published=True)[:3]
    site_settings = get_site_settings()
    
    context = {
        'services': services,
        'testimonials': testimonials,
        'recent_posts': recent_posts,
        'site_settings': site_settings,
    }
    return render(request, 'landing/home.html', context)

def about(request):
    """View para a página Sobre Nós"""
    testimonials = Testimonial.objects.filter(active=True)
    site_settings = get_site_settings()
    
    context = {
        'testimonials': testimonials,
        'site_settings': site_settings,
    }
    return render(request, 'landing/about.html', context)

def services(request):
    """View para a página de Serviços"""
    services = Service.objects.all()
    site_settings = get_site_settings()
    
    context = {
        'services': services,
        'site_settings': site_settings,
    }
    return render(request, 'landing/services.html', context)

def blog(request):
    """View para a página de Blog/Novidades"""
    posts = Post.objects.filter(is_published=True)
    site_settings = get_site_settings()
    
    context = {
        'posts': posts,
        'site_settings': site_settings,
    }
    return render(request, 'landing/blog.html', context)

def post_detail(request, slug):
    """View para a página de detalhes de um post"""
    post = get_object_or_404(Post, slug=slug, is_published=True)
    recent_posts = Post.objects.filter(is_published=True).exclude(id=post.id)[:3]
    site_settings = get_site_settings()
    
    context = {
        'post': post,
        'recent_posts': recent_posts,
        'site_settings': site_settings,
    }
    return render(request, 'landing/post_detail.html', context)

def contact(request):
    """View para a página de Contato"""
    site_settings = get_site_settings()
    form_sent = False
    form_error = False
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Salvar mensagem no banco de dados
            try:
                message = Message.objects.create(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message']
                )
                form_sent = True
                form = ContactForm()  # Limpar o formulário
                
                # Enviar notificação WhatsApp para o gestor
                try:
                    whatsapp_manager = WhatsAppManager()
                    whatsapp_manager.notify_new_contact(message)
                except Exception as e:
                    print(f"Erro ao enviar notificação WhatsApp: {e}")
                    
            except Exception as e:
                form_error = True
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'site_settings': site_settings,
        'form_sent': form_sent,
        'form_error': form_error
    }
    return render(request, 'landing/contact.html', context)

def register(request):
    """View para a página de cadastro de pessoas"""
    site_settings = get_site_settings()
    form_sent = False
    form_error = False
    
    # Obter categorias profissionais para o formulário
    professional_categories = ProfessionalCategory.objects.all()
    
    if request.method == 'POST':
        # Converter vírgula para ponto no campo altura
        post_data = request.POST.copy()
        if 'altura' in post_data and post_data['altura']:
            post_data['altura'] = post_data['altura'].replace(',', '.')
            
        form = RegistrationForm(post_data, request.FILES)
        if form.is_valid():
            try:
                # Salvar pessoa com status pendente
                person = form.save(commit=False)
                person.status = 'pendente'
                person.origem_cadastro = 'externo'
                person.save()
                
                # Salvar categorias profissionais
                form.save_m2m()
                
                # Adicionar contatos
                if form.cleaned_data['contact_email']:
                    PersonContact.objects.create(
                        person=person,
                        type='email',
                        value=form.cleaned_data['contact_email'],
                        label='Principal'
                    )
                
                if form.cleaned_data['contact_phone']:
                    PersonContact.objects.create(
                        person=person,
                        type='whatsapp',
                        value=form.cleaned_data['contact_phone'],
                        label='Principal'
                    )
                
                form_sent = True
                form = RegistrationForm()  # Limpar o formulário
                
                # Enviar notificação WhatsApp para o gestor
                try:
                    whatsapp_manager = WhatsAppManager()
                    whatsapp_manager.notify_new_registration(person)
                except Exception as e:
                    print(f"Erro ao enviar notificação WhatsApp: {e}")
                
            except Exception as e:
                form_error = True
                print(f"Erro ao salvar registro: {e}")
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
        'site_settings': site_settings,
        'form_sent': form_sent,
        'form_error': form_error,
        'professional_categories': professional_categories,
        'title': 'Cadastre-se',
        'subtitle': 'Faça parte do nosso time de profissionais'
    }
    return render(request, 'landing/register.html', context)

@login_required
def message_list(request):
    """View para listar todas as mensagens"""
    messages_query = Message.objects.all()
    
    # Filtro por status (lida/não lida)
    status_filter = request.GET.get('status')
    if status_filter == 'read':
        messages_query = messages_query.filter(is_read=True)
    elif status_filter == 'unread':
        messages_query = messages_query.filter(is_read=False)
    
    # Filtro por período
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            messages_query = messages_query.filter(created_at__date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            # Adiciona um dia ao end_date para incluir mensagens do próprio dia
            end_date_obj = timezone.datetime.combine(end_date_obj, timezone.datetime.max.time())
            messages_query = messages_query.filter(created_at__lte=end_date_obj)
        except ValueError:
            pass
    
    # Filtro por busca (nome ou assunto)
    search_query = request.GET.get('search', '')
    if search_query:
        messages_query = messages_query.filter(
            Q(name__icontains=search_query) | 
            Q(subject__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Contagem de mensagens não lidas
    unread_count = Message.objects.filter(is_read=False).count()
    
    context = {
        'messages_list': messages_query,
        'unread_count': unread_count,
        'title': 'Mensagens',
        'subtitle': 'Gerenciar mensagens recebidas pelo site',
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
        'search_query': search_query,
    }
    return render(request, 'landing/message_list.html', context)

@login_required
def message_detail(request, pk):
    """View para visualizar detalhes de uma mensagem"""
    message = get_object_or_404(Message, pk=pk)
    
    # Marcar como lida automaticamente ao visualizar
    if not message.is_read:
        message.mark_as_read()
    
    context = {
        'message': message,
        'title': f'Mensagem: {message.subject}',
        'subtitle': f'De: {message.name}'
    }
    return render(request, 'landing/message_detail.html', context)

@login_required
def message_mark_as_read(request, pk):
    """View para marcar uma mensagem como lida"""
    message = get_object_or_404(Message, pk=pk)
    message.mark_as_read()
    messages.success(request, "Mensagem marcada como lida.")
    return redirect('landing:message_list')

@login_required
def message_mark_as_unread(request, pk):
    """View para marcar uma mensagem como não lida"""
    message = get_object_or_404(Message, pk=pk)
    message.is_read = False
    message.read_at = None
    message.save()
    messages.success(request, "Mensagem marcada como não lida.")
    return redirect('landing:message_list')

def get_unread_messages_count():
    """Função auxiliar para obter o número de mensagens não lidas"""
    return Message.objects.filter(is_read=False).count()

# Views para gerenciamento de posts do blog
@login_required
def post_list(request):
    """View para listar e gerenciar posts do blog"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    posts = Post.objects.all().order_by('-published_at')
    
    # Aplicar filtros
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    if status_filter:
        if status_filter == 'published':
            posts = posts.filter(is_published=True)
        elif status_filter == 'draft':
            posts = posts.filter(is_published=False)
    
    # Paginação
    paginator = Paginator(posts, 10)  # 10 posts por página
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)
    
    context = {
        'posts': posts_page,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'landing/post_list.html', context)

@login_required
def post_create(request):
    """View para criar um novo post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            messages.success(request, 'Post criado com sucesso!')
            return redirect('landing:post_list')
    else:
        form = PostForm(initial={'published_at': timezone.now()})
    
    context = {
        'form': form,
    }
    return render(request, 'landing/post_form.html', context)

@login_required
def post_update(request, pk):
    """View para atualizar um post existente"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        # Verificar se deve remover a imagem
        if 'remove_image' in request.POST and post.image:
            post.image.delete()
        
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post atualizado com sucesso!')
            return redirect('landing:post_list')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'landing/post_form.html', context)

@login_required
def post_delete(request, pk):
    """View para excluir um post"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post excluído com sucesso!')
        return redirect('landing:post_list')
    
    context = {
        'post': post,
    }
    return render(request, 'landing/post_confirm_delete.html', context)

@login_required
def post_detail_preview(request, pk):
    """View para visualizar um post (preview interno)"""
    post = get_object_or_404(Post, pk=pk)
    site_settings = get_site_settings()
    
    context = {
        'post': post,
        'site_settings': site_settings,
        'is_preview': True,
    }
    return render(request, 'landing/post_detail.html', context)
