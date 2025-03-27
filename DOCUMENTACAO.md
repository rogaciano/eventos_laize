# Documentação do Sistema de Gerenciamento de Eventos e Equipes

## Índice
1. [Introdução](#introdução)
2. [Acesso ao Sistema](#acesso-ao-sistema)
3. [Módulo de Eventos](#módulo-de-eventos)
4. [Módulo de Orçamentos](#módulo-de-orçamentos)
5. [Módulo de Pessoas](#módulo-de-pessoas)
6. [Módulo de Clientes](#módulo-de-clientes)
7. [Módulo de Comunicação](#módulo-de-comunicação)
8. [Site Público](#site-público)
9. [Dashboard e Relatórios](#dashboard-e-relatórios)
10. [Configurações do Sistema](#configurações-do-sistema)
11. [Perguntas Frequentes](#perguntas-frequentes)

## Introdução

O Sistema de Gerenciamento de Eventos e Equipes é uma solução completa para agências e produtoras de eventos gerenciarem todos os aspectos de seus negócios, desde o cadastro de clientes e profissionais até a geração de orçamentos e acompanhamento de eventos.

Este documento fornece instruções detalhadas sobre como utilizar cada módulo do sistema, explicando as principais funcionalidades e fluxos de trabalho.

## Acesso ao Sistema

### Requisitos de Sistema
- Navegador web atualizado (Chrome, Firefox, Edge ou Safari)
- Conexão com a internet

### Como Acessar
1. Acesse o endereço do sistema: https://agenciaatitude.com.br/sistema/
2. Informe seu nome de usuário e senha
3. Clique em "Entrar"

### Níveis de Acesso
- **Administrador**: Acesso completo a todas as funcionalidades
- **Gerente**: Acesso a gerenciamento de eventos, orçamentos, pessoas e clientes
- **Operador**: Acesso limitado a visualização e edição básica

## Módulo de Eventos

### Visão Geral
O módulo de eventos permite o cadastro, gerenciamento e acompanhamento de todos os eventos da agência.

### Funcionalidades Principais

#### Listagem de Eventos
- Acesse através do menu "Eventos" > "Listar Eventos"
- Utilize os filtros para encontrar eventos específicos (por data, cliente, status)
- Clique em um evento para visualizar seus detalhes

#### Cadastro de Novo Evento
1. Acesse "Eventos" > "Novo Evento"
2. Preencha os campos obrigatórios:
   - Título do evento
   - Cliente
   - Data e hora de início
   - Local
   - Status inicial
3. Clique em "Salvar" para criar o evento

#### Detalhes do Evento
Na tela de detalhes do evento, você pode:
- Visualizar todas as informações do evento
- Editar informações básicas
- Adicionar/remover pessoas da equipe
- Gerenciar orçamentos
- Alterar o status do evento
- Registrar ocorrências

#### Alteração de Status
1. Na tela de detalhes do evento, clique em "Alterar Status"
2. Selecione o novo status (Orçamento, Confirmado, Realizado, Cancelado)
3. Adicione um comentário explicando a alteração (opcional)
4. Clique em "Salvar"

### Fluxo de Trabalho Recomendado
1. Cadastre o evento com status "Orçamento"
2. Crie o orçamento detalhado
3. Após aprovação do cliente, altere o status para "Confirmado"
4. Atribua pessoas à equipe do evento
5. Após a realização, altere o status para "Realizado"

## Módulo de Orçamentos

### Visão Geral
O módulo de orçamentos permite criar, gerenciar e gerar PDFs de orçamentos para eventos.

### Funcionalidades Principais

#### Criação de Orçamento
1. Acesse a tela de detalhes do evento
2. Clique em "Orçamento" > "Criar Orçamento"
3. O sistema criará automaticamente um orçamento vinculado ao evento

#### Adição de Itens ao Orçamento
1. Na tela do orçamento, clique em "Adicionar Item"
2. Preencha:
   - Código do item
   - Descrição detalhada
   - Data e horário de início/fim
   - Quantidade
   - Valor unitário
3. Clique em "Salvar Item"

#### Geração de PDF
1. Na tela do orçamento, clique em "Gerar PDF"
2. O sistema gerará um PDF formatado com:
   - Logo e informações da empresa
   - Dados do cliente e evento
   - Tabela de itens com valores
   - Condições de pagamento e validade
   - Área para aceite do cliente
   - Dados bancários para pagamento

### Configurações de Orçamento
Acesse "Configurações" > "Orçamentos" para definir:
- Condições padrão de pagamento
- Validade padrão (em dias)
- Responsabilidades do cliente
- Observações adicionais
- Dados bancários

## Módulo de Pessoas

### Visão Geral
O módulo de pessoas permite gerenciar todos os profissionais que trabalham nos eventos.

### Funcionalidades Principais

#### Listagem de Pessoas
- Acesse através do menu "Pessoas" > "Listar Pessoas"
- Utilize os filtros avançados para encontrar pessoas por:
  - Nome, cidade, estado
  - Características físicas (altura, peso, cor dos olhos, etc.)
  - Categorias profissionais
  - Status (Ativo, Inativo, Pendente, Bloqueado)
  - Avaliações (eficiência, pontualidade, proatividade)

#### Cadastro de Nova Pessoa
1. Acesse "Pessoas" > "Nova Pessoa"
2. Preencha as informações pessoais
3. Adicione contatos (WhatsApp, email, etc.)
4. Selecione categorias profissionais
5. Defina o status inicial
6. Clique em "Salvar"

#### Detalhes da Pessoa
Na tela de detalhes, você pode:
- Visualizar todas as informações
- Editar dados pessoais
- Gerenciar contatos
- Atualizar avaliações
- Enviar mensagens via WhatsApp
- Gerenciar galeria de fotos
- Alterar status

#### Avaliação de Desempenho
1. Na tela de detalhes da pessoa, clique em "Avaliação"
2. Atribua notas de 1 a 5 para:
   - Eficiência
   - Pontualidade
   - Proatividade
   - Aparência
   - Comunicação
3. Clique em "Salvar Avaliação"

#### Categorias Profissionais
Para gerenciar categorias:
1. Acesse "Pessoas" > "Categorias Profissionais"
2. Visualize, adicione, edite ou remova categorias

### Cadastro Público de Pessoas
O sistema permite que novos profissionais se cadastrem através do site público:
1. Na página inicial do site, clique em "Cadastre-se em Nossa Equipe"
2. Preencha o formulário com dados pessoais e profissionais
3. Envie o cadastro
4. O sistema registrará a pessoa com status "Pendente" para aprovação

## Módulo de Clientes

### Visão Geral
O módulo de clientes permite gerenciar todos os clientes da agência.

### Funcionalidades Principais

#### Listagem de Clientes
- Acesse através do menu "Clientes" > "Listar Clientes"
- Utilize os filtros para encontrar clientes específicos

#### Cadastro de Novo Cliente
1. Acesse "Clientes" > "Novo Cliente"
2. Preencha as informações do cliente:
   - Nome/Razão Social
   - Documento (CPF/CNPJ)
   - Endereço completo
   - Classe do cliente
3. Adicione contatos
4. Clique em "Salvar"

#### Detalhes do Cliente
Na tela de detalhes, você pode:
- Visualizar todas as informações
- Editar dados do cliente
- Gerenciar contatos
- Ver histórico de eventos

## Módulo de Comunicação

### Visão Geral
O módulo de comunicação permite enviar mensagens via WhatsApp e gerenciar mensagens recebidas pelo site.

### Funcionalidades Principais

#### Envio de WhatsApp
1. Acesse a tela de detalhes da pessoa
2. Clique em "Enviar WhatsApp"
3. Digite a mensagem
4. Clique em "Enviar"

#### Histórico de Mensagens
- Visualize o histórico de mensagens enviadas
- Verifique o status de entrega

#### Mensagens do Site
1. Acesse "Landing" > "Mensagens"
2. Visualize as mensagens recebidas através do formulário de contato
3. Marque mensagens como lidas/não lidas

## Site Público

### Visão Geral
O site público (landing page) apresenta a agência para visitantes e permite interação através de formulários.

### Páginas Principais
- **Home**: Apresentação da empresa e serviços principais
- **Sobre**: História e informações sobre a agência
- **Serviços**: Detalhamento dos serviços oferecidos
- **Blog/Novidades**: Artigos e notícias
- **Contato**: Formulário para envio de mensagens
- **Cadastro**: Formulário para novos profissionais

### Gerenciamento de Conteúdo
Para atualizar o conteúdo do site:
1. Acesse "Landing" > "Configurações do Site"
2. Edite textos, imagens e informações de contato
3. Clique em "Salvar"

## Dashboard e Relatórios

### Visão Geral
O dashboard fornece uma visão geral do sistema e permite gerar relatórios.

### Funcionalidades Principais

#### Dashboard Principal
- Visualize eventos próximos
- Veja estatísticas de eventos por status
- Monitore cadastros pendentes
- Acompanhe mensagens não lidas

#### Relatórios
Para gerar relatórios:
1. Acesse "Relatórios" > selecione o tipo de relatório
2. Configure os filtros desejados
3. Clique em "Gerar Relatório"
4. Visualize na tela ou exporte para PDF

## Configurações do Sistema

### Visão Geral
As configurações permitem personalizar o comportamento do sistema.

### Principais Configurações
- **Empresa**: Dados da empresa (nome, endereço, contatos)
- **Orçamentos**: Configurações padrão para orçamentos
- **WhatsApp**: Configuração da integração com WhatsApp
- **Usuários**: Gerenciamento de usuários e permissões

## Perguntas Frequentes

### Como alterar minha senha?
1. Clique no seu nome de usuário no canto superior direito
2. Selecione "Alterar Senha"
3. Informe a senha atual e a nova senha
4. Clique em "Salvar"

### Como aprovar um cadastro pendente?
1. Acesse "Pessoas" > "Listar Pessoas"
2. Filtre por status "Pendente"
3. Clique na pessoa que deseja aprovar
4. Clique em "Alterar Status" e selecione "Ativo"
5. Clique em "Salvar"

### Como personalizar o PDF de orçamento?
1. Acesse "Configurações" > "Orçamentos"
2. Edite os campos de condições de pagamento, validade, etc.
3. Para alterar o logo, acesse "Configurações" > "Empresa"

### O que fazer se um evento for cancelado?
1. Acesse o evento
2. Clique em "Alterar Status"
3. Selecione "Cancelado"
4. Adicione um comentário explicando o motivo
5. Clique em "Salvar"

---

Para mais informações ou suporte técnico, entre em contato com a equipe de desenvolvimento através do email suporte@agenciaatitude.com.br ou pelo telefone (81) 9 9520-0103.
