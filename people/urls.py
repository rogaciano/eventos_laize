from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    path('', views.person_list, name='list'),
    path('add/', views.person_create, name='create'),
    path('<int:person_id>/', views.person_detail, name='detail'),
    path('<int:person_id>/edit/', views.person_update, name='update'),
    path('<int:person_id>/delete/', views.person_delete, name='delete'),
    path('<int:person_id>/contacts/add/', views.person_contact_add, name='contact_add'),
    path('<int:person_id>/contacts/<int:contact_id>/edit/', views.person_contact_edit, name='contact_edit'),
    path('<int:person_id>/contacts/<int:contact_id>/delete/', views.person_contact_delete, name='contact_delete'),
    path('report/pdf/', views.generate_person_report_pdf, name='report_pdf'),
]
