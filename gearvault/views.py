from django.shortcuts import render, redirect
from .models import Produto, Fornecedor, Compra, ItemCompra, Estoque, LocalArmazenamento
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField
from django.contrib.auth.models import User
from contas.models import Profile
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction


@login_required
def usuario_painel(request):
    if request.user.profile.role != 'USUARIO':
        if request.user.profile.role == 'ADMIN':
            return redirect('admin_painel')
        return redirect('login')

    produtos = Produto.objects.all()
    total_produtos = produtos.count()
    total_estoque = ItemCompra.objects.aggregate(
        total=Sum('quantidade'))['total'] or 0
    valor_total_estoque = ItemCompra.objects.aggregate(
        total=Sum(F('quantidade') * F('valor_unitario'),
                  output_field=FloatField())
    )['total'] or 0
    compras = Compra.objects.filter(comprador__user=request.user)
    estoques = Estoque.objects.prefetch_related('locais', 'compras')
    fornecedores = Fornecedor.objects.all()
    # Movimentações recentes apenas do usuário logado (ItemCompra das compras do usuário)
    movimentacoes = ItemCompra.objects.filter(
        compra__comprador__user=request.user).order_by('-id')[:5]

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'produtos': produtos,
        'total_produtos': total_produtos,
        'total_estoque': total_estoque,
        'valor_total_estoque': valor_total_estoque,
        'compras': compras,
        'estoques': estoques,
        'fornecedores': fornecedores,
        'movimentacoes': movimentacoes,
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
    total_estoque = ItemCompra.objects.aggregate(
        total=Sum('quantidade'))['total'] or 0
    valor_total_estoque = ItemCompra.objects.aggregate(
        total=Sum(F('quantidade') * F('valor_unitario'),
                  output_field=FloatField())
    )['total'] or 0
    compras = Compra.objects.all()
    estoques = Estoque.objects.prefetch_related('locais', 'compras')
    fornecedores = Fornecedor.objects.all()
    movimentacoes = ItemCompra.objects.select_related(
        'produto', 'local', 'compra', 'compra__estoque').order_by('-id')[:5]

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'produtos': produtos,
        'total_produtos': total_produtos,
        'total_estoque': total_estoque,
        'valor_total_estoque': valor_total_estoque,
        'compras': compras,
        'estoques': estoques,
        'fornecedores': fornecedores,
        'movimentacoes': movimentacoes,
    }
    return render(request, 'pages/admin/painel.html', contexto)


def admin_usuarios_list(request):
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return redirect('login')

    per_page = int(request.GET.get('per_page', 10))

    # Adição de usuário
    if request.method == 'POST' and 'add-usuario' in request.POST:
        username = request.POST.get('add-username')
        email = request.POST.get('add-email')
        role = request.POST.get('add-role')
        password = request.POST.get('add-password')
        if username and email and role and password:
            if not User.objects.filter(username=username).exists():
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=username, email=email, password=password)
                        # Profile é criado automaticamente pelo signal
                        user.profile.role = role
                        user.profile.save()
                    messages.success(
                        request, 'Usuário cadastrado com sucesso!')
                except Exception as e:
                    messages.error(
                        request, 'Erro ao cadastrar usuário: ' + str(e))
            else:
                messages.error(request, 'Nome de usuário já existe.')
        else:
            messages.error(
                request, 'Preencha todos os campos para cadastrar um usuário.')
        return redirect('admin_usuarios_list')

    # Edição de usuário
    if request.method == 'POST' and 'username' in request.POST and 'email' in request.POST and 'role' in request.POST:
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        try:
            user = User.objects.get(id=user_id)
            user.username = username
            user.email = email
            user.save()
            profile = user.profile
            profile.role = role
            profile.save()
            messages.success(request, 'Usuário editado com sucesso!')
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
        return redirect('admin_usuarios_list')
    # Exclusão de usuário
    if request.method == 'POST' and 'user_id' in request.POST and 'delete-user-id' in request.POST:
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            messages.success(request, 'Usuário excluído com sucesso!')
        except User.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
        return redirect('admin_usuarios_list')

    usuarios = User.objects.select_related('profile').all().order_by('id')
    paginator = Paginator(usuarios, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'usuarios': page_obj,
    }
    return render(request, 'pages/admin/usuarios_list.html', contexto)


@login_required
def usuario_perfil(request):
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'user': request.user,
    }
    return render(request, 'pages/user/perfil.html', contexto)


def get_sidebar_links(user):
    role = getattr(user.profile, 'role', None)
    if role == 'ADMIN':
        return [
            {'url': '/administrador/painel/', 'label': 'Painel Administrador'},
            {'url': '/administrador/usuarios/', 'label': 'Gerenciar Usuários'},
        ]
    elif role == 'USUARIO':
        return [
            {'url': '/usuario/painel/', 'label': 'Dashboard'},
            {'url': '/usuario/perfil/', 'label': 'Perfil'},
        ]
    return []
