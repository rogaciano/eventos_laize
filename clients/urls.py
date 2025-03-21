from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='list'),
    path('add/', views.client_create, name='create'),
    path('<int:client_id>/', views.client_detail, name='detail'),
    path('<int:client_id>/edit/', views.client_update, name='update'),
    path('<int:client_id>/delete/', views.client_delete, name='delete'),
    path('classes/', views.client_class_list, name='class_list'),
    path('classes/add/', views.client_class_create, name='class_create'),
    path('classes/<int:class_id>/edit/', views.client_class_update, name='class_update'),
    path('classes/<int:class_id>/delete/', views.client_class_delete, name='class_delete'),
]
