from django.db import models
from django.conf import settings
import os

class CompanySettings(models.Model):
    """Configurações da empresa para uso em documentos"""
    name = models.CharField(max_length=100, verbose_name='Nome da Empresa')
    address = models.CharField(max_length=255, verbose_name='Endereço')
    phone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(verbose_name='E-mail')
    cnpj = models.CharField(max_length=20, verbose_name='CNPJ')
    logo = models.ImageField(upload_to='company/', verbose_name='Logo', null=True, blank=True)
    signature_name = models.CharField(max_length=100, verbose_name='Nome para Assinatura', 
                                     help_text='Nome que aparecerá nas assinaturas de documentos')
    signature_title = models.CharField(max_length=100, verbose_name='Cargo/Título', 
                                     help_text='Cargo ou título que aparecerá abaixo do nome nas assinaturas')
    
    class Meta:
        verbose_name = 'Configuração da Empresa'
        verbose_name_plural = 'Configurações da Empresa'
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_default(cls):
        """Retorna as configurações da empresa ou cria um padrão se não existir"""
        from django.core.files.images import ImageFile
        import os
        from django.conf import settings
        
        settings_obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'name': 'Agência Laize Eventos',
                'address': 'Rua Tiradentes, 123 - Boa Vista 2 - CEP: 55.038-550',
                'phone': '(81) 9 9520-0103',
                'email': 'agencialaize.eventos@gmail.com',
                'cnpj': '13.050.039/1000-35',
                'signature_name': 'Laize Alves Azevedo Monteiro',
                'signature_title': 'Agência Laize Eventos'
            }
        )
        
        # Se a configuração foi criada agora ou se não tem logo, adiciona a logo padrão
        if created or not settings_obj.logo:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'brand', 'logo_orcamento.jpg')
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    settings_obj.logo.save('logo_orcamento.jpg', ImageFile(f), save=True)
        
        return settings_obj
    
    def logo_url(self):
        """Retorna a URL da logo ou None se não existir"""
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return None
