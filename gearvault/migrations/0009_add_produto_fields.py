# Generated manually on 2025-07-06
# Adiciona campo categoria se não existir e garante compatibilidade

from django.db import migrations, models, connection


def check_and_add_categoria(apps, schema_editor):
    """Adiciona o campo categoria apenas se ele não existir"""
    cursor = connection.cursor()
    
    if connection.vendor == 'postgresql':
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='gearvault_produto' AND column_name='categoria';
        """)
        categoria_exists = cursor.fetchone()
    else:
        # Para SQLite
        cursor.execute("PRAGMA table_info(gearvault_produto);")
        columns = [row[1] for row in cursor.fetchall()]
        categoria_exists = 'categoria' in columns
    
    if not categoria_exists:
        if connection.vendor == 'postgresql':
            cursor.execute("ALTER TABLE gearvault_produto ADD COLUMN categoria VARCHAR(100);")
        else:
            cursor.execute("ALTER TABLE gearvault_produto ADD COLUMN categoria VARCHAR(100);")


class Migration(migrations.Migration):

    dependencies = [
        ('gearvault', '0008_solicitacaoproduto'),
    ]

    operations = [
        # Adiciona categoria apenas se não existir
        migrations.RunPython(check_and_add_categoria, migrations.RunPython.noop),
    ]
