from django.shortcuts import render, redirect
from .models import Produto
from django.contrib.auth.decorators import login_required

@login_required
def usuario_painel(request):
    if request.user.profile.role != 'USUARIO':
        if request.user.profile.role == 'ADMIN':
            return redirect('admin_painel')
        return redirect('login')

    return render(request, 'pages/user/painel.html', {'sidebar_links': get_sidebar_links(request.user)})

@login_required
def admin_painel(request):
    if request.user.profile.role != 'ADMIN':
        if request.user.profile.role == 'USUARIO':
            return redirect('usuario_painel')
        return redirect('login')

    return render(request, 'pages/admin/painel.html', {'sidebar_links': get_sidebar_links(request.user)})

    # TODO: Adicionar URLs correspondentes para os painéis de administrador e usuário aqui.
def get_sidebar_links(user):
    role = getattr(user.profile, 'role', None)
    if role == 'ADMIN':
        return [
            {'url': '', 'label': 'Painel Administrador'},
            {'url': '', 'label': 'Gerenciar Usuários'},
        ]
    elif role == 'USUARIO':
        return [
            {'url': '', 'label': 'Dashboard'},
            {'url': '', 'label': 'Perfil'},
        ]
    return []
