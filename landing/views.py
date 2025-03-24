from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Service, Testimonial, Post, SiteSettings, Message
from .forms import ContactForm

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
                Message.objects.create(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message']
                )
                form_sent = True
                form = ContactForm()  # Limpar o formulário
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

@login_required
def message_list(request):
    """View para listar todas as mensagens"""
    messages_list = Message.objects.all()
    unread_count = Message.objects.filter(is_read=False).count()
    
    context = {
        'messages_list': messages_list,
        'unread_count': unread_count,
        'title': 'Mensagens',
        'subtitle': 'Gerenciar mensagens recebidas pelo site'
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
