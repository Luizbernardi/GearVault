from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('USUARIO', 'Usuário'),
        ('ADMIN', 'Administrador'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Configurações de email SMTP
    email_smtp_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Senha de app do Gmail ou senha do email para SMTP"
    )
    email_smtp_host = models.CharField(
        max_length=255,
        default='smtp.gmail.com',
        help_text="Servidor SMTP (ex: smtp.gmail.com)"
    )
    email_smtp_port = models.IntegerField(
        default=587,
        help_text="Porta SMTP (ex: 587 para TLS, 465 para SSL)"
    )
    email_use_tls = models.BooleanField(
        default=True,
        help_text="Usar TLS para conexão segura"
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def can_send_email(self):
        """Verifica se o usuário tem configuração completa para enviar emails"""
        return bool(self.user.email and self.email_smtp_password)
