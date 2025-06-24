from django.shortcuts import render, redirect
from .models import Produto, Fornecedor, Compra, ItemCompra, Estoque, LocalArmazenamento, Endereco
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField
from django.contrib.auth.models import User
from contas.models import Profile
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods


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


@login_required
def usuario_estoques(request):
    from django.core.paginator import Paginator
    from django.db.models import Sum, Count

    # Buscar todos os estoques com informações relacionadas
    estoques_list = Estoque.objects.prefetch_related('locais').annotate(
        total_locais=Count('locais'),
        total_itens=Sum('compras__itens__quantidade')
    ).order_by('nome')

    # Configurar paginação
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 30]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10

    paginator = Paginator(estoques_list, per_page)
    page_number = request.GET.get('page')
    estoques = paginator.get_page(page_number)

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'estoques': estoques,
    }
    return render(request, 'pages/user/estoques_list.html', contexto)


@login_required
def usuario_estoque_locais(request, estoque_id):
    """API endpoint para buscar locais de um estoque específico"""
    from django.http import JsonResponse
    from collections import defaultdict
    try:
        estoque = Estoque.objects.get(id=estoque_id)
        locais = LocalArmazenamento.objects.filter(
            estoque=estoque).order_by('nome')
        locais_data = []
        for local in locais:
            # Agrupar itens por compra
            itens = ItemCompra.objects.select_related(
                'produto', 'compra', 'compra__fornecedor').filter(local=local)
            compras_dict = defaultdict(list)
            compras_info = {}
            for item in itens:
                compras_dict[item.compra.id].append({
                    'produto': item.produto.nome,
                    'quantidade': item.quantidade,
                    'valor_unitario': float(item.valor_unitario),
                })
                if item.compra.id not in compras_info:
                    compras_info[item.compra.id] = {
                        'data': item.compra.data.strftime('%d/%m/%Y'),
                        'fornecedor': item.compra.fornecedor.nome,
                        'comprador': item.compra.comprador.user.get_full_name() or item.compra.comprador.user.username,
                    }
            compras = []
            for compra_id, itens_compra in compras_dict.items():
                compras.append({
                    'id': compra_id,
                    'data': compras_info[compra_id]['data'],
                    'fornecedor': compras_info[compra_id]['fornecedor'],
                    'comprador': compras_info[compra_id]['comprador'],
                    'itens': itens_compra
                })
            total_itens = sum(item['quantidade']
                              for compra in compras for item in compra['itens'])
            locais_data.append({
                'id': local.id,
                'nome': local.nome,
                'descricao': local.descricao or '',
                'total_itens': total_itens,
                'compras': compras
            })
        return JsonResponse({
            'success': True,
            'locais': locais_data
        })
    except Estoque.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Estoque não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET", "POST"])
def admin_produto_add(request):
    if request.user.profile.role != 'ADMIN':
        return redirect('login')
    fornecedores = Fornecedor.objects.all()
    if request.method == 'POST':
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        fornecedor_id = request.POST.get('fornecedor')
        categoria = request.POST.get('categoria')
        unidade = request.POST.get('unidade')
        valor_unitario = request.POST.get('valor_unitario')
        descricao = request.POST.get('descricao')
        fornecedor = Fornecedor.objects.filter(
            id=fornecedor_id).first() if fornecedor_id else None
        if nome and codigo and valor_unitario:
            try:
                Produto.objects.create(
                    nome=nome,
                    codigo=codigo,
                    fornecedor=fornecedor,
                    descricao=descricao,
                )
                messages.success(request, 'Produto cadastrado com sucesso!')
                return redirect('admin_produto_add')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar produto: {str(e)}')
        else:
            messages.error(request, 'Preencha os campos obrigatórios.')
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'fornecedores': fornecedores,
    }
    return render(request, 'pages/admin/produto_add.html', contexto)


@login_required
@require_http_methods(["GET", "POST"])
def admin_fornecedor_add(request):
    if request.user.profile.role != 'ADMIN':
        return redirect('login')
    enderecos = Endereco.objects.all()
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco_id = request.POST.get('endereco')
        endereco = Endereco.objects.filter(
            id=endereco_id).first() if endereco_id else None
        if nome and cnpj and email and telefone and endereco:
            try:
                Fornecedor.objects.create(
                    nome=nome,
                    cnpj=cnpj,
                    email=email,
                    telefone=telefone,
                    endereco=endereco
                )
                messages.success(request, 'Fornecedor cadastrado com sucesso!')
                return redirect('admin_fornecedor_add')
            except Exception as e:
                messages.error(
                    request, f'Erro ao cadastrar fornecedor: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'enderecos': enderecos,
    }
    return render(request, 'pages/admin/fornecedor_add.html', contexto)


@login_required
def usuario_compras(request):
    from django.core.paginator import Paginator
    compras_list = Compra.objects.filter(
        comprador__user=request.user).order_by('-data', '-id')
    paginator = Paginator(compras_list, 10)
    page_number = request.GET.get('page')
    compras = paginator.get_page(page_number)
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'compras': compras,
    }
    return render(request, 'pages/user/compras_list.html', contexto)


@login_required
def usuario_compra_detalhes(request, compra_id):
    from django.http import JsonResponse
    from django.utils.dateformat import DateFormat
    from django.utils.formats import get_format
    try:
        compra = Compra.objects.select_related('fornecedor', 'estoque').get(
            id=compra_id, comprador__user=request.user)
        itens = ItemCompra.objects.select_related(
            'produto', 'local').filter(compra=compra)
        itens_data = []
        for item in itens:
            subtotal = item.quantidade * item.valor_unitario
            itens_data.append({
                'produto': item.produto.nome,
                'local': item.local.nome,
                'quantidade': item.quantidade,
                'valor_unitario': f'{item.valor_unitario:.2f}',
                'subtotal': f'{subtotal:.2f}'
            })
        data_formatada = DateFormat(compra.data).format(
            get_format('DATE_FORMAT'))
        response = {
            'success': True,
            'compra': {
                'data': data_formatada,
                'fornecedor': compra.fornecedor.nome,
                'estoque': compra.estoque.nome,
                'valor_total': f'{compra.valor_total:.2f}',
                'invoice_url': compra.invoice.url if compra.invoice else None,
            },
            'itens': itens_data
        }
        return JsonResponse(response)
    except Compra.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Compra não encontrada'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def usuario_compra_add(request):
    from django.db import transaction
    if request.method == 'POST':
        estoque_id = request.POST.get('estoque')
        local_id = request.POST.get('local')
        fornecedor_id = request.POST.get('fornecedor')
        invoice = request.FILES.get('invoice')
        produtos = request.POST.getlist('produto[]')
        quantidades = request.POST.getlist('quantidade[]')
        valores_unitarios = request.POST.getlist('valor_unitario[]')
        erros = []
        if not (estoque_id and local_id and fornecedor_id and produtos and quantidades and valores_unitarios):
            erros.append('Preencha todos os campos obrigatórios.')
        if len(produtos) != len(quantidades) or len(produtos) != len(valores_unitarios):
            erros.append('Itens da compra estão inconsistentes.')
        if erros:
            messages.error(request, ' '.join(erros))
        else:
            try:
                with transaction.atomic():
                    estoque = Estoque.objects.get(id=estoque_id)
                    local = LocalArmazenamento.objects.get(
                        id=local_id, estoque=estoque)
                    fornecedor = Fornecedor.objects.get(id=fornecedor_id)
                    compra = Compra.objects.create(
                        estoque=estoque,
                        fornecedor=fornecedor,
                        comprador=request.user.comprador,
                        invoice=invoice
                    )
                    for i in range(len(produtos)):
                        produto = Produto.objects.get(id=produtos[i])
                        quantidade = int(quantidades[i])
                        valor_unitario = float(valores_unitarios[i])
                        ItemCompra.objects.create(
                            compra=compra,
                            produto=produto,
                            local=local,
                            quantidade=quantidade,
                            valor_unitario=valor_unitario
                        )
                    messages.success(request, 'Compra cadastrada com sucesso!')
                    return redirect('usuario_compras')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar compra: {str(e)}')
    estoques = Estoque.objects.prefetch_related('locais').all()
    fornecedores = Fornecedor.objects.all()
    produtos = Produto.objects.all()
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'estoques': estoques,
        'fornecedores': fornecedores,
        'produtos': produtos,
    }
    return render(request, 'pages/user/compra_add.html', contexto)


def get_sidebar_links(user):
    role = getattr(user.profile, 'role', None)
    if role == 'ADMIN':
        return [
            {'url': '/administrador/painel/', 'label': 'Painel Administrador'},
            {'url': '/administrador/usuarios/', 'label': 'Gerenciar Usuários'},
            {'url': '/administrador/produtos/adicionar/',
                'label': 'Adicionar Produto'},
            {'url': '/administrador/fornecedores/adicionar/',
                'label': 'Adicionar Fornecedor'},
        ]
    elif role == 'USUARIO':
        return [
            {'url': '/usuario/painel/', 'label': 'Dashboard'},
            {'url': '/usuario/perfil/', 'label': 'Perfil'},
            {'url': '/usuario/estoques/', 'label': 'Estoques'},
            {'url': '/usuario/compras/', 'label': 'Minhas Compras'},
            {'url': '/usuario/compras/nova/', 'label': 'Nova Compra'},
        ]
    return []
