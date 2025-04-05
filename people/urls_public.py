from django.urls import path
from . import views_public

urlpatterns = [
    path('', views_public.public_catalog_view, name='public_catalog_view'),
]
