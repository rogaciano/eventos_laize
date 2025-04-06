from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.core.signing import Signer, BadSignature, SignatureExpired
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse

from .models_casting import CastingCatalog

def public_catalog_view(request, catalog_id, signature):
    """
    View para visualização pública de catálogos de casting sem necessidade de login
    """
    # Verificar a assinatura
    signer = Signer()
    try:
        # Verificar se a assinatura é válida para o ID do catálogo
        # A assinatura já vem sem os dois pontos, então precisamos adicioná-los de volta
        full_signature = f"{catalog_id}:{signature}"
        
        # Verificar se a assinatura é válida
        unsigned_value = signer.unsign(full_signature)
        if unsigned_value != str(catalog_id):
            raise Http404("Link inválido")
    except (BadSignature, SignatureExpired):
        raise Http404("Link inválido ou expirado")
    
    # Obter o catálogo
    catalog = get_object_or_404(CastingCatalog, pk=catalog_id)
    
    # Verificar se o catálogo está ativo
    if not catalog.is_active:
        return render(request, 'people/public_catalog_expired.html', {'catalog': catalog})
    
    # Obter as pessoas do catálogo
    persons = catalog.get_filtered_people()
    
    context = {
        'catalog': catalog,
        'persons': persons,
        'is_public_view': True,
    }
    
    return render(request, 'people/public_catalog_view.html', context)

def generate_public_link(request, catalog_id):
    """
    Gera um link público para um catálogo de casting
    """
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para gerar links públicos.")
        return redirect('login')
    
    catalog = get_object_or_404(CastingCatalog, pk=catalog_id)
    
    # Gerar assinatura para o ID do catálogo
    signer = Signer()
    signature = signer.sign(str(catalog_id))
    
    # Extrair apenas a parte da assinatura após os dois pontos
    signature = signature.split(':')[1]
    
    # Gerar URL pública
    public_url = reverse('public_catalog_view', kwargs={
        'catalog_id': catalog_id,
        'signature': signature
    })
    
    # URL completa (incluindo domínio)
    full_url = request.build_absolute_uri(public_url)
    
    context = {
        'catalog': catalog,
        'public_url': public_url,
        'full_url': full_url,
    }
    
    return render(request, 'people/public_link_generated.html', context)
