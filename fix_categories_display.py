#!/usr/bin/env python
"""
Script para verificar e corrigir a exibição das categorias profissionais.
Este script pode ser executado tanto no ambiente de desenvolvimento quanto na VPS.
"""

import os
import sys
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventos.settings')
django.setup()

from people.models import Person, ProfessionalCategory
from django.core.management import call_command

def main():
    print("Verificando e corrigindo a exibição das categorias profissionais...")
    
    # Verificar se existem categorias profissionais
    categories = ProfessionalCategory.objects.all()
    print(f"Total de categorias profissionais: {categories.count()}")
    for category in categories:
        print(f" - {category.nome} (ID: {category.id})")
    
    # Verificar pessoas com categorias
    people_with_categories = Person.objects.filter(professional_categories__isnull=False).distinct()
    print(f"\nTotal de pessoas com categorias atribuídas: {people_with_categories.count()}")
    
    for person in people_with_categories:
        categories = person.professional_categories.all()
        print(f" - {person.name}: {', '.join([c.nome for c in categories])}")
    
    # Limpar o cache do template
    print("\nLimpando o cache do template...")
    try:
        call_command('clear_cache')
        print("Cache limpo com sucesso.")
    except:
        print("Não foi possível limpar o cache automaticamente.")
        print("Recomendação: Reinicie o servidor Django na VPS.")
    
    print("\nPara garantir que as alterações sejam aplicadas na VPS, execute os seguintes comandos:")
    print("1. Acesse o servidor via SSH")
    print("2. Navegue até o diretório do projeto")
    print("3. Execute: python manage.py clear_cache (se disponível)")
    print("4. Reinicie o servidor Django (dependendo da configuração, pode ser um dos comandos abaixo):")
    print("   - systemctl restart gunicorn")
    print("   - supervisorctl restart eventos_laize")
    print("   - touch eventos_laize/wsgi.py (se estiver usando mod_wsgi)")

if __name__ == "__main__":
    main()
