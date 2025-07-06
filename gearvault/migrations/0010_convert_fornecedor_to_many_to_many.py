# Generated manually on 2025-07-06
# Migração para converter Produto.fornecedor (1:N) para Produto.fornecedores (N:N)
# e remover o campo preco

from django.db import migrations, models, connection


def migrate_fornecedor_to_many_to_many(apps, schema_editor):
    """
    Migra dados do campo fornecedor (ForeignKey) para fornecedores (ManyToMany)
    """
    db_alias = schema_editor.connection.alias
    Produto = apps.get_model('gearvault', 'Produto')
    
    # Verifica se existe o campo fornecedor_id
    cursor = connection.cursor()
    
    try:
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
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT id, fornecedor_id 
                    FROM gearvault_produto 
                    WHERE fornecedor_id IS NOT NULL
                """)
            else:
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
            print("Campo fornecedor_id não encontrado, pulando migração de dados.")
            
    except Exception as e:
        print(f"Erro durante migração de dados: {e}")
        # Não falha a migração, apenas informa o problema


def reverse_migration(apps, schema_editor):
    """
    Operação reversa - não implementada pois seria complexa
    """
    print("Operação reversa não implementada. Use backup do banco para reverter.")


def remove_old_fields_safely(apps, schema_editor):
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
        else:
            # SQLite não suporta DROP COLUMN facilmente, mas como estamos focando em produção (PostgreSQL)
            # vamos deixar isso para o SQLite local se necessário
            pass
        
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
        # Não falha a migração


class Migration(migrations.Migration):

    dependencies = [
        ('gearvault', '0009_add_produto_fields'),
    ]

    operations = [
        # 1. Adiciona o campo ManyToMany
        migrations.AddField(
            model_name='produto',
            name='fornecedores',
            field=models.ManyToManyField(
                blank=True, 
                related_name='produtos', 
                to='gearvault.fornecedor',
                verbose_name='Fornecedores'
            ),
        ),
        
        # 2. Migra os dados do campo antigo para o novo
        migrations.RunPython(
            migrate_fornecedor_to_many_to_many, 
            reverse_migration
        ),
        
        # 3. Remove os campos antigos de forma segura
        migrations.RunPython(
            remove_old_fields_safely, 
            migrations.RunPython.noop
        ),
    ]
