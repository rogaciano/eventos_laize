from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    path('', views.person_list, name='list'),
    path('add/', views.person_create, name='create'),
    path('<int:person_id>/', views.person_detail, name='detail'),
    path('<int:person_id>/edit/', views.person_update, name='update'),
    path('<int:person_id>/delete/', views.person_delete, name='delete'),
    path('<int:person_id>/update-status/', views.update_person_status, name='update_status'),
    path('<int:person_id>/contacts/add/', views.person_contact_add, name='contact_add'),
    path('<int:person_id>/contacts/<int:contact_id>/edit/', views.person_contact_edit, name='contact_edit'),
    path('<int:person_id>/contacts/<int:contact_id>/delete/', views.person_contact_delete, name='contact_delete'),
    path('report/pdf/', views.generate_person_report_pdf, name='report_pdf'),
    # WhatsApp
    path('person/<int:person_id>/whatsapp/', views.send_whatsapp, name='send_whatsapp'),
    path('person/<int:person_id>/whatsapp/<int:contact_id>/', views.send_whatsapp, name='send_whatsapp_contact'),
    path('person/<int:person_id>/whatsapp-history/', views.whatsapp_history, name='whatsapp_history'),
    path('person/<int:person_id>/whatsapp-ajax/', views.send_whatsapp_ajax, name='send_whatsapp_ajax'),
    path('whatsapp-webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
    
    # Professional Category URLs
    path('professional-categories/', views.professional_category_list, name='professional_category_list'),
    path('professional-categories/add/', views.professional_category_create, name='professional_category_create'),
    path('professional-categories/<int:category_id>/edit/', views.professional_category_update, name='professional_category_update'),
    path('professional-categories/<int:category_id>/delete/', views.professional_category_delete, name='professional_category_delete'),
    
    # Gallery URLs
    path('person/<int:person_id>/gallery/', views.person_gallery, name='person_gallery'),
    path('person/<int:person_id>/gallery/add/', views.person_gallery_add, name='person_gallery_add'),
    path('person/<int:person_id>/gallery/<int:gallery_id>/edit/', views.person_gallery_edit, name='person_gallery_edit'),
    path('person/<int:person_id>/gallery/<int:gallery_id>/delete/', views.person_gallery_delete, name='person_gallery_delete'),
]
