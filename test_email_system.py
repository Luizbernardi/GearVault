#!/usr/bin/env python
"""
Script de teste para o sistema de email do Gear Vault
Execute: python test_email_system.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from contas.models import Profile
from gearvault.email_utils import send_email_from_user, get_admin_emails

def test_email_configuration():
    """Testa as configurações de email dos usuários"""
    print("=== TESTE DO SISTEMA DE EMAIL ===\n")
    
    # Listar todos os usuários e suas configurações
    usuarios = User.objects.all().select_related('profile')
    
    for usuario in usuarios:
        print(f"Usuário: {usuario.username}")
        print(f"Email: {usuario.email or 'NÃO CONFIGURADO'}")
        
        try:
            profile = usuario.profile
            print(f"Função: {profile.get_role_display()}")
            print(f"Pode enviar email: {'SIM' if profile.can_send_email() else 'NÃO'}")
            print(f"Servidor SMTP: {profile.email_smtp_host}")
            print(f"Porta: {profile.email_smtp_port}")
            print(f"TLS: {'SIM' if profile.email_use_tls else 'NÃO'}")
            print(f"Senha configurada: {'SIM' if profile.email_smtp_password else 'NÃO'}")
        except Profile.DoesNotExist:
            print("ERRO: Perfil não encontrado")
        
        print("-" * 40)
    
    # Testar busca de emails de administradores
    print("\n=== ADMINISTRADORES ===")
    admin_emails = get_admin_emails()
    print(f"Emails de administradores encontrados: {admin_emails}")
    
    # Testar envio de email de teste
    print("\n=== TESTE DE ENVIO ===")
    if usuarios.exists():
        usuario_teste = usuarios.first()
        print(f"Testando envio com usuário: {usuario_teste.username}")
        
        resultado = send_email_from_user(
            user=usuario_teste,
            subject="Teste do Sistema de Email - Gear Vault",
            message="Este é um email de teste do sistema Gear Vault.",
            recipient_list=["teste@exemplo.com"],
            fail_silently=True
        )
        
        print(f"Resultado do envio: {'SUCESSO' if resultado else 'FALHA'}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    test_email_configuration()
