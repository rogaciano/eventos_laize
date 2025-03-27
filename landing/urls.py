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
    path('cadastro/', views.register, name='register'),
    
    # URLs para gerenciamento de mensagens
    path('mensagens/', views.message_list, name='message_list'),
    path('mensagens/<int:pk>/', views.message_detail, name='message_detail'),
    path('mensagens/<int:pk>/marcar-como-lida/', views.message_mark_as_read, name='message_mark_as_read'),
    path('mensagens/<int:pk>/marcar-como-nao-lida/', views.message_mark_as_unread, name='message_mark_as_unread'),
    
    # URLs para gerenciamento de blog
    path('blog/', views.post_list, name='post_list'),
    path('blog/novo/', views.post_create, name='post_create'),
    path('blog/<int:pk>/editar/', views.post_update, name='post_update'),
    path('blog/<int:pk>/excluir/', views.post_delete, name='post_delete'),
    path('blog/<int:pk>/preview/', views.post_detail_preview, name='post_detail_preview'),
]
