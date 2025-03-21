# Gerenciador de Eventos

Sistema de gerenciamento de eventos desenvolvido em Django para controle de eventos, participantes, clientes e relatórios.

## Funcionalidades

- Cadastro e gerenciamento de eventos
- Controle de status de eventos com histórico de mudanças
- Cadastro de clientes e participantes
- Gerenciamento de funções e valores
- Relatórios e listagens

## Tecnologias Utilizadas

- Django 5.0
- Python 3.12
- Tailwind CSS
- FontAwesome
- SQLite (banco de dados)

## Instalação

1. Clone o repositório
```
git clone https://github.com/seu-usuario/gerenciador-eventos.git
cd gerenciador-eventos
```

2. Crie um ambiente virtual e ative-o
```
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências
```
pip install -r requirements.txt
```

4. Execute as migrações
```
python manage.py migrate
```

5. Inicie o servidor de desenvolvimento
```
python manage.py runserver
```

6. Acesse o sistema em http://127.0.0.1:8000/

## Estrutura do Projeto

- **events**: Aplicativo para gerenciamento de eventos e participantes
- **people**: Aplicativo para gerenciamento de pessoas/participantes
- **clients**: Aplicativo para gerenciamento de clientes
- **templates**: Templates HTML do sistema
- **static**: Arquivos estáticos (CSS, JS, imagens)

## Licença

Este projeto está licenciado sob a licença MIT.
