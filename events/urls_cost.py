from django.urls import path
from . import views_cost

urlpatterns = [
    # Categorias de Custos
    path('cost-categories/', views_cost.cost_category_list, name='cost_category_list'),
    path('cost-categories/create/', views_cost.cost_category_create, name='cost_category_create'),
    path('cost-categories/<int:category_id>/update/', views_cost.cost_category_update, name='cost_category_update'),
    path('cost-categories/<int:category_id>/delete/', views_cost.cost_category_delete, name='cost_category_delete'),
    
    # Custos de Eventos
    path('<int:event_id>/costs/', views_cost.event_costs, name='event_costs'),
    path('<int:event_id>/costs/add/', views_cost.add_event_cost, name='add_event_cost'),
    path('<int:event_id>/costs/<int:cost_id>/update/', views_cost.update_event_cost, name='update_event_cost'),
    path('<int:event_id>/costs/<int:cost_id>/delete/', views_cost.delete_event_cost, name='delete_event_cost'),
    
    # Relatórios Financeiros
    path('financial-report/', views_cost.financial_report, name='financial_report'),
    path('<int:event_id>/export-financial-data/', views_cost.export_financial_data, name='export_financial_data'),
]
