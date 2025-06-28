#!/bin/bash

# Script de inicialização para produção
echo "Executando migrações..."
python manage.py makemigrations
python manage.py migrate

echo "Criando superusuário se não existir..."
python manage.py shell -c "
from django.contrib.auth.models import User
from contas.models import Profile
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@gearvault.com', 'admin123')
    profile, created = Profile.objects.get_or_create(user=user)
    profile.role = 'ADMIN'
    profile.save()
    print('Superusuário criado: admin/admin123')
else:
    print('Superusuário já existe')
"

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec "$@"
