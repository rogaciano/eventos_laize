from django.urls import path
from . import views

app_name = 'occurrences'

urlpatterns = [
    path('', views.occurrence_list, name='list'),
    path('add/', views.occurrence_create, name='create'),
    path('<int:occurrence_id>/', views.occurrence_detail, name='detail'),
    path('<int:occurrence_id>/edit/', views.occurrence_update, name='update'),
    path('<int:occurrence_id>/delete/', views.occurrence_delete, name='delete'),
    path('<int:occurrence_id>/status/<str:new_status>/', views.occurrence_update_status, name='update_status'),
]
