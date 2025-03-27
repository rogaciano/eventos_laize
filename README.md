# Sistema de Gerenciamento de Eventos e Equipes

Sistema completo para gerenciamento de eventos, equipes, orçamentos e clientes desenvolvido em Django para a Agência Atitude.

## Módulos Principais

### 1. Gestão de Eventos
- Cadastro e gerenciamento completo de eventos
- Controle de status de eventos com histórico de mudanças (Orçamento, Confirmado, Realizado, Cancelado)
- Calendário visual de eventos
- Detalhamento de eventos por dia e horário
- Anexos e documentos relacionados aos eventos

### 2. Orçamentos
- Geração de orçamentos detalhados para eventos
- Itens de orçamento com código, descrição, quantidade, valor unitário e total
- Exportação de orçamentos em PDF com layout profissional
- Informações de pagamento, validade e responsabilidades
- Área para aceite do cliente com dados para assinatura

### 3. Gestão de Pessoas e Equipes
- Cadastro completo de profissionais com informações detalhadas
- Categorização por tipo de serviço/função
- Controle de status (Ativo, Inativo, Pendente, Bloqueado)
- Sistema de avaliação de desempenho (Eficiência, Pontualidade, Proatividade)
- Galeria de fotos para cada profissional
- Formulário público para cadastro de novos profissionais

### 4. Gestão de Clientes
- Cadastro e gerenciamento de clientes
- Histórico de eventos por cliente
- Classificação de clientes
- Contatos e informações detalhadas

### 5. Comunicação
- Integração com WhatsApp para comunicação com equipe
- Histórico de mensagens enviadas
- Formulário de contato no site público
- Gestão de mensagens recebidas

### 6. Site Público (Landing Page)
- Página inicial com apresentação da empresa
- Seção de serviços oferecidos
- Blog/Novidades
- Formulário de contato
- Área para cadastro de novos profissionais
- Design responsivo e moderno

### 7. Dashboard e Relatórios
- Visão geral de eventos, equipes e clientes
- Estatísticas e métricas de desempenho
- Relatórios personalizados
- Exportação de dados

## Tecnologias Utilizadas

- **Backend**: Django 5.0, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Banco de Dados**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Geração de PDF**: xhtml2pdf, ReportLab
- **Comunicação**: Integração com API WhatsApp
- **Hospedagem**: Servidor Linux com Nginx e Gunicorn

## Requisitos do Sistema

- Python 3.12+
- Django 5.0+
- Bibliotecas listadas em requirements.txt

## Instalação

1. Clone o repositório
```
git clone https://github.com/rogaciano/eventos_laize.git
cd eventos_laize
```

2. Crie um ambiente virtual e ative-o
```
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências
```
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente (copie o arquivo .env.example para .env e ajuste as configurações)

5. Execute as migrações
```
python manage.py migrate
```

6. Crie um superusuário para acessar o painel administrativo
```
python manage.py createsuperuser
```

7. Inicie o servidor de desenvolvimento
```
python manage.py runserver
```

8. Acesse o sistema em http://127.0.0.1:8000/

## Estrutura do Projeto

- **dashboard**: App para o painel administrativo e visão geral
- **events**: App para gerenciamento de eventos e orçamentos
- **people**: App para gerenciamento de pessoas e equipes
- **clients**: App para gerenciamento de clientes
- **occurrences**: App para registro de ocorrências e histórico
- **landing**: App para o site público (landing page)

## Funcionalidades Específicas

### Orçamentos
- Geração de orçamentos detalhados com itens, quantidades e valores
- Layout profissional com logo da empresa
- Seções para condições de pagamento, validade e responsabilidades
- Área para aceite do cliente
- Dados bancários para pagamento

### Gestão de Pessoas
- Cadastro detalhado com características físicas (altura, peso, cor dos olhos, etc.)
- Sistema de avaliação com notas de 1 a 5 em diferentes critérios
- Categorização por tipo de serviço
- Controle de status (ativo, inativo, pendente, bloqueado)
- Galeria de fotos para cada pessoa

### Eventos
- Detalhamento completo com data, horário, local e cliente
- Associação de pessoas/equipe ao evento
- Controle de status com histórico de mudanças
- Orçamentos vinculados aos eventos

## Manutenção e Suporte

Para reportar problemas ou solicitar novas funcionalidades, abra uma issue no repositório do GitHub ou entre em contato com a equipe de desenvolvimento.

## Licença

Este projeto é propriedade da Agência Atitude e seu uso é restrito conforme os termos acordados.
