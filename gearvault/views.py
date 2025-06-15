from django.shortcuts import render, redirect
from .models import Produto, Fornecedor, Compra, ItemCompra, Estoque, LocalArmazenamento
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField


@login_required
def usuario_painel(request):
    if request.user.profile.role != 'USUARIO':
        if request.user.profile.role == 'ADMIN':
            return redirect('admin_painel')
        return redirect('login')

    produtos = Produto.objects.all()
    total_produtos = produtos.count()
    total_estoque = Estoque.objects.aggregate(
        total=Sum('lote__item_compra__quantidade'))['total'] or 0
    valor_total_estoque = ItemCompra.objects.aggregate(
        total=Sum(F('quantidade') * F('valor_unitario'),
                  output_field=FloatField())
    )['total'] or 0
    compras = Compra.objects.filter(comprador__user=request.user)
    estoques = Estoque.objects.select_related(
        'lote', 'local', 'lote__item_compra', 'lote__item_compra__produto')
    fornecedores = Fornecedor.objects.all()

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'produtos': produtos,
        'total_produtos': total_produtos,
        'total_estoque': total_estoque,
        'valor_total_estoque': valor_total_estoque,
        'compras': compras,
        'estoques': estoques,
        'fornecedores': fornecedores,
    }
    return render(request, 'pages/user/painel.html', contexto)


@login_required
def admin_painel(request):
    if request.user.profile.role != 'ADMIN':
        if request.user.profile.role == 'USUARIO':
            return redirect('usuario_painel')
        return redirect('login')

    produtos = Produto.objects.all()
    total_produtos = produtos.count()
    total_estoque = Estoque.objects.aggregate(
        total=Sum('lote__item_compra__quantidade'))['total'] or 0
    valor_total_estoque = ItemCompra.objects.aggregate(
        total=Sum(F('quantidade') * F('valor_unitario'),
                  output_field=FloatField())
    )['total'] or 0
    compras = Compra.objects.all()
    estoques = Estoque.objects.select_related(
        'lote', 'local', 'lote__item_compra', 'lote__item_compra__produto')
    fornecedores = Fornecedor.objects.all()

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'produtos': produtos,
        'total_produtos': total_produtos,
        'total_estoque': total_estoque,
        'valor_total_estoque': valor_total_estoque,
        'compras': compras,
        'estoques': estoques,
        'fornecedores': fornecedores,
    }
    return render(request, 'pages/admin/painel.html', contexto)

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
