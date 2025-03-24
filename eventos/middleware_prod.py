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
        ]
        # Add password reset confirm URL pattern and landing page patterns (can't use reverse with parameters)
        self.public_patterns = [
            '/reset/',
            '/blog/post/',  # Para detalhes de posts do blog
        ]

    def __call__(self, request):
        # Check if the request is for the landing page (starts with /, but not /sistema/)
        if request.path_info == '/' or (
            not request.path_info.startswith('/sistema/') and 
            not request.path_info.startswith('/admin/') and
            any(request.path_info.startswith(pattern[1:]) for pattern in [
                reverse('landing:home'),
                reverse('landing:about'),
                reverse('landing:services'),
                reverse('landing:blog'),
                reverse('landing:contact')
            ])
        ):
            # Allow access to landing page without authentication
            return self.get_response(request)
            
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
