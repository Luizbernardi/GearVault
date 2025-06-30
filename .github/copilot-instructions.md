# GitHub Copilot Project Configuration - GearVault

## Technology Stack
- **Backend:** Python (Django 5.1.7)
- **Database:** SQLite (db.sqlite3)
- **Frontend:** Django Templates, HTML, CSS, JavaScript
- **ORM/Data Access:** Django ORM
- **Deployment:** Gunicorn, Fly.io

## Folder Structure
```
GearVault/
  contas/             # Application for user accounts (login, register, profile)
    migrations/       # Database migrations for 'contas' app
    templates/        # HTML templates for 'contas' app
    __init__.py
    admin.py
    apps.py
    models.py         # User Profile model
    signals.py
    tests.py
    urls.py
    views.py
  core/               # Main project configuration
    __init__.py
    asgi.py
    settings.py       # Django project settings
    urls.py           # Main URL routing
    wsgi.py
  diagrama_models/    # Directory for model diagrams
  docs/               # Project documentation (if any)
  gearvault/          # Main application for inventory management
    migrations/       # Database migrations for 'gearvault' app
    templates/        # HTML templates for 'gearvault' app
    __init__.py
    admin.py
    admin_urls.py     # URL routing for admin functionalities
    apps.py
    models.py         # Core models (Endereco, Fornecedor, Comprador, Estoque, LocalArmazenamento, Produto, Compra, ItemCompra, SolicitacaoProduto)
    tests.py
    urls.py
    usuario_urls.py   # URL routing for user functionalities
    views.py
  media/              # Uploaded media files (e.g., product images, invoices)
  static/             # Static files (CSS, JS, images)
  templates/          # Global project templates
  venv/               # Python virtual environment
  Dockerfile          # Docker configuration for deployment
  Procfile            # Process definitions for Heroku/Fly.io
  README.md           # Project README
  db.sqlite3          # SQLite database file
  fly.toml            # Fly.io deployment configuration
  gerar_diagrama.py   # Script to generate model diagrams
  manage.py           # Django management utility
  requirements.txt    # Python dependencies
  start.sh            # Startup script for the application
  test_email_system.py # Script to test email system
```

## Standards and Best Practices
- **Django Apps:** Project is structured into reusable Django applications (`contas`, `gearvault`).
- **Models:** Models define the database schema and relationships.
- **Views:** Views handle request/response logic and render templates.
- **Templates:** HTML templates are used for rendering dynamic content.
- **Static Files:** Static assets (CSS, JS, images) are served from the `static/` directory.
- **Media Files:** User-uploaded content is stored in the `media/` directory.
- **Authentication:** Django's built-in authentication system is used, extended with a `Profile` model for user roles.
- **URL Routing:** URLs are organized by application and user/admin roles.

## Code Conventions
- **Python:** Follows PEP 8 guidelines.
- **Django:** Adheres to Django's conventions for models, views, templates, and URLs.
- **Model Fields:** Use appropriate Django model field types and validators.
- **Function Naming:** Use `snake_case` for function and variable names.
- **Class Naming:** Use `PascalCase` for class names.

## Data Flow
1.  **Request:** A user request comes to the Django application.
2.  **URL Routing:** `core/urls.py` dispatches the request to the appropriate app's `urls.py` (e.g., `gearvault/usuario_urls.py`).
3.  **View:** The corresponding view function (e.g., `gearvault/views.py` or `contas/views.py`) processes the request.
4.  **Model/ORM:** The view interacts with Django Models (defined in `models.py` of each app) via the Django ORM to query or modify data in the SQLite database.
5.  **Template:** The view renders an HTML template (from `templates/` directories) with context data.
6.  **Response:** The rendered HTML is sent back to the user.

## Specific Framework/Library Details
- **Django:** A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **Django ORM:** Used for database interactions, abstracting SQL queries.
- **Django Admin:** Provides an automatic admin interface for managing models.
- **Gunicorn:** A Python WSGI HTTP Server for UNIX, used for deploying the Django application.
- **Pillow:** Python Imaging Library (PIL) fork, used for image processing (e.g., product images).
- **Graphviz:** Used for generating visual representations of Django models.

## Documentation
- Refer to `README.md` for project setup and general information.
- Model definitions and relationships can be found in `contas/models.py` and `gearvault/models.py`.
- URL structures are defined in `core/urls.py`, `contas/urls.py`, `gearvault/usuario_urls.py`, and `gearvault/admin_urls.py`.
- Deployment configurations are in `Dockerfile`, `Procfile`, `fly.toml`, and `start.sh`.