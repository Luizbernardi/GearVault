# Gear Vault

Sistema de Gestão de Aquisições e Estoque de Componentes Eletrônicos

## Visão Geral
O Gear Vault é uma solução completa para o gerenciamento de estoque e controle de componentes eletrônicos, voltada para empresas, laboratórios e equipes de projetos. O sistema oferece controle granular de acesso com dois perfis distintos: **Administradores** que gerenciam compras, fornecedores e produtos, e **Usuários** que consultam estoques e fazem solicitações de produtos através de um sistema estruturado de aprovação.

## Funcionalidades

### **Para Administradores**
- **Cadastro e Gerenciamento de Produtos**: Controle detalhado de componentes eletrônicos, com código, descrição, categoria, preço, fornecedor e imagem.
- **Gestão de Fornecedores**: Cadastro completo de fornecedores, incluindo CNPJ, contato e endereço com validação automática.
- **Controle de Compras**: Registro de compras, upload de invoices (PDF/imagens), cálculo automático do valor total e histórico de aquisições.
- **Gestão de Estoque Multi-localização**: Controle avançado de estoque em múltiplos locais com rastreio detalhado de quantidades por produto/local.
- **Sistema de Solicitações**: Processamento completo de solicitações com aprovação/rejeição e sistema FIFO automático.
- **Controle de Estoque Automático**: Redução automática do estoque (FIFO) quando solicitações são aprovadas.
- **Dashboard Administrativo**: Painéis completos com estatísticas de produtos, estoque, compras recentes e solicitações pendentes.
- **Gerenciamento de Usuários**: Criação, edição e controle de perfis de usuários com diferentes níveis de acesso.

### **Para Usuários**
- **Consulta de Estoque**: Visualização completa de produtos disponíveis, quantidades e locais de armazenamento com navegação paginada e filtros avançados.
- **Sistema de Solicitações**: Solicitação estruturada de produtos com validação automática de estoque e justificativa obrigatória.
- **Navegação de Estoques**: Interface intuitiva para navegar entre diferentes estoques e locais de armazenamento.
- **Histórico de Solicitações**: Acompanhamento em tempo real do status das solicitações (Pendente, Aprovada, Rejeitada) com sistema de notificações.
- **Histórico de Compras**: Acesso ao histórico completo de compras por local com informações detalhadas.
- **Dashboard Personalizado**: Painéis com estatísticas de produtos disponíveis, estoques e solicitações recentes.
- **Configuração de Perfil**: Configurações personalizadas de email SMTP para notificações automáticas do sistema.

### **Recursos Técnicos**
- **Autenticação e Autorização**: Sistema robusto de controle de acesso por perfis (ADMIN/USUARIO) com middleware personalizado.
- **Upload de Arquivos**: Suporte para upload de imagens de produtos e invoices de compras com validação automática.
- **Sistema de Notificações**: Notificações automáticas para administradores quando há novas solicitações.
- **Interface Responsiva**: Design moderno com Bootstrap 5 e Bootstrap Icons, totalmente otimizado para desktop e mobile.
- **Navegação Intuitiva**: Sistema de breadcrumbs, paginação customizável e filtros avançados.
- **Relatórios e Indicadores**: Dashboards interativos com métricas financeiras e estatísticas de estoque em tempo real.
- **Sistema FIFO**: Controle automático de estoque com algoritmo First-In-First-Out para solicitações aprovadas.
- **Validação de Dados**: Validação robusta de CNPJ, telefone, CEP e outros dados críticos.

## Tecnologias Utilizadas
- **Backend**: Python 3.13+, Django 5.1.7
- **Banco de Dados**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Frontend**: Django Templates, Bootstrap 5, Bootstrap Icons, JavaScript vanilla
- **Deployment**: Gunicorn, Fly.io, Docker, WhiteNoise
- **Outras Bibliotecas**:
  - `Pillow` - Processamento de imagens
  - `dj-database-url` - Configuração dinâmica de banco de dados
  - `psycopg2-binary` - Adaptador PostgreSQL
  - `graphviz` - Geração de diagramas de models
  - `whitenoise` - Servir arquivos estáticos em produção

## Instalação e Execução

### Pré-requisitos
- Python 3.13+ instalado
- Git instalado

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/luizbernardi/GearVault.git
   cd GearVault
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   # Atualize o pip primeiro
   python -m pip install --upgrade pip
   
   # Instale as dependências
   pip install -r requirements.txt
   ```
   
   > **Nota**: Se houver problemas com `psycopg2-binary` no Windows, execute:
   > ```bash
   > pip install --only-binary=psycopg2-binary psycopg2-binary
   > ```

4. **Configure o banco de dados:**
   ```bash
   python manage.py migrate
   ```

5. **Crie um superusuário:**
   ```bash
   python manage.py createsuperuser
   ```
   > Durante a criação, será criado automaticamente um perfil de administrador.

6. **Execute o servidor de desenvolvimento:**
   ```bash
   python manage.py runserver
   ```

7. **Acesse o sistema:**
   - Sistema: [http://localhost:8000](http://localhost:8000)
   - Admin Django: [http://localhost:8000/admin](http://localhost:8000/admin)

### Primeiro Acesso
1. Faça login com o superusuário criado
2. Você será redirecionado para o painel administrativo
3. Cadastre fornecedores, produtos e estoques
4. Crie usuários adicionais e configure seus perfis
5. Teste o sistema de solicitações entre usuários

## Deployment em Produção

### Fly.io (Recomendado)
O projeto está configurado para deploy no Fly.io com PostgreSQL:

1. **Instale o Fly CLI:**
   ```bash
   # Windows
   iwr https://fly.io/install.ps1 -useb | iex
   
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Faça login e lance a aplicação:**
   ```bash
   fly auth login
   fly launch
   ```

3. **Configure as variáveis de ambiente:**
   ```bash
   fly secrets set SECRET_KEY="sua-secret-key-aqui"
   fly secrets set DATABASE_URL="postgresql://..."
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

### Variáveis de Ambiente
- `SECRET_KEY`: Chave secreta do Django (obrigatória em produção)
- `DATABASE_URL`: URL do banco PostgreSQL (produção)
- `DEBUG`: False em produção, True em desenvolvimento
- `ALLOWED_HOSTS`: Lista de hosts permitidos separados por vírgula


## Funcionalidades Implementadas
- [x] Sistema completo de autenticação e autorização
- [x] Gestão de produtos, fornecedores e estoque multi-localização
- [x] Sistema de compras com upload de invoices
- [x] Sistema de solicitações com aprovação/rejeição
- [x] Navegação intuitiva de estoques com paginação
- [x] Histórico completo de compras por local
- [x] Dashboard administrativo e do usuário
- [x] Sistema FIFO para controle automático de estoque
- [x] Interface responsiva e moderna

## Funcionalidades Futuras
- [ ] API REST para integração com outros sistemas
- [ ] Relatórios em PDF com gráficos
- [ ] Dashboard com gráficos interativos (Chart.js)
- [ ] Sistema de notificações push/real-time
- [ ] Integração com códigos de barras/QR Code
- [ ] Histórico de movimentações detalhado com auditoria
- [ ] Backup automático de dados
- [ ] Sistema de alertas para estoque baixo
- [ ] Integração com sistemas de ERP
- [ ] Mobile app (React Native)

## Estrutura do Projeto
```
GearVault/
├── contas/                 # App de autenticação e perfis
│   ├── migrations/        # Migrações do banco de dados
│   ├── templates/         # Templates de autenticação
│   ├── __pycache__/       # Cache compilado Python
│   ├── __init__.py        # Inicializador do pacote
│   ├── admin.py           # Configuração do admin Django
│   ├── apps.py            # Configuração da aplicação
│   ├── models.py          # Profile model com roles (ADMIN/USUARIO)
│   ├── signals.py         # Sinais para criação automática de perfis
│   ├── tests.py           # Testes unitários
│   ├── urls.py            # URLs de autenticação
│   └── views.py           # Views de login, register, logout
├── core/                  # Configurações principais do projeto
│   ├── __pycache__/       # Cache compilado Python
│   ├── __init__.py        # Inicializador do pacote
│   ├── asgi.py            # Configuração ASGI
│   ├── settings.py        # Configurações Django
│   ├── urls.py            # URLs principais do projeto
│   └── wsgi.py            # Configuração WSGI para produção
├── gearvault/             # App principal do sistema de gestão
│   ├── migrations/        # Migrações do banco de dados
│   ├── templates/         # Templates do sistema
│   │   ├── components/    # Componentes reutilizáveis
│   │   └── pages/         # Páginas principais
│   │       ├── admin/     # Templates administrativos
│   │       └── user/      # Templates de usuário
│   ├── templatetags/      # Tags personalizadas do Django
│   ├── __pycache__/       # Cache compilado Python
│   ├── __init__.py        # Inicializador do pacote
│   ├── admin.py           # Configuração do admin Django
│   ├── admin_urls.py      # URLs para funcionalidades administrativas
│   ├── apps.py            # Configuração da aplicação
│   ├── email_utils.py     # Utilitários de email personalizados
│   ├── models.py          # Models principais (Produto, Estoque, etc.)
│   ├── signals.py         # Sinais para criação automática de compradores
│   ├── tests.py           # Testes unitários
│   ├── urls.py            # URLs principais da aplicação
│   ├── usuario_urls.py    # URLs para funcionalidades do usuário
│   └── views.py           # Views para admin e usuário
├── static/                # Arquivos estáticos
│   ├── assets/            # Imagens e ícones
│   └── js/                # Scripts JavaScript
├── media/                 # Uploads (produtos, invoices)
├── templates/             # Templates globais (base, sidebar)
├── venv/                  # Ambiente virtual Python
├── db.sqlite3             # Banco de dados SQLite
├── Dockerfile             # Configuração Docker
├── fly.toml               # Configuração para deploy no Fly.io
├── gerar_diagrama.py      # Script para gerar diagrama de models
├── manage.py              # Utilitário de gerenciamento Django
├── Procfile               # Definições de processo para Heroku/Fly.io
├── requirements.txt       # Dependências Python
├── requirements-local.txt # Dependências locais de desenvolvimento
└── start.sh               # Script de inicialização
```

## Models Principais
- **`Profile` (contas/models.py)**: Perfis de usuário com roles (ADMIN/USUARIO)
- **`Endereco` (gearvault/models.py)**: Endereços dos fornecedores com validação CEP
- **`Fornecedor` (gearvault/models.py)**: Dados completos dos fornecedores com CNPJ e contato
- **`Comprador` (gearvault/models.py)**: Compradores associados aos usuários do sistema
- **`Estoque` (gearvault/models.py)**: Locais principais de armazenamento
- **`LocalArmazenamento` (gearvault/models.py)**: Subdivisões específicas dos estoques
- **`Produto` (gearvault/models.py)**: Componentes eletrônicos com código, categoria e preço
- **`Compra` (gearvault/models.py)**: Registros de compras (apenas administradores)
- **`ItemCompra` (gearvault/models.py)**: Itens individuais das compras com quantidades
- **`SolicitacaoProduto` (gearvault/models.py)**: Sistema de solicitações usuário → admin

## Fluxo de Dados
1. **Requisição**: Usuário faz requisição ao sistema Django
2. **Roteamento**: `core/urls.py` direciona para URLs específicas de cada app
3. **View**: View correspondente processa a requisição e interage com models
4. **ORM/Banco**: Django ORM executa queries no banco SQLite (`db.sqlite3`)
5. **Template**: View renderiza template HTML com dados do contexto
6. **Resposta**: HTML renderizado é retornado ao usuário
  
*GearVault - Gestão Inteligente de Componentes Eletrônicos* 

---

**Desenvolvido por [Bruno Meredyk](https://github.com/Meredyk48) e [Luiz Bernardi](https://github.com/luizbernardi)** 