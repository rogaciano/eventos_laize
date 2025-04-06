from django.urls import path
from . import views_public

urlpatterns = [
    # URL principal do catálogo
    path('catalog/<int:catalog_id>/signature/<str:signature>/', views_public.public_catalog_view, name='public_catalog_view'),
    
    # URLs para AJAX
    path('catalog/<int:catalog_id>/person/<int:person_id>/view/', views_public.record_person_view, name='record_person_view'),
    path('catalog/<int:catalog_id>/person/<int:person_id>/comments/', views_public.get_person_comments, name='get_person_comments'),
    path('catalog/<int:catalog_id>/person/<int:person_id>/select/', views_public.toggle_person_selection, name='toggle_person_selection'),
    path('catalog/<int:catalog_id>/selected/', views_public.get_selected_people, name='get_selected_people'),
]
