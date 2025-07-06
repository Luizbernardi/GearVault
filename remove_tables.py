#!/usr/bin/env python
"""
Script para remover todas as tabelas do GearVault (exceto usuários)
para fazer uma migração limpa.

Execute: python remove_tables.py
"""

import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection


def remove_gearvault_tables():
    """
    Remove todas as tabelas relacionadas ao app gearvault
    """
    cursor = connection.cursor()
    
    try:
        print("Conectado ao banco:", connection.vendor)
        
        # Lista de tabelas do gearvault para remover
        tables_to_remove = [
            'gearvault_solicitacaoproduto',
            'gearvault_itemcompra', 
            'gearvault_compra',
            'gearvault_produto_fornecedores',
            'gearvault_produto',
            'gearvault_localarmazenamento',
            'gearvault_estoque',
            'gearvault_comprador',
            'gearvault_fornecedor',
            'gearvault_endereco',
            'gearvault_loteestoque',  # se existir
        ]
        
        # Remove as tabelas na ordem correta (dependências)
        for table in tables_to_remove:
            try:
                if connection.vendor == 'postgresql':
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                else:
                    cursor.execute(f"DROP TABLE IF EXISTS {table};")
                print(f"✓ Tabela {table} removida")
            except Exception as e:
                print(f"⚠ Erro ao remover {table}: {e}")
        
        # Remove registros de migração do gearvault
        try:
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'gearvault';
            """)
            print("✓ Registros de migração do gearvault removidos")
        except Exception as e:
            print(f"⚠ Erro ao remover registros de migração: {e}")
        
        print("\n🎉 Limpeza concluída!")
        print("Agora você pode executar as novas migrações.")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
        cursor.close()


if __name__ == "__main__":
    print("🧹 Removendo tabelas do GearVault...")
    print("⚠ ATENÇÃO: Este script remove TODAS as tabelas do gearvault!")
    
    confirm = input("Deseja continuar? (digite 'SIM' para confirmar): ")
    if confirm == 'SIM':
        remove_gearvault_tables()
    else:
        print("Operação cancelada.")
