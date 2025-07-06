# Generated manually on 2025-07-06
# Transição de fornecedor único para fornecedores muitos-para-muitos

from django.db import migrations, models, connection


def check_and_add_fornecedores_field(apps, schema_editor):
    """Adiciona o campo fornecedores apenas se não existir"""
    cursor = connection.cursor()
    
    # Verifica se a tabela intermediária já existe
    if connection.vendor == 'postgresql':
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name='gearvault_produto_fornecedores';
        """)
        table_exists = cursor.fetchone()
    else:
        # Para SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gearvault_produto_fornecedores';")
        table_exists = cursor.fetchone()
    
    if table_exists:
        print("Tabela gearvault_produto_fornecedores já existe, pulando criação...")
        return True
    return False


def migrate_fornecedor_data(apps, schema_editor):
    """Migra dados do campo fornecedor único para o campo fornecedores ManyToMany"""
    cursor = connection.cursor()
    
    # Verifica se o campo fornecedor_id ainda existe
    if connection.vendor == 'postgresql':
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='gearvault_produto' AND column_name='fornecedor_id';
        """)
        fornecedor_exists = cursor.fetchone()
    else:
        # Para SQLite
        cursor.execute("PRAGMA table_info(gearvault_produto);")
        columns = [row[1] for row in cursor.fetchall()]
        fornecedor_exists = 'fornecedor_id' in columns
    
    if fornecedor_exists:
        print("Migrando dados de fornecedor único para fornecedores múltiplos...")
        # Busca todos os produtos com fornecedor definido usando SQL direto
        cursor.execute("SELECT id, fornecedor_id FROM gearvault_produto WHERE fornecedor_id IS NOT NULL;")
        produtos_com_fornecedor = cursor.fetchall()
        
        for produto_id, fornecedor_id in produtos_com_fornecedor:
            # Adiciona a relação na tabela intermediária
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    INSERT INTO gearvault_produto_fornecedores (produto_id, fornecedor_id) 
                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """, [produto_id, fornecedor_id])
            else:
                cursor.execute("""
                    INSERT OR IGNORE INTO gearvault_produto_fornecedores (produto_id, fornecedor_id) 
                    VALUES (?, ?);
                """, [produto_id, fornecedor_id])
        
        print(f"Migrados {len(produtos_com_fornecedor)} produtos com fornecedores.")


def reverse_migrate_fornecedor_data(apps, schema_editor):
    """Operação reversa - seleciona o primeiro fornecedor como fornecedor único"""
    Produto = apps.get_model('gearvault', 'Produto')
    
    for produto in Produto.objects.all():
        primeiro_fornecedor = produto.fornecedores.first()
        if primeiro_fornecedor:
            # Nota: Esta operação reversa só funcionará se o campo fornecedor ainda existir
            pass


def remove_old_fields(apps, schema_editor):
    """Remove campos antigos que não são mais necessários"""
    cursor = connection.cursor()
    
    # Remove campo preco se existir
    if connection.vendor == 'postgresql':
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='gearvault_produto' AND column_name='preco';
        """)
        preco_exists = cursor.fetchone()
    else:
        cursor.execute("PRAGMA table_info(gearvault_produto);")
        columns = [row[1] for row in cursor.fetchall()]
        preco_exists = 'preco' in columns
    
    if preco_exists:
        print("Removendo campo preco...")
        cursor.execute("ALTER TABLE gearvault_produto DROP COLUMN IF EXISTS preco;")
    
    # Remove campo fornecedor_id se existir
    if connection.vendor == 'postgresql':
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='gearvault_produto' AND column_name='fornecedor_id';
        """)
        fornecedor_exists = cursor.fetchone()
    else:
        cursor.execute("PRAGMA table_info(gearvault_produto);")
        columns = [row[1] for row in cursor.fetchall()]
        fornecedor_exists = 'fornecedor_id' in columns
    
    if fornecedor_exists:
        print("Removendo campo fornecedor_id...")
        cursor.execute("ALTER TABLE gearvault_produto DROP COLUMN IF EXISTS fornecedor_id;")


class Migration(migrations.Migration):

    dependencies = [
        ('gearvault', '0009_add_produto_fields'),
    ]

    operations = [
        # Verifica e adiciona o campo ManyToMany apenas se necessário
        migrations.RunPython(
            lambda apps, schema_editor: None if check_and_add_fornecedores_field(apps, schema_editor) 
            else None,
            migrations.RunPython.noop
        ),
        
        # Adiciona o campo ManyToMany apenas se a tabela não existir
        migrations.AddField(
            model_name='produto',
            name='fornecedores',
            field=models.ManyToManyField(blank=True, related_name='produtos', to='gearvault.fornecedor'),
        ),
        
        # Migra os dados do campo fornecedor para fornecedores
        migrations.RunPython(migrate_fornecedor_data, reverse_migrate_fornecedor_data),
        
        # Remove os campos antigos de forma segura
        migrations.RunPython(remove_old_fields, migrations.RunPython.noop),
    ]
