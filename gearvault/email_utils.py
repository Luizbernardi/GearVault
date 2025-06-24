from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
from contas.models import Profile

def send_email_from_user(user, subject, message, recipient_list, fail_silently=True):
    """
    Envia email usando as configurações SMTP do usuário logado
    
    Args:
        user: Usuário que está enviando o email
        subject: Assunto do email
        message: Corpo do email
        recipient_list: Lista de destinatários
        fail_silently: Se deve falhar silenciosamente em caso de erro
    
    Returns:
        bool: True se enviou com sucesso, False caso contrário
    """
    try:
        # Verificar se o usuário tem email configurado
        if not user.email:
            print(f"Usuário {user.username} não tem email configurado")
            return False
            
        # Verificar se o usuário tem perfil com configurações SMTP
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            print(f"Usuário {user.username} não tem perfil configurado")
            return False
            
        # Verificar se tem senha SMTP configurada
        if not profile.email_smtp_password:
            print(f"Usuário {user.username} não tem senha SMTP configurada")
            # Para desenvolvimento, apenas mostra no console
            print(f"EMAIL SIMULADO:")
            print(f"DE: {user.email}")
            print(f"PARA: {recipient_list}")
            print(f"ASSUNTO: {subject}")
            print(f"MENSAGEM: {message}")
            print("-" * 50)
            return True
            
        # Configurar backend SMTP com as credenciais do usuário
        smtp_backend = EmailBackend(
            host=profile.email_smtp_host,
            port=profile.email_smtp_port,
            username=user.email,
            password=profile.email_smtp_password,
            use_tls=profile.email_use_tls,
            fail_silently=fail_silently
        )
        
        # Criar e enviar email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=user.email,
            to=recipient_list,
            connection=smtp_backend
        )
        
        return email.send() > 0
        
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        if not fail_silently:
            raise
        return False


def get_admin_emails():
    """
    Retorna lista de emails dos administradores
    """
    try:
        admin_profiles = Profile.objects.filter(role='ADMIN').select_related('user')
        admin_emails = [profile.user.email for profile in admin_profiles if profile.user.email]
        return admin_emails
    except Exception as e:
        print(f"Erro ao buscar emails de administradores: {e}")
        return []
