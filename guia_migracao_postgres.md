# Guia de Migração para PostgreSQL

Este guia descreve o processo para migrar o banco de dados do SQLite para o PostgreSQL no sistema de eventos.

## Passo 1: Preparar o Ambiente Local

1. Instale o pacote psycopg2 (adaptador PostgreSQL para Python):
   ```
   pip install psycopg2
   ```

2. Verifique se o PostgreSQL está instalado e funcionando no seu ambiente local.

3. Certifique-se de que o arquivo `settings.py` está configurado com os dois bancos de dados:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       },
       'postgres': {
           'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'NAME': 'agenciaatitude',
           'USER': 'agenciaatitude',
           'PASSWORD': '*Marien2012',
           'HOST': 'localhost',
           'PORT': '',
       }
   }
   ```

## Passo 2: Executar a Migração em Duas Etapas

### Etapa 1: Exportar Dados do SQLite para JSON

Execute o comando de exportação para gerar os arquivos JSON:

```
python manage.py migrate_to_postgres --export-only --export-path=data_export
```

Este comando irá:
1. Criar um diretório `data_export` (se não existir)
2. Exportar todos os dados do SQLite para arquivos JSON nesse diretório
3. Cada modelo terá seu próprio arquivo JSON (ex: `events.event.json`)

### Etapa 2: Importar Dados do JSON para PostgreSQL

Execute o comando de importação para carregar os dados no PostgreSQL:

```
python manage.py migrate_to_postgres --import-only --export-path=data_export
```

Este comando irá:
1. Ler os arquivos JSON do diretório `data_export`
2. Importar os dados para o PostgreSQL na ordem correta
3. Tratar adequadamente as relações ManyToMany e chaves estrangeiras

## Passo 3: Verificar a Migração

Após a migração, verifique se todos os dados foram transferidos corretamente:

1. Acesse o sistema usando o banco PostgreSQL:
   ```python
   # No shell do Django
   python manage.py shell
   
   # Dentro do shell
   from django.db import connections
   connections.databases['default'] = connections.databases['postgres']
   
   # Agora você pode consultar os modelos normalmente
   from events.models import Event
   Event.objects.count()  # Deve mostrar o mesmo número de registros que no SQLite
   ```

2. Verifique especialmente os modelos com relações ManyToMany para garantir que todas as relações foram preservadas.

## Passo 4: Transferir para o Servidor

1. Copie o script de migração para o servidor:
   ```
   scp events/management/commands/migrate_to_postgres.py usuario@servidor:/caminho/para/projeto/events/management/commands/
   ```

2. No servidor, crie um backup do banco SQLite atual:
   ```
   cp db.sqlite3 db.sqlite3.backup
   ```

3. Limpe os dados de teste do banco SQLite (opcional, se necessário):
   ```
   python manage.py flush
   ```

4. Atualize o arquivo `settings.py` no servidor para incluir a configuração do PostgreSQL:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       },
       'postgres': {
           'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'NAME': 'agenciaatitude',
           'USER': 'agenciaatitude',
           'PASSWORD': '*Marien2012',
           'HOST': 'localhost',
           'PORT': '',
       }
   }
   ```

5. Execute a migração em duas etapas como descrito anteriormente:
   ```
   python manage.py migrate_to_postgres --export-only --export-path=data_export
   python manage.py migrate_to_postgres --import-only --export-path=data_export
   ```

## Passo 5: Atualizar a Configuração para Usar Apenas PostgreSQL

1. Após confirmar que a migração foi bem-sucedida, atualize o arquivo `settings.py` para usar apenas o PostgreSQL:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'NAME': 'agenciaatitude',
           'USER': 'agenciaatitude',
           'PASSWORD': '*Marien2012',
           'HOST': 'localhost',
           'PORT': '',
       }
   }
   ```

2. Reinicie o servidor Gunicorn:
   ```
   systemctl restart gunicorn_agenciaatitude
   ```

## Solução de Problemas

### Problema: Erro de Foreign Key Constraint

Se você encontrar erros de restrição de chave estrangeira durante a importação, isso geralmente ocorre porque os modelos estão sendo importados em uma ordem que não respeita as dependências. O script foi projetado para evitar isso, mas se ocorrer:

1. Verifique se todos os modelos relacionados foram migrados corretamente
2. Tente executar novamente o comando de importação

### Problema: Dados Ausentes

Se você notar que alguns dados estão ausentes após a migração:

1. Verifique os arquivos JSON exportados para confirmar se os dados foram exportados corretamente
2. Verifique se há erros nos logs durante a importação
3. Para modelos específicos, você pode tentar migrar manualmente:
   ```
   python manage.py migrate_to_postgres --export-only --export-path=data_export_specific
   # Edite os arquivos JSON conforme necessário
   python manage.py migrate_to_postgres --import-only --export-path=data_export_specific
   ```

### Problema: Erros de Conexão

Se você encontrar erros de conexão com o PostgreSQL:

1. Verifique se o PostgreSQL está em execução:
   ```
   systemctl status postgresql
   ```

2. Verifique se as credenciais estão corretas no arquivo `settings.py`

3. Verifique se o usuário do PostgreSQL tem permissões adequadas:
   ```
   sudo -u postgres psql
   postgres=# ALTER USER agenciaatitude WITH SUPERUSER;
   postgres=# \q
   ```
