# Guia do Desenvolvedor - Sistema de Gerenciamento de Eventos

Este guia fornece informações técnicas sobre a estrutura do projeto, padrões de código e fluxos de desenvolvimento para facilitar a manutenção e expansão do sistema.

## Estrutura do Projeto

### Apps Django

- **dashboard**: Painel administrativo e visão geral do sistema
- **events**: Gerenciamento de eventos e orçamentos
- **people**: Gerenciamento de pessoas e equipes
- **clients**: Gerenciamento de clientes
- **occurrences**: Registro de ocorrências e histórico
- **landing**: Site público (landing page)
- **eventos**: App principal com configurações do projeto

### Modelos Principais

#### Events
```python
# events/models.py
class Event(models.Model):
    title = models.CharField(max_length=200)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES)
    # Outros campos...

# events/models_budget.py
class Budget(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField()
    # Outros campos...

class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    description = models.TextField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Outros campos...
```

#### People
```python
# people/models.py
class Person(models.Model):
    name = models.CharField(max_length=200)
    document = models.CharField(max_length=20)
    birth_date = models.DateField()
    status = models.CharField(max_length=20, choices=PERSON_STATUS_CHOICES)
    # Campos de características físicas
    # Campos de avaliação
    categories = models.ManyToManyField(ProfessionalCategory)
    # Outros campos...

class ProfessionalCategory(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    # Outros campos...
```

#### Clients
```python
# clients/models.py
class Client(models.Model):
    name = models.CharField(max_length=200)
    document = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    # Outros campos...
```

## Fluxos de Desenvolvimento

### Criação de Novas Funcionalidades

1. **Planejamento**:
   - Defina os requisitos da funcionalidade
   - Identifique os modelos e views afetados
   - Crie um branch específico para a funcionalidade

2. **Implementação**:
   - Atualize/crie modelos necessários
   - Implemente as views e templates
   - Adicione testes unitários

3. **Revisão e Merge**:
   - Faça uma revisão do código
   - Execute todos os testes
   - Faça o merge com a branch principal

### Padrões de Código

#### Convenções de Nomenclatura

- **Modelos**: Nomes em singular, CamelCase (ex: `Person`, `Event`)
- **Apps**: Nomes em plural, snake_case (ex: `events`, `people`)
- **Views**: Nomes descritivos, snake_case (ex: `event_detail`, `person_list`)
- **URLs**: Nomes descritivos, kebab-case (ex: `event-detail`, `person-list`)

#### Estrutura de Views

Utilize Class-Based Views quando possível:

```python
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        # Personalize a consulta conforme necessário
        return Event.objects.filter(status='active').order_by('-start_date')
```

Para views mais simples, use Function-Based Views:

```python
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})
```

## Geração de PDF

O sistema utiliza `xhtml2pdf` para gerar PDFs a partir de templates HTML:

```python
def generate_budget_pdf(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id)
    
    # Contexto para o template
    context = {
        'budget': budget,
        'items': budget.budgetitem_set.all(),
        'settings': DefaultBudgetSettings.objects.first(),
    }
    
    # Renderiza o template HTML
    template = get_template('events/event_budget_pdf.html')
    html = template.render(context)
    
    # Cria o PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{budget.id}.pdf"'
        return response
    
    return HttpResponse('Erro ao gerar PDF', status=400)
```

## Autenticação e Autorização

O sistema utiliza o sistema de autenticação do Django com um middleware personalizado para controlar o acesso:

```python
# eventos/middleware.py
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = [
            reverse('login'),
            reverse('logout'),
            reverse('landing:home'),
            reverse('landing:register'),
            # Outras URLs públicas...
        ]
    
    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            if not any(url == path for url in self.public_urls) and not path.startswith('/static/'):
                return redirect('login')
        
        return self.get_response(request)
```

## Integração com WhatsApp

O sistema utiliza a API do WhatsApp para enviar mensagens:

```python
def send_whatsapp_message(phone, message):
    # Configuração da API
    api_key = settings.WHATSAPP_API_KEY
    url = settings.WHATSAPP_API_URL
    
    # Preparação dos dados
    data = {
        'phone': phone,
        'message': message,
    }
    
    # Envio da requisição
    response = requests.post(url, json=data, headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    })
    
    return response.status_code == 200
```

## Formulário de Cadastro Público

O formulário de cadastro público permite que novos profissionais se cadastrem sem autenticação:

```python
# landing/views.py
def register(request):
    if request.method == 'POST':
        form = PersonRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            person = form.save(commit=False)
            person.status = 'pending'  # Status inicial: pendente de aprovação
            person.save()
            form.save_m2m()  # Salva as relações ManyToMany
            
            # Notifica administradores sobre o novo cadastro
            notify_admins_about_new_registration(person)
            
            return render(request, 'landing/register_success.html')
    else:
        form = PersonRegistrationForm()
    
    return render(request, 'landing/register.html', {'form': form})
```

## Controle de Status

O sistema utiliza um padrão de controle de status para eventos e pessoas:

```python
# events/models.py
EVENT_STATUS_CHOICES = [
    ('budget', 'Orçamento'),
    ('confirmed', 'Confirmado'),
    ('completed', 'Realizado'),
    ('canceled', 'Cancelado'),
]

# people/models.py
PERSON_STATUS_CHOICES = [
    ('active', 'Ativo'),
    ('inactive', 'Inativo'),
    ('pending', 'Pendente'),
    ('blocked', 'Bloqueado'),
]
```

## Migrações de Banco de Dados

Para criar e aplicar migrações:

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar migrações para um app específico
python manage.py makemigrations app_name

# Verificar status das migrações
python manage.py showmigrations
```

## Testes

O sistema utiliza o framework de testes do Django:

```python
# events/tests.py
class EventModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(name='Test Client')
        self.event = Event.objects.create(
            title='Test Event',
            client=self.client,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(hours=2),
            location='Test Location',
            status='budget'
        )
    
    def test_event_creation(self):
        self.assertEqual(self.event.title, 'Test Event')
        self.assertEqual(self.event.status, 'budget')
```

Para executar os testes:

```bash
# Executar todos os testes
python manage.py test

# Executar testes de um app específico
python manage.py test app_name

# Executar um teste específico
python manage.py test app_name.tests.TestClass.test_method
```

## Configuração de Ambiente

O projeto utiliza variáveis de ambiente para configurações sensíveis:

```python
# eventos/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Configurações de banco de dados
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}
```

Crie um arquivo `.env` na raiz do projeto com as configurações necessárias.

## Deployment

O sistema está configurado para deployment em um servidor Linux com Nginx e Gunicorn:

```bash
# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic

# Aplicar migrações
python manage.py migrate

# Iniciar o Gunicorn
gunicorn eventos.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
```

Configuração do Nginx:

```nginx
server {
    listen 80;
    server_name agenciaatitude.com.br www.agenciaatitude.com.br;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/agenciaatitude;
    }
    
    location /media/ {
        root /var/www/agenciaatitude;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://localhost:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

## Contribuição

Para contribuir com o projeto:

1. Clone o repositório
2. Crie um branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça suas alterações
4. Execute os testes
5. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
6. Push para o branch (`git push origin feature/nova-funcionalidade`)
7. Crie um Pull Request

## Recursos Adicionais

- [Documentação do Django](https://docs.djangoproject.com/)
- [Documentação do xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf)
- [Tailwind CSS](https://tailwindcss.com/docs)
