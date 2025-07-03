# Gear Vault

Sistema de Gestão de Aquisições e Estoque de Componentes Eletrônicos

## Visão Geral
O Gear Vault é uma solução completa para o gerenciamento de estoque e controle de componentes eletrônicos, voltada para empresas, laboratórios e equipes de projetos. O sistema oferece controle granular de acesso com dois perfis distintos: **Administradores** que gerenciam compras, fornecedores e produtos, e **Usuários** que consultam estoques e fazem solicitações de produtos através de um sistema estruturado de aprovação.

## Funcionalidades

### **Para Administradores**
- **Cadastro e Gerenciamento de Produtos**: Controle detalhado de componentes eletrônicos, com código, descrição, categoria, preço, fornecedor e imagem.
- **Gestão de Fornecedores**: Cadastro completo de fornecedores, incluindo CNPJ, contato e endereço.
- **Controle de Compras**: Registro de compras, upload de invoices (PDF/imagens), cálculo automático do valor total e histórico de aquisições.
- **Gestão de Estoque Multi-localização**: Controle de estoque em múltiplos locais e rastreio de quantidades por produto/local.
- **Sistema de Solicitações**: Aprovação/rejeição de solicitações de produtos feitas pelos usuários, com histórico e notificações por email.
- **Dashboard Administrativo**: Painéis com estatísticas de produtos, estoque, compras recentes e solicitações pendentes.
- **Gerenciamento de Usuários**: Criação, edição e controle de perfis de usuários do sistema.

### **Para Usuários**
- **Consulta de Estoque**: Visualização de produtos disponíveis, quantidades e locais de armazenamento.
- **Sistema de Solicitações**: Solicitação estruturada de produtos com justificativa obrigatória.
- **Histórico de Solicitações**: Acompanhamento do status das solicitações (Pendente, Aprovada, Rejeitada).
- **Dashboard Personalizado**: Painéis com produtos disponíveis, estatísticas de estoque e solicitações recentes.
- **Configuração de Perfil**: Configurações de email SMTP para notificações do sistema.

### **Recursos Técnicos**
- **Autenticação e Autorização**: Sistema robusto de controle de acesso por perfis (ADMIN/USUARIO).
- **Upload de Arquivos**: Suporte para upload de imagens de produtos e invoices de compras.
- **Sistema de Notificações**: Emails automáticos para administradores quando há novas solicitações.
- **Interface Responsiva**: Design moderno com Bootstrap 5, otimizado para desktop e mobile.
- **Relatórios e Indicadores**: Dashboards com métricas financeiras e estatísticas de estoque.

## Tecnologias Utilizadas
- **Backend**: Python 3.13+, Django 5.1.7
- **Banco de Dados**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Frontend**: Django Templates, Bootstrap 5, Bootstrap Icons
- **Deployment**: Gunicorn, Fly.io, Docker
- **Outras Bibliotecas**:
  - `Pillow` - Processamento de imagens
  - `dj-database-url` - Configuração dinâmica de banco de dados
  - `psycopg2-binary` - Adaptador PostgreSQL
  - `graphviz` - Geração de diagramas de models

## Instalação e Execução

### Pré-requisitos
- Python 3.13+ instalado
- Git instalado

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/gear-vault.git
   cd gear-vault
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
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
4. Crie usuários adicionais conforme necessário

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
- `SECRET_KEY`: Chave secreta do Django
- `DATABASE_URL`: URL do banco PostgreSQL (produção)
- `DEBUG`: False em produção

## Funcionalidades Futuras
- [ ] API REST para integração com outros sistemas
- [ ] Relatórios em PDF
- [ ] Dashboard com gráficos interativos
- [ ] Sistema de notificações push
- [ ] Integração com códigos de barras/QR Code
- [ ] Histórico de movimentações detalhado
- [ ] Backup automático de dados

## Estrutura do Projeto
```
GearVault/
├── contas/                 # App de autenticação e perfis
│   ├── models.py          # Profile model com roles
│   ├── views.py           # Login, register, logout
│   └── templates/         # Templates de autenticação
├── core/                  # Configurações do projeto
│   ├── settings.py        # Configurações Django
│   ├── urls.py           # URLs principais
│   └── wsgi.py           # WSGI para produção
├── gearvault/             # App principal do sistema
│   ├── models.py         # Models principais (Produto, Estoque, etc.)
│   ├── views.py          # Views para admin e usuário
│   ├── admin_urls.py     # URLs para administradores
│   ├── usuario_urls.py   # URLs para usuários
│   ├── email_utils.py    # Utilitários de email
│   └── templates/        # Templates do sistema
│       ├── pages/admin/  # Templates administrativos
│       └── pages/user/   # Templates de usuário
├── static/               # Arquivos estáticos (CSS, JS, imagens)
├── media/                # Uploads (produtos, invoices)
├── templates/            # Templates globais (base, sidebar)
├── requirements.txt      # Dependências Python
├── Dockerfile           # Configuração Docker
├── fly.toml            # Configuração Fly.io
└── manage.py           # Django management
```

## Models Principais
- **`Profile`**: Perfis de usuário (ADMIN/USUARIO) com configurações SMTP
- **`Produto`**: Componentes eletrônicos com código, categoria, preço
- **`Fornecedor`**: Dados completos dos fornecedores
- **`Estoque`**: Locais de armazenamento
- **`LocalArmazenamento`**: Subdivisões dos estoques
- **`Compra`**: Registros de compras (apenas administradores)
- **`ItemCompra`**: Itens individuais das compras
- **`SolicitacaoProduto`**: Sistema de solicitações usuário → admin
  
*GearVault - Gestão Inteligente de Componentes Eletrônicos* 

---

**Desenvolvido por [Bruno Meredyk](https://github.com/Meredyk48) e [Luiz Bernardi](https://github.com/luizbernardi)** 