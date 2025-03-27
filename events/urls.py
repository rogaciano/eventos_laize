from django.urls import path, include
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
    path('<int:event_id>/participants/confirm-add/', views.confirm_add_participant, name='confirm_add_participant'),
    path('<int:event_id>/participants/<int:participant_id>/remove/', views.remove_participant, name='remove_participant'),
    path('<int:event_id>/participants/<int:participant_id>/edit/', views.update_participant, name='update_participant'),
    
    # Função URLs
    path('funcoes/create/', views.funcao_create, name='funcao_create'),
    path('funcoes/nova/', views.funcao_create_page, name='funcao_create_page'),
    path('funcoes/<int:funcao_id>/valor_padrao/', views.funcao_valor_padrao, name='funcao_valor_padrao'),
    path('funcoes/', views.funcao_list, name='funcao_list'),
    path('funcoes/<int:funcao_id>/edit/', views.funcao_edit, name='funcao_edit'),
    path('funcoes/<int:funcao_id>/delete/', views.funcao_delete, name='funcao_delete'),
    
    # Calendar URLs
    path('calendar/', views.event_calendar, name='calendar'),
    path('calendar/data/', views.event_calendar_data, name='calendar_data'),
    
    # Incluir URLs de gestão de custos
    path('cost/', include('events.urls_cost')),
    
    # Cost URLs
    path('event/<int:event_id>/costs/', views.event_costs, name='event_costs'),
    path('event/<int:event_id>/cost/add/', views.event_cost_add, name='event_cost_add'),
    path('event/<int:event_id>/cost/<int:cost_id>/edit/', views.event_cost_edit, name='event_cost_edit'),
    path('event/<int:event_id>/cost/<int:cost_id>/delete/', views.event_cost_delete, name='event_cost_delete'),
    
    # Gallery URLs
    path('event/<int:event_id>/gallery/', views.event_gallery, name='event_gallery'),
    path('event/<int:event_id>/gallery/add/', views.event_gallery_add, name='event_gallery_add'),
    path('event/<int:event_id>/gallery/<int:photo_id>/edit/', views.event_gallery_edit, name='event_gallery_edit'),
    path('event/<int:event_id>/gallery/<int:photo_id>/delete/', views.event_gallery_delete, name='event_gallery_delete'),
    
    # Budget URLs
    path('event/<int:event_id>/budget/', views.event_budget, name='event_budget'),
    path('event/<int:event_id>/budget/item/add/', views.event_budget_item_add, name='event_budget_item_add'),
    path('event/<int:event_id>/budget/item/<int:item_id>/edit/', views.event_budget_item_edit, name='event_budget_item_edit'),
    path('event/<int:event_id>/budget/item/<int:item_id>/delete/', views.event_budget_item_delete, name='event_budget_item_delete'),
    path('event/<int:event_id>/budget/settings/', views.event_budget_settings, name='event_budget_settings'),
    path('event/<int:event_id>/budget/pdf/', views.event_budget_pdf, name='event_budget_pdf'),
    path('budget/default-settings/', views.default_budget_settings, name='default_budget_settings'),
    
    # Company Settings URL
    path('company/settings/', views.company_settings, name='company_settings'),
]
