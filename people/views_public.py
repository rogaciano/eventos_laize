from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.core.signing import Signer, BadSignature, SignatureExpired
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpRequest
import json

from .models_casting import CastingCatalog
from .models import Person, PersonView, PersonComment, PersonSelection

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
    
    # Inicializar a sessão se não existir
    if not request.session.session_key:
        request.session.save()
    
    # Obter as pessoas do catálogo
    persons = catalog.get_filtered_people()
    
    # Obter pessoas selecionadas para este catálogo e sessão
    session_key = request.session.session_key
    selected_person_ids = list(PersonSelection.objects.filter(
        catalog=catalog,
        session_key=session_key
    ).values_list('person_id', flat=True))
    
    # Criar uma lista ordenada com selecionados primeiro
    if selected_person_ids:
        # Criar uma lista de pessoas selecionadas
        selected_persons = list(persons.filter(id__in=selected_person_ids))
        # Criar uma lista de pessoas não selecionadas
        unselected_persons = list(persons.exclude(id__in=selected_person_ids))
        # Combinar as duas listas
        persons = selected_persons + unselected_persons
    
    # Processar comentários/perguntas
    if request.method == 'POST' and 'comment_text' in request.POST:
        # Verificar se é uma requisição AJAX para evitar processamento duplicado
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        person_id = request.POST.get('person_id')
        comment_text = request.POST.get('comment_text', '').strip()
        is_question = request.POST.get('is_question', '') == 'on'
        
        if comment_text and person_id:
            try:
                person = Person.objects.get(pk=person_id)
                comment = PersonComment.objects.create(
                    person=person,
                    catalog=catalog,
                    user=request.user if request.user.is_authenticated else None,
                    comment_text=comment_text,
                    is_question=is_question
                )
                
                # Se for uma solicitação AJAX, retornar JSON
                if is_ajax:
                    return JsonResponse({
                        'success': True
                    })
                
                # Apenas adicionar mensagem de sucesso para requisições não-AJAX
                messages.success(request, 'Seu comentário foi enviado com sucesso!')
            except Person.DoesNotExist:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'error': 'Pessoa não encontrada.'
                    })
                messages.error(request, 'Pessoa não encontrada.')
            
            # Apenas redirecionar para requisições não-AJAX
            if not is_ajax:
                return redirect('people:public_catalog_view', catalog_id=catalog_id, signature=signature)
    
    context = {
        'catalog': catalog,
        'persons': persons,
        'is_public_view': True,
        'selected_person_ids': selected_person_ids,
        'signature': signature,
    }
    
    return render(request, 'people/public_catalog_view.html', context)

@csrf_exempt
def record_person_view(request, catalog_id, person_id):
    """
    Endpoint AJAX para registrar visualização de perfil no catálogo público
    """
    if request.method == 'POST':
        try:
            catalog = CastingCatalog.objects.get(pk=catalog_id)
            person = Person.objects.get(pk=person_id)
            
            # Inicializar a sessão se não existir
            if not request.session.session_key:
                request.session.save()
                
            # Registrar visualização
            ip_address = request.META.get('REMOTE_ADDR', '')
            session_key = request.session.session_key
            
            PersonView.objects.create(
                person=person,
                catalog=catalog,
                user=request.user if request.user.is_authenticated else None,
                ip_address=ip_address,
                session_key=session_key
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Visualização registrada com sucesso'
            })
        except (CastingCatalog.DoesNotExist, Person.DoesNotExist):
            return JsonResponse({
                'success': False,
                'error': 'Catálogo ou pessoa não encontrados'
            }, status=404)
    
    return JsonResponse({
        'success': False,
        'error': 'Método não permitido'
    }, status=405)

def get_person_comments(request, catalog_id, person_id):
    """
    Endpoint para obter comentários de uma pessoa em um catálogo específico via AJAX
    """
    try:
        person = Person.objects.get(pk=person_id)
        catalog = CastingCatalog.objects.get(pk=catalog_id)
        
        # Obter comentários
        comments = PersonComment.objects.filter(
            person=person,
            catalog=catalog
        ).order_by('-created_at')
        
        # Formatar para JSON
        comments_data = []
        for comment in comments:
            comment_data = {
                'id': comment.id,
                'comment_text': comment.comment_text,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_question': comment.is_question,
                'is_answered': bool(comment.answer_text),
                'answer_text': comment.answer_text or '',
            }
            
            if comment.answered_at:
                comment_data['answered_at'] = comment.answered_at.strftime('%d/%m/%Y %H:%M')
            else:
                comment_data['answered_at'] = None
                
            comments_data.append(comment_data)
        
        return JsonResponse({
            'success': True,
            'comments': comments_data
        })
    except (Person.DoesNotExist, CastingCatalog.DoesNotExist) as e:
        return JsonResponse({
            'success': False,
            'error': f'Pessoa ou catálogo não encontrados: {str(e)}'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao carregar comentários: {str(e)}'
        }, status=500)

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
    public_url = reverse('people:public_catalog_view', kwargs={
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

@require_POST
def toggle_person_selection(request, catalog_id, person_id):
    """
    View para alternar a seleção de uma pessoa em um catálogo
    """
    # Obter o catálogo e a pessoa
    catalog = get_object_or_404(CastingCatalog, pk=catalog_id)
    person = get_object_or_404(Person, pk=person_id)
    
    # Inicializar a sessão se não existir
    if not request.session.session_key:
        request.session.save()
    
    session_key = request.session.session_key
    
    # Verificar se a pessoa já está selecionada
    try:
        data = json.loads(request.body)
        selected = data.get('selected', True)  # Por padrão, seleciona
    except json.JSONDecodeError:
        selected = True  # Se não houver dados JSON, assume que estamos selecionando
    
    # Verificar se já existe uma seleção para esta pessoa neste catálogo
    selection = PersonSelection.objects.filter(
        catalog=catalog,
        person=person,
        session_key=session_key
    ).first()
    
    if selected:
        # Se estamos selecionando e não existe seleção, criar uma nova
        if not selection:
            selection = PersonSelection(
                catalog=catalog,
                person=person,
                session_key=session_key
            )
            selection.save()
            is_selected = True
        else:
            # Já está selecionada, não faz nada
            is_selected = True
    else:
        # Se estamos desselecionando e existe seleção, remover
        if selection:
            selection.delete()
            is_selected = False
        else:
            # Já está desselecionada, não faz nada
            is_selected = False
    
    return JsonResponse({
        'success': True,
        'is_selected': is_selected,
        'person_id': person_id
    })

@csrf_exempt
def get_selected_people(request, catalog_id):
    """
    Endpoint AJAX para obter as pessoas selecionadas em um catálogo
    """
    try:
        catalog = CastingCatalog.objects.get(pk=catalog_id)
        
        # Inicializar a sessão se não existir
        if not request.session.session_key:
            request.session.save()
            
        session_key = request.session.session_key
        
        # Obter seleções
        selections = PersonSelection.objects.filter(
            catalog=catalog,
            session_key=session_key
        ).select_related('person')
        
        # Formatar para JSON
        selected_people = []
        for selection in selections:
            person = selection.person
            person_data = {
                'id': person.id,
                'name': person.name,
                'photo': request.build_absolute_uri(person.photo.url) if person.photo else None,
            }
            selected_people.append(person_data)
        
        return JsonResponse({
            'success': True,
            'selected_people': selected_people
        })
    except CastingCatalog.DoesNotExist as e:
        return JsonResponse({
            'success': False,
            'error': f'Catálogo não encontrado: {str(e)}'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao obter pessoas selecionadas: {str(e)}'
        }, status=500)

def public_person_gallery(request, catalog_id, person_id, signature):
    """
    View para exibir a galeria de fotos de uma pessoa no catálogo público
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
    
    # Obter a pessoa
    person = get_object_or_404(Person, pk=person_id)
    
    # Verificar se a pessoa está no catálogo
    if not catalog.get_filtered_people().filter(id=person_id).exists():
        raise Http404("Pessoa não encontrada neste catálogo")
    
    # Obter as fotos da galeria da pessoa
    gallery_photos = person.gallery.all().order_by('order')
    
    # Preparar dados da galeria para JSON
    gallery_photos_json = []
    for photo in gallery_photos:
        gallery_photos_json.append({
            'src': request.build_absolute_uri(photo.image.url),
            'title': photo.title or '',
            'description': photo.description or ''
        })
    
    # Registrar visualização
    if request.session.session_key is None:
        request.session.save()
    
    # Registrar visualização
    ip_address = request.META.get('REMOTE_ADDR', '')
    session_key = request.session.session_key
    
    PersonView.objects.create(
        person=person,
        catalog=catalog,
        user=request.user if request.user.is_authenticated else None,
        ip_address=ip_address,
        session_key=session_key
    )
    
    import json
    
    context = {
        'catalog': catalog,
        'person': person,
        'gallery_photos': gallery_photos,
        'gallery_photos_json': json.dumps(gallery_photos_json),
        'signature': signature,
        'is_public_view': True,
    }
    
    return render(request, 'people/public_person_gallery.html', context)
