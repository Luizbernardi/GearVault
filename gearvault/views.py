from django.shortcuts import render
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


def home(request):
    produtos = Produto.objects.all()
    return render(request, 'pages/home.html', {'produtos': produtos})
