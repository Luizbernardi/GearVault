# Generated manually on 2025-07-06
# Migração simplificada apenas para migrar dados e remover campos antigos
# Assume que a tabela gearvault_produto_fornecedores já existe

from django.db import migrations, connection


def migrate_existing_data(apps, schema_editor):
    """
    Migra dados do campo fornecedor para fornecedores (apenas se o campo ainda existir)
    """
    cursor = connection.cursor()
    
    try:
        # Verifica se existe o campo fornecedor_id
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='gearvault_produto' AND column_name='fornecedor_id'
                    AND table_schema = current_schema();
            """)
            has_fornecedor = cursor.fetchone() is not None
        else:  # SQLite
            cursor.execute("PRAGMA table_info(gearvault_produto);")
            columns = [row[1] for row in cursor.fetchall()]
            has_fornecedor = 'fornecedor_id' in columns
        
        if has_fornecedor:
            print("Migrando dados de fornecedor único para fornecedores múltiplos...")
            
            # Busca todos os produtos que têm fornecedor definido
            cursor.execute("""
                SELECT id, fornecedor_id 
                FROM gearvault_produto 
                WHERE fornecedor_id IS NOT NULL
            """)
            produtos_com_fornecedor = cursor.fetchall()
            
            # Para cada produto, adiciona o fornecedor na tabela intermediária
            for produto_id, fornecedor_id in produtos_com_fornecedor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        INSERT INTO gearvault_produto_fornecedores (produto_id, fornecedor_id)
                        VALUES (%s, %s)
                        ON CONFLICT (produto_id, fornecedor_id) DO NOTHING
                    """, [produto_id, fornecedor_id])
                else:
                    cursor.execute("""
                        INSERT OR IGNORE INTO gearvault_produto_fornecedores (produto_id, fornecedor_id)
                        VALUES (?, ?)
                    """, [produto_id, fornecedor_id])
            
            print(f"Migrados {len(produtos_com_fornecedor)} produtos com fornecedores.")
        else:
            print("Campo fornecedor_id não encontrado, dados já migrados.")
            
    except Exception as e:
        print(f"Erro durante migração de dados: {e}")


def remove_old_fields(apps, schema_editor):
    """
    Remove campos antigos de forma segura
    """
    cursor = connection.cursor()
    
    try:
        # Remove campo fornecedor_id se existir
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='gearvault_produto' AND column_name='fornecedor_id'
                    AND table_schema = current_schema();
            """)
            if cursor.fetchone():
                cursor.execute("ALTER TABLE gearvault_produto DROP COLUMN IF EXISTS fornecedor_id")
                print("Campo fornecedor_id removido com sucesso.")
        
        # Remove campo preco se existir
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='gearvault_produto' AND column_name='preco'
                    AND table_schema = current_schema();
            """)
            if cursor.fetchone():
                cursor.execute("ALTER TABLE gearvault_produto DROP COLUMN IF EXISTS preco")
                print("Campo preco removido com sucesso.")
        
    except Exception as e:
        print(f"Erro ao remover campos antigos: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('gearvault', '0009_add_produto_fields'),
    ]

    operations = [
        # 1. Migra os dados do campo antigo para o novo
        migrations.RunPython(
            migrate_existing_data, 
            migrations.RunPython.noop
        ),
        
        # 2. Remove os campos antigos de forma segura
        migrations.RunPython(
            remove_old_fields, 
            migrations.RunPython.noop
        ),
    ]
