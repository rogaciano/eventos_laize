import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventos.settings')
django.setup()

# Importar o modelo após configurar o Django
from people.models_casting import CastingCatalog
from people.models import Person

# Verificar se o campo is_active existe
print('Campo is_active existe:', hasattr(CastingCatalog(), 'is_active'))

# Contar catálogos
catalogs = CastingCatalog.objects.all()
print('Total de catálogos:', catalogs.count())

# Listar catálogos e pessoas
for catalog in catalogs:
    people_count = catalog.get_filtered_people().count()
    print(f'Catálogo {catalog.id} - {catalog.name}:')
    print(f'  - Ativo: {catalog.is_active}')
    print(f'  - Pessoas: {people_count}')
    
    # Se não houver pessoas, vamos verificar os filtros
    if people_count == 0:
        print('  - Verificando filtros:')
        print(f'    - Altura: min={catalog.min_height}, max={catalog.max_height}')
        print(f'    - Peso: min={catalog.min_weight}, max={catalog.max_weight}')
        print(f'    - Idade: min={catalog.min_age}, max={catalog.max_age}')
        print(f'    - Pessoas incluídas manualmente: {catalog.included_people.count()}')
        
        # Verificar se há pessoas no sistema
        total_people = Person.objects.count()
        print(f'  - Total de pessoas no sistema: {total_people}')
