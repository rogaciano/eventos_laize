from django.urls import path
from . import views
from . import views_casting
from . import views_public

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
    
    # URLs para Catálogo de Casting
    path('casting-catalogs/', views_casting.casting_catalog_list, name='casting_catalog_list'),
    path('casting-catalogs/create/', views_casting.casting_catalog_create, name='casting_catalog_create'),
    path('casting-catalogs/create-from-filter/', views_casting.create_catalog_from_filter, name='create_catalog_from_filter'),
    path('casting-catalogs/<int:pk>/', views_casting.casting_catalog_detail, name='casting_catalog_detail'),
    path('casting-catalogs/<int:pk>/edit/', views_casting.casting_catalog_edit, name='casting_catalog_edit'),
    path('casting-catalogs/<int:pk>/delete/', views_casting.casting_catalog_delete, name='casting_catalog_delete'),
    path('casting-catalogs/<int:catalog_pk>/add-person/<int:person_pk>/', views_casting.casting_catalog_add_person, name='casting_catalog_add_person'),
    path('casting-catalogs/<int:catalog_pk>/remove-person/<int:person_pk>/', views_casting.casting_catalog_remove_person, name='casting_catalog_remove_person'),
    
    # URLs para acesso público a catálogos
    path('casting-catalogs/<int:catalog_id>/generate-link/', views_public.generate_public_link, name='generate_public_link'),
    path('public/catalog/<int:catalog_id>/<str:signature>/', views_public.public_catalog_view, name='public_catalog_view'),
]
