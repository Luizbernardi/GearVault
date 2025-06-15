from django.shortcuts import render, redirect
from .models import Produto
from django.contrib.auth.decorators import login_required
# Create your views here.


# @login_required(login_url='login')
# def index(request):
#     contatos = Contato.objects.all()
#     categorias = Categoria.objects.all()
#     return render(request, 'pages/index.html', {'contatos': contatos, 'categorias': categorias})


# @login_required(login_url='login')
# def contato_detalhes(request, id):
# contato = Contato.objects.get(id=id)
# , {'contato': contato})
#   return render(request, 'pages/contato_detalhes.html', {'contato': Contato.objects.get(id=id)})

@login_required
def usuario_painel(request):
    if request.user.profile.role != 'USUARIO':
        # Se não for usuário comum, redireciona para o painel correto
        if request.user.profile.role == 'ADMIN':
            return redirect('admin_painel')
        return redirect('login')  # Se não tiver role válida, vai para login
    return render(request, 'pages/user/painel.html')

@login_required
def admin_painel(request):
    if request.user.profile.role != 'ADMIN':
        # Se não for admin, redireciona para o painel correto
        if request.user.profile.role == 'USUARIO':
            return redirect('usuario_painel')
        return redirect('login')  # Se não tiver role válida, vai para login
    return render(request, 'pages/admin/painel.html')