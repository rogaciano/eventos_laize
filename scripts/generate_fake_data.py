#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
import django
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventos.settings')
django.setup()

# Importar depois de configurar o ambiente
from faker import Faker
from people.models import Person, PersonContact, CorOlhos, CorCabelo, CorPele, Genero
from clients.models import Client, Contact, ClientClass

# Configurar o Faker para português do Brasil
fake = Faker('pt_BR')

# Função para gerar um CPF válido (apenas para fins de teste)
def generate_cpf():
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcular o primeiro dígito verificador
    soma = sum((cpf[i] * (10 - i)) for i in range(9))
    resto = soma % 11
    if resto < 2:
        cpf.append(0)
    else:
        cpf.append(11 - resto)
    
    # Calcular o segundo dígito verificador
    soma = sum((cpf[i] * (11 - i)) for i in range(10))
    resto = soma % 11
    if resto < 2:
        cpf.append(0)
    else:
        cpf.append(11 - resto)
    
    return ''.join(map(str, cpf))

# Função para gerar um CNPJ válido (apenas para fins de teste)
def generate_cnpj():
    cnpj = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    
    # Calcular o primeiro dígito verificador
    fatores = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(cnpj[i] * fatores[i] for i in range(12))
    resto = soma % 11
    if resto < 2:
        cnpj.append(0)
    else:
        cnpj.append(11 - resto)
    
    # Calcular o segundo dígito verificador
    fatores = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(cnpj[i] * fatores[i] for i in range(13))
    resto = soma % 11
    if resto < 2:
        cnpj.append(0)
    else:
        cnpj.append(11 - resto)
    
    return ''.join(map(str, cnpj))

def create_person_contacts(person, num_contacts=2):
    """Criar contatos para uma pessoa"""
    contact_types = ['whatsapp', 'email', 'instagram', 'outro']
    
    for _ in range(num_contacts):
        contact_type = random.choice(contact_types)
        
        if contact_type == 'whatsapp':
            value = fake.phone_number()
        elif contact_type == 'email':
            value = fake.email()
        elif contact_type == 'instagram':
            value = '@' + fake.user_name()
        else:
            value = fake.phone_number()
        
        label = random.choice(['Pessoal', 'Trabalho', 'Outro'])
        
        PersonContact.objects.create(
            person=person,
            type=contact_type,
            value=value,
            label=label
        )

def create_fake_people(num_people=20):
    """Criar pessoas fictícias"""
    # Garantir que temos dados de características físicas
    if not CorOlhos.objects.exists():
        for cor in ['Castanhos', 'Azuis', 'Verdes', 'Pretos', 'Mel']:
            CorOlhos.objects.create(nome=cor)
    
    if not CorCabelo.objects.exists():
        for cor in ['Preto', 'Castanho', 'Loiro', 'Ruivo', 'Grisalho']:
            CorCabelo.objects.create(nome=cor)
    
    if not CorPele.objects.exists():
        for cor in ['Clara', 'Média', 'Morena', 'Negra']:
            CorPele.objects.create(nome=cor)
    
    if not Genero.objects.exists():
        for genero in ['Masculino', 'Feminino', 'Não-binário']:
            Genero.objects.create(nome=genero)
    
    # Obter todas as opções de características
    cores_olhos = list(CorOlhos.objects.all())
    cores_cabelo = list(CorCabelo.objects.all())
    cores_pele = list(CorPele.objects.all())
    generos = list(Genero.objects.all())
    
    # Tamanhos de manequim comuns
    manequins = ['P', 'M', 'G', 'GG', '36', '38', '40', '42', '44', '46', '48']
    
    # Criar pessoas
    created_people = []
    for _ in range(num_people):
        # Dados básicos
        nome = fake.name()
        data_nascimento = fake.date_of_birth(minimum_age=18, maximum_age=65)
        
        # Endereço
        endereco = fake.street_name()
        numero = str(random.randint(1, 999))
        complemento = random.choice(['Apto ' + str(random.randint(1, 100)), 'Casa', 'Bloco ' + str(random.randint(1, 10)), ''])
        bairro = fake.bairro()
        cidade = fake.city()
        estado = fake.estado_sigla()
        cep = fake.postcode()
        
        # Características físicas
        altura = Decimal(str(round(random.uniform(1.50, 2.00), 2)))
        peso = Decimal(str(round(random.uniform(45.0, 100.0), 2)))
        manequim = random.choice(manequins)
        
        # Avaliações
        efficiency = random.randint(1, 5) if random.random() > 0.2 else None
        punctuality = random.randint(1, 5) if random.random() > 0.2 else None
        proactivity = random.randint(1, 5) if random.random() > 0.2 else None
        appearance = random.randint(1, 5) if random.random() > 0.2 else None
        communication = random.randint(1, 5) if random.random() > 0.2 else None
        
        # Criar a pessoa
        person = Person.objects.create(
            name=nome,
            document_id=generate_cpf(),
            data_nascimento=data_nascimento,
            address=endereco,
            address_number=numero,
            address_complement=complemento,
            neighborhood=bairro,
            city=cidade,
            state=estado,
            zipcode=cep,
            pix=fake.email() if random.random() > 0.5 else fake.phone_number(),
            notes=fake.text(max_nb_chars=200) if random.random() > 0.7 else None,
            
            # Características físicas
            altura=altura,
            peso=peso,
            manequim=manequim,
            cor_olhos=random.choice(cores_olhos),
            cor_cabelo=random.choice(cores_cabelo),
            cor_pele=random.choice(cores_pele),
            genero=random.choice(generos),
            
            # Avaliações
            efficiency=efficiency,
            punctuality=punctuality,
            proactivity=proactivity,
            appearance=appearance,
            communication=communication,
        )
        
        # Criar contatos
        create_person_contacts(person, random.randint(1, 3))
        
        created_people.append(person)
        print(f"Pessoa criada: {person.name}")
    
    return created_people

def create_client_contacts(num_contacts=2):
    """Criar contatos para clientes"""
    contacts = []
    contact_types = ['whatsapp', 'email', 'instagram', 'other']
    
    for _ in range(num_contacts):
        contact_type = random.choice(contact_types)
        
        if contact_type == 'whatsapp':
            value = fake.phone_number()
        elif contact_type == 'email':
            value = fake.email()
        elif contact_type == 'instagram':
            value = '@' + fake.user_name()
        else:
            value = fake.phone_number()
        
        label = random.choice(['Comercial', 'Financeiro', 'Suporte', 'Geral'])
        
        contact = Contact.objects.create(
            type=contact_type,
            value=value,
            label=label
        )
        
        contacts.append(contact)
    
    return contacts

def create_fake_companies(num_companies=10):
    """Criar empresas fictícias"""
    # Garantir que temos classes de clientes
    if not ClientClass.objects.exists():
        for name in ['Premium', 'Standard', 'Basic']:
            ClientClass.objects.create(
                name=name,
                description=f"Cliente {name}"
            )
    
    # Obter todas as classes de clientes
    client_classes = list(ClientClass.objects.all())
    
    # Criar empresas
    created_companies = []
    for _ in range(num_companies):
        # Dados básicos da empresa
        company_name = fake.company()
        
        # Criar a empresa
        client = Client.objects.create(
            name=company_name,
            client_class=random.choice(client_classes),
            notes=fake.text(max_nb_chars=200) if random.random() > 0.5 else None,
        )
        
        # Criar contatos
        contacts = create_client_contacts(random.randint(1, 4))
        client.contacts.set(contacts)
        
        created_companies.append(client)
        print(f"Empresa criada: {client.name}")
    
    return created_companies

if __name__ == "__main__":
    # Número de registros a serem criados
    num_people = 20
    num_companies = 10
    
    print(f"Gerando {num_people} pessoas fictícias...")
    people = create_fake_people(num_people)
    
    print(f"\nGerando {num_companies} empresas fictícias...")
    companies = create_fake_companies(num_companies)
    
    print("\nDados gerados com sucesso!")
    print(f"Total de pessoas criadas: {len(people)}")
    print(f"Total de empresas criadas: {len(companies)}")
