#!/usr/bin/env python
"""
Script para testar a configuração de arquivos de mídia
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_media_configuration():
    print("=== Teste de Configuração de Mídia ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    
    # Verificar se os diretórios existem
    print(f"\nDiretório MEDIA_ROOT existe: {os.path.exists(settings.MEDIA_ROOT)}")
    print(f"Diretório STATIC_ROOT existe: {os.path.exists(settings.STATIC_ROOT)}")
    
    # Verificar middleware
    print(f"\nWhiteNoise no MIDDLEWARE: {'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE}")
    
    # Verificar produtos com imagens
    from gearvault.models import Produto
    produtos_com_imagem = Produto.objects.exclude(imagem='')
    produtos_sem_imagem = Produto.objects.filter(imagem='')
    
    print(f"\nProdutos com imagem: {produtos_com_imagem.count()}")
    print(f"Produtos sem imagem: {produtos_sem_imagem.count()}")
    
    if produtos_com_imagem.exists():
        print("\nProdutos com imagem:")
        for produto in produtos_com_imagem[:5]:  # Mostrar apenas os 5 primeiros
            print(f"  - {produto.nome}: {produto.imagem.name}")
            if produto.imagem:
                caminho_completo = os.path.join(settings.MEDIA_ROOT, produto.imagem.name)
                existe = os.path.exists(caminho_completo)
                print(f"    Arquivo existe: {existe}")
                if existe:
                    tamanho = os.path.getsize(caminho_completo)
                    print(f"    Tamanho: {tamanho} bytes")

if __name__ == '__main__':
    test_media_configuration()
