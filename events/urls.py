from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event URLs
    path('', views.event_list, name='list'),
    path('<int:event_id>/', views.event_detail, name='detail'),
    path('add/', views.event_create, name='create'),
    path('<int:event_id>/edit/', views.event_update, name='update'),
    path('<int:event_id>/delete/', views.event_delete, name='delete'),
    
    # Event Status History URLs
    path('<int:event_id>/status-history/', views.event_status_history, name='status_history'),
    path('<int:event_id>/change-status/', views.change_event_status, name='change_status'),
    
    # Event Type URLs
    path('types/', views.event_type_list, name='type_list'),
    path('types/add/', views.event_type_create, name='type_create'),
    path('types/<int:type_id>/edit/', views.event_type_update, name='type_update'),
    path('types/<int:type_id>/delete/', views.event_type_delete, name='type_delete'),
    
    # Event Participant URLs
    path('<int:event_id>/participants/add/', views.add_participant, name='add_participant'),
    path('<int:event_id>/participants/<int:participant_id>/remove/', views.remove_participant, name='remove_participant'),
    path('<int:event_id>/participants/<int:participant_id>/edit/', views.update_participant, name='update_participant'),
    
    # Função URLs
    path('funcoes/create/', views.funcao_create, name='funcao_create'),
    path('funcoes/nova/', views.funcao_create_page, name='funcao_create_page'),
    path('funcoes/<int:funcao_id>/valor_padrao/', views.funcao_valor_padrao, name='funcao_valor_padrao'),
    path('funcoes/', views.funcao_list, name='funcao_list'),
    path('funcoes/<int:funcao_id>/edit/', views.funcao_edit, name='funcao_edit'),
    path('funcoes/<int:funcao_id>/delete/', views.funcao_delete, name='funcao_delete'),
]
