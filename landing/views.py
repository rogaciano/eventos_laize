from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import Service, Testimonial, Post, SiteSettings
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
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Enviar e-mail
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            email_message = f"""
            Nome: {name}
            E-mail: {email}
            Telefone: {phone}
            
            Mensagem:
            {message}
            """
            
            try:
                send_mail(
                    f"Contato do site: {subject}",
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [site_settings.contact_email],
                    fail_silently=False,
                )
                messages.success(request, "Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.")
                return redirect('landing:contact')
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao enviar sua mensagem. Por favor, tente novamente mais tarde.")
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'site_settings': site_settings,
    }
    return render(request, 'landing/contact.html', context)
