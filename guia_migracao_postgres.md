# Guia de Migração de Dados: SQLite para PostgreSQL na VPS

Este guia descreve o processo completo para migrar os dados do seu banco SQLite local para o PostgreSQL na VPS.

## Passo 1: Transferir os Arquivos Necessários para a VPS

1. Transfira os seguintes arquivos para a VPS usando SFTP (FileZilla ou outro cliente):
   - O arquivo `data_export.zip` (contém todos os dados exportados)
   - O script `events/management/commands/migrate_to_postgres.py`

   ```
   Caminho local: c:\projetos\eventos_laize\data_export.zip
   Caminho na VPS: /home/seu_usuario/eventos_laize/data_export.zip
   
   Caminho local: c:\projetos\eventos_laize\events\management\commands\migrate_to_postgres.py
   Caminho na VPS: /home/seu_usuario/eventos_laize/events/management/commands/migrate_to_postgres.py
   ```

## Passo 2: Preparar o Ambiente na VPS

1. Conecte-se à VPS via SSH:
   ```
   ssh seu_usuario@seu_servidor
   ```

2. Navegue até o diretório do projeto:
   ```
   cd /home/seu_usuario/eventos_laize
   ```

3. Descompacte o arquivo de dados:
   ```
   unzip data_export.zip
   ```

4. Certifique-se de que a estrutura do banco de dados PostgreSQL está criada:
   ```
   python manage.py migrate
   ```

## Passo 3: Importar os Dados para o PostgreSQL

1. Execute o comando de importação:
   ```
   python manage.py migrate_to_postgres --import-only
   ```

2. Verifique se a importação foi bem-sucedida acessando o sistema e confirmando que os dados estão disponíveis.

## Passo 4: Migrar Usuários e Permissões

Como os usuários e permissões são gerenciados pelo Django Auth, precisamos transferi-los separadamente:

1. Exporte os usuários do SQLite:
   ```
   python manage.py dumpdata auth.User auth.Group auth.Permission --indent 2 > users_export.json
   ```

2. Transfira o arquivo `users_export.json` para a VPS.

3. Na VPS, importe os usuários para o PostgreSQL:
   ```
   python manage.py loaddata users_export.json
   ```

4. Verifique se os usuários foram importados corretamente:
   ```
   python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.all().values('username'))"
   ```

## Passo 5: Verificar a Integridade dos Dados

1. Verifique se todos os dados foram importados corretamente:
   ```
   python manage.py shell -c "from events.models import Event; print(Event.objects.count())"
   python manage.py shell -c "from people.models import Person; print(Person.objects.count())"
   python manage.py shell -c "from clients.models import Client; print(Client.objects.count())"
   ```

2. Verifique se os relacionamentos estão corretos:
   ```
   python manage.py shell -c "from events.models import Event; print(Event.objects.first().participants.count())"
   ```

## Passo 6: Criar um Superusuário (se necessário)

Se você precisar criar um novo superusuário no PostgreSQL:
```
python manage.py createsuperuser
```

## Passo 7: Reiniciar o Servidor Web

1. Reinicie o servidor web para aplicar todas as alterações:
   ```
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

## Solução de Problemas

### Problema: Erro de conexão com o PostgreSQL
- Verifique se o PostgreSQL está em execução: `sudo systemctl status postgresql`
- Verifique as configurações de conexão em `settings_prod.py`
- Certifique-se de que o usuário PostgreSQL tem as permissões corretas

### Problema: Erros durante a importação
- Verifique os logs para identificar o problema específico
- Pode ser necessário ajustar o script de migração para lidar com casos específicos
- Verifique se todas as tabelas foram criadas corretamente com `python manage.py showmigrations`

### Problema: Dados ausentes após a importação
- Verifique se todos os arquivos JSON foram transferidos corretamente
- Certifique-se de que a ordem de importação está respeitando as dependências entre modelos

## Observações Importantes

1. **Backup**: Sempre faça um backup do banco de dados PostgreSQL antes de importar novos dados.
2. **Ambiente de Teste**: Se possível, teste a importação em um ambiente de teste antes de aplicar no ambiente de produção.
3. **Configurações de Estilo**: As preferências de estilo (fundo claro para tabelas, listas de dados e inputs) serão mantidas, pois estão definidas nos templates e não no banco de dados.
   - Verifique se o arquivo `templates/base/base.html` contém os estilos corretos para inputs e selects com fundo claro e texto escuro.
   - Confirme que as tabelas e listas de dados (como categorias de custos, eventos, etc.) mantêm o estilo com fundo claro e texto escuro.

## Verificação Final

Após a migração, verifique os seguintes pontos para garantir que tudo está funcionando corretamente:

1. **Estilos e Aparência**:
   - Verifique se todos os inputs e selects têm fundo claro e texto escuro, mesmo no tema escuro geral do sistema.
   - Confirme que as tabelas e listas de dados mantêm o estilo com fundo claro e texto escuro para melhor legibilidade.

2. **Funcionalidades do Menu Móvel**:
   - Teste o menu móvel em dispositivos reais para garantir que ele abre e fecha corretamente.
   - Verifique se a diretiva `x-cloak` está funcionando corretamente para o menu móvel.

3. **Visualização em Dispositivos Móveis**:
   - Confirme que a visualização de eventos, pessoas e clientes está usando cards em dispositivos móveis.
   - Verifique se as áreas de toque têm tamanho adequado para interação em dispositivos móveis.

## Próximos Passos

Após a migração bem-sucedida, você pode:
1. Realizar testes abrangentes para garantir que todas as funcionalidades estão operando corretamente
2. Monitorar o desempenho do sistema com o PostgreSQL
3. Configurar backups automáticos para o PostgreSQL
4. Considerar otimizações específicas para PostgreSQL, como índices adicionais para melhorar o desempenho
