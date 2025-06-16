# Gear Vault

Sistema de Gestão de Aquisições e Estoque de Componentes Eletrônicos

## Visão Geral
O Gear Vault é uma solução completa para o gerenciamento de compras, estoque e controle de componentes eletrônicos, voltada para empresas, laboratórios e equipes de projetos. O sistema automatiza processos, reduz custos, padroniza operações e oferece total rastreabilidade das aquisições e movimentações de itens.

## Funcionalidades
- **Cadastro e Gerenciamento de Produtos**: Controle detalhado de componentes eletrônicos, com código, descrição, fornecedor e imagem.
- **Gestão de Fornecedores**: Cadastro completo de fornecedores, incluindo CNPJ, contato e endereço.
- **Controle de Compras**: Registro de compras, upload de invoices, cálculo automático do valor total e histórico de aquisições.
- **Estoque Multi-localização**: Controle de lotes, armazenamento em múltiplos locais e rastreio de quantidades por produto/lote/local.
- **Relatórios e Indicadores**: Visualização de totais em estoque, valor financeiro do estoque, listagem de compras, produtos e fornecedores.
- **Painéis para Usuário e Administrador**: Interfaces diferenciadas para cada perfil, com informações e ações específicas.
- **Segurança**: Autenticação, autorização e boas práticas de proteção de dados.

## Tecnologias Utilizadas
- **Backend**: Python 3, Django
- **Banco de Dados**: SQLite (desenvolvimento), compatível com PostgreSQL/MySQL
- **Frontend**: Django Templates, Bootstrap 5
- **Outros**: Django ORM, validações, upload de arquivos, imagens e invoices

## Instalação e Execução
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/gear-vault.git
   cd gear-vault
   ```
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate    # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Realize as migrações e crie um superusuário:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Execute o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```
6. Acesse o sistema em [http://localhost:8000](http://localhost:8000)

## Estrutura do Projeto
- `gearvault/` - App principal com models, views, templates e urls
- `contas/` - App de autenticação e perfis de usuário
- `static/assets/` - Imagens, ícones e arquivos estáticos
- `templates/` - Templates base e layouts

## Contribuição
Contribuições são bem-vindas! Para contribuir:
- Abra uma issue para sugestões ou problemas
- Faça um fork do projeto
- Crie uma branch para sua feature/correção
- Envie um pull request

---
Desenvolvido por [Bruno Meredyk e Luiz Bernardi]