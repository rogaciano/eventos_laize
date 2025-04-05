"""
URL configuration for eventos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Redirect root URL to login
    # path('', RedirectView.as_view(pattern_name='login'), name='root'),
    
    path('admin/', admin.site.urls),
    
    # Landing page
    path('', include('landing.urls')),
    
    # URL pública para catálogos (fora do namespace sistema/)
    path('public/catalog/<int:catalog_id>/<str:signature>/', include('people.urls_public')),
    
    # Sistema de gestão (área restrita)
    path('sistema/', include([
        path('', RedirectView.as_view(pattern_name='dashboard:dashboard'), name='sistema_home'),
        path('dashboard/', include('dashboard.urls')),
        path('events/', include('events.urls')),
        path('people/', include('people.urls')),
        path('clients/', include('clients.urls')),
        path('occurrences/', include('occurrences.urls')),
    ])),
    
    # Autenticação
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Password reset URLs
    # path('password_reset/', 
    #      auth_views.PasswordResetView.as_view(
    #          template_name='auth/password_reset_form.html',
    #          email_template_name='auth/password_reset_email.html',
    #          subject_template_name='auth/password_reset_subject.txt'
    #      ), 
    #      name='password_reset'),
    # path('password_reset/done/', 
    #      auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), 
    #      name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', 
    #      auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), 
    #      name='password_reset_confirm'),
    # path('reset/done/', 
    #      auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), 
    #      name='password_reset_complete'),
]

# Add media URL handling for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
