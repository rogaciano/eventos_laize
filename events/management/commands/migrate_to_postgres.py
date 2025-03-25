import os
import sys
import json
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connections
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import ForeignKey, ManyToManyField
from django.db.models.fields.files import FieldFile


class CustomJSONEncoder(DjangoJSONEncoder):
    """Encoder personalizado para lidar com tipos que o Django não serializa por padrão"""
    def default(self, obj):
        # Lidar com objetos de modelo
        if hasattr(obj, '_meta'):
            return str(obj)
        # Lidar com arquivos de campo
        if isinstance(obj, FieldFile):
            if obj:
                return obj.name
            return None
        # Deixar o encoder padrão do Django lidar com outros tipos
        return super().default(obj)


class Command(BaseCommand):
    help = 'Migra dados do SQLite para PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--export-only',
            action='store_true',
            help='Apenas exporta os dados para JSON, sem importar para PostgreSQL',
        )
        parser.add_argument(
            '--import-only',
            action='store_true',
            help='Apenas importa os dados de JSON para PostgreSQL',
        )
        parser.add_argument(
            '--export-path',
            type=str,
            default='data_export',
            help='Caminho para exportar/importar os arquivos JSON',
        )

    def handle(self, *args, **options):
        export_only = options['export_only']
        import_only = options['import_only']
        export_path = options['export_path']

        # Criar diretório de exportação se não existir
        if not os.path.exists(export_path):
            os.makedirs(export_path)

        # Obter todas as aplicações e modelos
        all_models = []
        for app_config in apps.get_app_configs():
            # Ignorar apps do Django e outros que não queremos migrar
            if app_config.name.startswith('django.') or app_config.name in ['contenttypes', 'admin', 'sessions', 'messages']:
                continue
            for model in app_config.get_models():
                all_models.append(model)

        # Ordenar modelos para garantir que dependências sejam respeitadas
        models_order = self.sort_models_by_dependencies(all_models)

        if not import_only:
            self.stdout.write(self.style.SUCCESS('Exportando dados do SQLite...'))
            self.export_data(models_order, export_path)

        if not export_only:
            self.stdout.write(self.style.SUCCESS('Importando dados para PostgreSQL...'))
            self.import_data(models_order, export_path)

        self.stdout.write(self.style.SUCCESS('Migração concluída com sucesso!'))

    def sort_models_by_dependencies(self, models):
        """Ordena os modelos para garantir que dependências sejam respeitadas"""
        models_with_deps = {}
        
        # Coletar dependências
        for model in models:
            deps = []
            for field in model._meta.fields:
                if isinstance(field, ForeignKey):
                    deps.append(field.remote_field.model)
            
            # Adicionar dependências de ManyToMany também
            for field in model._meta.many_to_many:
                deps.append(field.remote_field.model)
                
            models_with_deps[model] = deps
        
        # Ordenar
        result = []
        visited = set()
        
        def visit(model):
            if model in visited:
                return
            visited.add(model)
            for dep in models_with_deps.get(model, []):
                if dep in models_with_deps:  # Apenas visitar modelos que estamos migrando
                    visit(dep)
            result.append(model)
        
        for model in models_with_deps:
            visit(model)
        
        return result

    def export_data(self, models, export_path):
        """Exporta dados de todos os modelos para arquivos JSON"""
        for model in models:
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            self.stdout.write(f"Exportando {model_name}...")
            
            # Obter todos os objetos do modelo
            objects = model.objects.all()
            
            # Converter objetos para dicionários
            data = []
            for obj in objects:
                obj_dict = {}
                for field in model._meta.fields:
                    field_name = field.name
                    field_value = getattr(obj, field_name)
                    
                    # Para campos FK, armazenar apenas o ID
                    if isinstance(field, ForeignKey) and field_value is not None:
                        obj_dict[field_name + '_id'] = field_value.pk
                    else:
                        # Converter valores especiais
                        if field_value is not None:
                            obj_dict[field_name] = field_value
                
                # Adicionar campos ManyToMany
                for field in model._meta.many_to_many:
                    field_name = field.name
                    m2m_values = getattr(obj, field_name).values_list('pk', flat=True)
                    if m2m_values:
                        obj_dict[field_name + '_ids'] = list(m2m_values)
                
                data.append(obj_dict)
            
            # Salvar em arquivo JSON
            file_path = os.path.join(export_path, f"{model_name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, cls=CustomJSONEncoder, ensure_ascii=False, indent=4)
            
            self.stdout.write(self.style.SUCCESS(f"  Exportados {len(data)} registros para {file_path}"))

    def import_data(self, models, export_path):
        """Importa dados de arquivos JSON para o PostgreSQL"""
        # Verificar conexão com PostgreSQL
        try:
            connection = connections['postgres']
            connection.cursor()
            self.stdout.write(self.style.SUCCESS("Conexão com PostgreSQL estabelecida com sucesso!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao conectar ao PostgreSQL: {str(e)}"))
            return
        
        # Importar dados na ordem correta
        for model in models:
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            file_path = os.path.join(export_path, f"{model_name}.json")
            
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f"Arquivo {file_path} não encontrado. Pulando..."))
                continue
            
            self.stdout.write(f"Importando {model_name}...")
            
            # Carregar dados do arquivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Limpar tabela antes de importar
            model.objects.using('postgres').all().delete()
            
            # Importar objetos
            imported_count = 0
            m2m_data = []  # Armazenar dados M2M para importar depois
            
            for obj_dict in data:
                # Separar campos M2M
                m2m_fields = {}
                fields_dict = {}
                
                for field_name, field_value in obj_dict.items():
                    # Verificar se é um campo M2M (termina com _ids)
                    if field_name.endswith('_ids'):
                        original_field_name = field_name[:-4]  # Remover _ids
                        if original_field_name in [f.name for f in model._meta.many_to_many]:
                            m2m_fields[original_field_name] = field_value
                    else:
                        fields_dict[field_name] = field_value
                
                # Criar objeto
                try:
                    obj = model.objects.using('postgres').create(**fields_dict)
                    
                    # Armazenar dados M2M para importar depois
                    if m2m_fields:
                        m2m_data.append((obj, m2m_fields))
                    
                    imported_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Erro ao importar registro: {str(e)}"))
                    self.stdout.write(self.style.ERROR(f"  Dados: {fields_dict}"))
            
            # Importar dados M2M
            for obj, m2m_fields in m2m_data:
                for field_name, values in m2m_fields.items():
                    try:
                        m2m_field = getattr(obj, field_name)
                        # Verificar se todos os IDs existem antes de tentar definir
                        model_to_check = model._meta.get_field(field_name).remote_field.model
                        existing_ids = set(model_to_check.objects.using('postgres').filter(pk__in=values).values_list('pk', flat=True))
                        missing_ids = set(values) - existing_ids
                        
                        if missing_ids:
                            self.stdout.write(self.style.WARNING(
                                f"  Aviso: IDs {missing_ids} não encontrados para o campo {field_name} do modelo {model_name}"
                            ))
                            # Usar apenas IDs existentes
                            m2m_field.set(existing_ids)
                        else:
                            m2m_field.set(values)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Erro ao definir relação M2M {field_name}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"  Importados {imported_count} registros para {model_name}"))
