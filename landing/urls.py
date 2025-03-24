from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
    path('sobre/', views.about, name='about'),
    path('servicos/', views.services, name='services'),
    path('novidades/', views.blog, name='blog'),
    path('novidades/<slug:slug>/', views.post_detail, name='post_detail'),
    path('contato/', views.contact, name='contact'),
]
