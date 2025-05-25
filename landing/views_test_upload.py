from django.shortcuts import render
from django.conf import settings
from people.models import Person
from django.http import HttpResponse
import logging
import os

logger = logging.getLogger(__name__)

def test_upload(request):
    """View para testar o upload de fotos sem outras funcionalidades"""
    upload_success = False
    upload_error = None
    uploaded_file_path = None
    
    if request.method == 'POST' and request.FILES:
        try:
            # Obter o arquivo enviado
            photo = request.FILES.get('photo')
            
            if photo:
                # Verificar se o diretório de destino existe
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'people_photos')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                # Salvar o arquivo diretamente
                file_path = os.path.join(upload_dir, photo.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in photo.chunks():
                        destination.write(chunk)
                
                # Registrar sucesso
                upload_success = True
                uploaded_file_path = os.path.join('people_photos', photo.name)
                logger.info(f"Arquivo enviado com sucesso: {file_path}")
            else:
                upload_error = "Nenhum arquivo foi enviado."
                logger.warning("Tentativa de upload sem arquivo")
        
        except Exception as e:
            upload_error = f"Erro ao processar o upload: {str(e)}"
            logger.error(f"Erro no upload de arquivo: {e}")
    
    context = {
        'upload_success': upload_success,
        'upload_error': upload_error,
        'uploaded_file_path': uploaded_file_path,
        'media_url': settings.MEDIA_URL
    }
    
    return render(request, 'landing/test_upload.html', context)
