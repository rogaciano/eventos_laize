from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class LoginRequiredMiddleware:
    """
    Middleware to ensure users are authenticated for all pages except those explicitly excluded.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't require authentication
        self.public_urls = [
            reverse('login'),
            reverse('logout'),
            reverse('password_reset'),
            reverse('password_reset_done'),
            reverse('password_reset_complete'),
            '/admin/login/',
            '/static/',
            '/media/',
            # Landing page URLs
            reverse('landing:home'),
            reverse('landing:about'),
            reverse('landing:services'),
            reverse('landing:blog'),
            reverse('landing:contact'),
            reverse('landing:register'),  # Adicionando a URL de registro
            '/',  # Root URL
        ]
        # Add password reset confirm URL pattern (can't use reverse with parameters)
        self.public_patterns = [
            '/reset/',
            '/landing/',  # Todas as URLs que começam com /landing/
            '/novidades/', # Para acessar a página de blog
            '/sistema/people/public/',  # Todas as URLs públicas do módulo people
        ]

    def __call__(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Check if the current path is in the public URLs
            if request.path_info not in self.public_urls and not any(
                request.path_info.startswith(pattern) for pattern in self.public_patterns
            ):
                # If not, redirect to login page with next parameter
                return redirect(f"{reverse('login')}?next={request.path}")
        
        response = self.get_response(request)
        return response
