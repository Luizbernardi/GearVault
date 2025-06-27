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
    
    # Buscar solicitações recentes do usuário
    from .models import SolicitacaoProduto
    minhas_solicitacoes = SolicitacaoProduto.objects.filter(
        usuario=request.user
    ).select_related('produto', 'local', 'local__estoque').order_by('-data_solicitacao')[:5]
    
    # Buscar produtos disponíveis em estoque (agregados por produto/local)
    produtos_disponiveis = ItemCompra.objects.values(
        'produto__nome', 'local__nome', 'local__estoque__nome'
    ).annotate(
        quantidade_total=Sum('quantidade')
    ).filter(
        quantidade_total__gt=0
    ).order_by('-quantidade_total')[:5]
    
    estoques = Estoque.objects.prefetch_related('locais')
    fornecedores = Fornecedor.objects.all()

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'produtos': produtos,
        'total_produtos': total_produtos,
        'total_estoque': total_estoque,
        'minhas_solicitacoes': minhas_solicitacoes,
        'produtos_disponiveis': produtos_disponiveis,
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
    # View simplificada - apenas exibe informações do perfil
    # Configurações SMTP são gerenciadas apenas por administradores
    
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
        total_locais=Count('locais', distinct=True)
    ).order_by('nome')
    
    # Calcular total de itens separadamente para evitar problemas com joins múltiplos
    for estoque in estoques_list:
        total_itens = ItemCompra.objects.filter(
            local__estoque=estoque
        ).aggregate(total=Sum('quantidade'))['total'] or 0
        estoque.total_itens = total_itens

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
    from decimal import Decimal
    try:
        estoque = Estoque.objects.get(id=estoque_id)
        locais = LocalArmazenamento.objects.filter(
            estoque=estoque).order_by('nome')
        locais_data = []
        for local in locais:
            # Agrupar itens por compra com informações detalhadas
            itens = ItemCompra.objects.select_related(
                'produto', 'compra', 'compra__fornecedor', 'compra__comprador__user').filter(local=local)
            compras_dict = defaultdict(list)
            compras_info = {}
            for item in itens:
                subtotal = item.quantidade * item.valor_unitario
                compras_dict[item.compra.id].append({
                    'produto': item.produto.nome,
                    'codigo': item.produto.codigo,
                    'quantidade': item.quantidade,
                    'valor_unitario': float(item.valor_unitario),
                    'subtotal': float(subtotal),
                })
                if item.compra.id not in compras_info:
                    compras_info[item.compra.id] = {
                        'data': item.compra.data.strftime('%d/%m/%Y'),
                        'fornecedor': item.compra.fornecedor.nome,
                        'comprador': item.compra.comprador.user.get_full_name() or item.compra.comprador.user.username,
                        'valor_total': float(item.compra.valor_total) if item.compra.valor_total else 0.0,
                        'invoice_url': item.compra.invoice.url if item.compra.invoice else None,
                    }
            compras = []
            for compra_id, itens_compra in compras_dict.items():
                total_itens = sum(item['quantidade'] for item in itens_compra)
                valor_total_compra = sum(item['subtotal']
                                         for item in itens_compra)
                compras.append({
                    'id': compra_id,
                    'data': compras_info[compra_id]['data'],
                    'fornecedor': compras_info[compra_id]['fornecedor'],
                    'comprador': compras_info[compra_id]['comprador'],
                    'valor_total': compras_info[compra_id]['valor_total'],
                    'invoice_url': compras_info[compra_id]['invoice_url'],
                    'total_itens': total_itens,
                    'valor_itens_local': valor_total_compra,
                    'itens': itens_compra
                })
            # Ordenar compras por data (mais recente primeiro)
            compras.sort(key=lambda x: x['data'], reverse=True)
            total_itens = sum(item['quantidade']
                              for compra in compras for item in compra['itens'])
            locais_data.append({
                'id': local.id,
                'nome': local.nome,
                'descricao': local.descricao or '',
                'total_itens': total_itens,
                'total_compras': len(compras),
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
def admin_fornecedor_list(request):
    if request.user.profile.role != 'ADMIN':
        return redirect('login')

    per_page = int(request.GET.get('per_page', 10))
    enderecos = Endereco.objects.all()

    # Adição de fornecedor
    if request.method == 'POST' and 'add-fornecedor' in request.POST:
        nome = request.POST.get('add-nome')
        cnpj = request.POST.get('add-cnpj')
        email = request.POST.get('add-email')
        telefone = request.POST.get('add-telefone')
        endereco_id = request.POST.get('add-endereco')
        # Campos do novo endereço
        novo_logradouro = request.POST.get('novo-logradouro')
        novo_numero = request.POST.get('novo-numero')
        novo_bairro = request.POST.get('novo-bairro')
        novo_cidade = request.POST.get('novo-cidade')
        novo_estado = request.POST.get('novo-estado')
        novo_cep = request.POST.get('novo-cep')
        novo_complemento = request.POST.get('novo-complemento')
        endereco = None
        # Se algum campo de novo endereço foi preenchido, cria o endereço
        if novo_logradouro and novo_numero and novo_bairro and novo_cidade and novo_estado and novo_cep:
            endereco = Endereco.objects.create(
                logradouro=novo_logradouro,
                numero=novo_numero,
                bairro=novo_bairro,
                cidade=novo_cidade,
                estado=novo_estado,
                cep=novo_cep,
                complemento=novo_complemento
            )
        elif endereco_id:
            endereco = Endereco.objects.filter(id=endereco_id).first()
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
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar fornecedor: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        return redirect('admin_fornecedor_list')

    # Edição de fornecedor
    if request.method == 'POST' and 'fornecedor_id' in request.POST and 'nome' in request.POST and 'cnpj' in request.POST and 'email' in request.POST and 'telefone' in request.POST and 'endereco' in request.POST:
        fornecedor_id = request.POST.get('fornecedor_id')
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        endereco_id = request.POST.get('endereco')
        endereco = Endereco.objects.filter(id=endereco_id).first() if endereco_id else None
        try:
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            fornecedor.nome = nome
            fornecedor.cnpj = cnpj
            fornecedor.email = email
            fornecedor.telefone = telefone
            fornecedor.endereco = endereco
            fornecedor.save()
            messages.success(request, 'Fornecedor editado com sucesso!')
        except Fornecedor.DoesNotExist:
            messages.error(request, 'Fornecedor não encontrado.')
        return redirect('admin_fornecedor_list')

    # Exclusão de fornecedor
    if request.method == 'POST' and 'fornecedor_id' in request.POST and 'delete-fornecedor-id' in request.POST:
        fornecedor_id = request.POST.get('fornecedor_id')
        try:
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            fornecedor.delete()
            messages.success(request, 'Fornecedor excluído com sucesso!')
        except Fornecedor.DoesNotExist:
            messages.error(request, 'Fornecedor não encontrado.')
        return redirect('admin_fornecedor_list')

    fornecedores = Fornecedor.objects.select_related('endereco').all().order_by('id')
    paginator = Paginator(fornecedores, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'fornecedores': page_obj,
        'enderecos': enderecos,
    }
    return render(request, 'pages/admin/fornecedor_list.html', contexto)


@login_required
@require_http_methods(["GET", "POST"])
def admin_produto_list(request):
    if request.user.profile.role != 'ADMIN':
        return redirect('login')

    per_page = int(request.GET.get('per_page', 10))

    # Adição de produto
    if request.method == 'POST' and 'add-produto' in request.POST:
        nome = request.POST.get('add-nome')
        codigo = request.POST.get('add-codigo')
        categoria = request.POST.get('add-categoria')
        preco = request.POST.get('add-preco')
        imagem = request.FILES.get('add-imagem')
        descricao = request.POST.get('add-descricao')
        if nome and codigo and categoria and preco is not None:
            try:
                Produto.objects.create(
                    nome=nome,
                    codigo=codigo,
                    categoria=categoria,
                    preco=preco,
                    imagem=imagem,
                    descricao=descricao,
                )
                messages.success(request, 'Produto cadastrado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar produto: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        return redirect('admin_produto_list')

    # Edição de produto
    if request.method == 'POST' and 'produto_id' in request.POST and 'nome' in request.POST and 'codigo' in request.POST and 'categoria' in request.POST and 'preco' in request.POST:
        produto_id = request.POST.get('produto_id')
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        categoria = request.POST.get('categoria')
        preco = request.POST.get('preco')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get('descricao')
        fornecedor_id = request.POST.get('fornecedor')
        fornecedor = Fornecedor.objects.filter(id=fornecedor_id).first() if fornecedor_id else None
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.nome = nome
            produto.codigo = codigo
            produto.categoria = categoria
            produto.preco = preco
            if imagem:
                produto.imagem = imagem
            produto.descricao = descricao
            produto.fornecedor = fornecedor
            produto.save()
            messages.success(request, 'Produto editado com sucesso!')
        except Produto.DoesNotExist:
            messages.error(request, 'Produto não encontrado.')
        return redirect('admin_produto_list')

    # Exclusão de produto
    if request.method == 'POST' and 'produto_id' in request.POST and 'delete-produto-id' in request.POST:
        produto_id = request.POST.get('produto_id')
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.delete()
            messages.success(request, 'Produto excluído com sucesso!')
        except Produto.DoesNotExist:
            messages.error(request, 'Produto não encontrado.')
        return redirect('admin_produto_list')

    produtos = Produto.objects.all().order_by('id')
    fornecedores = Fornecedor.objects.all()
    paginator = Paginator(produtos, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'produtos': page_obj,
        'fornecedores': fornecedores,    }
    return render(request, 'pages/admin/produto_list.html', contexto)


@login_required
def usuario_estoque_detalhes(request, estoque_id):
    from django.core.paginator import Paginator
    from django.db.models import Sum
    try:
        estoque = Estoque.objects.prefetch_related('locais').get(id=estoque_id)
        locais_list = LocalArmazenamento.objects.filter(
            estoque=estoque).order_by('nome')

        # Adicionar informações de produtos para cada local
        for local in locais_list:
            # Buscar produtos únicos neste local com totais
            produtos_no_local = ItemCompra.objects.filter(local=local).values(
                'produto__nome', 'produto__codigo', 'produto__id'
            ).annotate(
                quantidade_total=Sum('quantidade')
            ).order_by('produto__nome')
            local.produtos = produtos_no_local
            local.total_produtos = produtos_no_local.count()

        # Configurar paginação para locais
        per_page = request.GET.get('per_page', 5)
        try:
            per_page = int(per_page)
            if per_page not in [5, 10, 15]:
                per_page = 5
        except (ValueError, TypeError):
            per_page = 5

        paginator = Paginator(locais_list, per_page)
        page_number = request.GET.get('page')
        locais = paginator.get_page(page_number)

        contexto = {
            'sidebar_links': get_sidebar_links(request.user),
            'estoque': estoque,
            'locais': locais,
        }
        return render(request, 'pages/user/estoque_detalhes.html', contexto)
    except Estoque.DoesNotExist:
        messages.error(request, 'Estoque não encontrado.')
        return redirect('usuario_estoques')


# Solicitações de Produtos

@login_required
def usuario_solicitar_produto(request, local_id, produto_id):
    """View para criar uma solicitação de produto"""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.urls import reverse

    try:
        local = LocalArmazenamento.objects.get(id=local_id)
        produto = Produto.objects.get(id=produto_id)

        # Verificar se há estoque disponível
        quantidade_disponivel = ItemCompra.objects.filter(
            local=local, produto=produto
        ).aggregate(total=Sum('quantidade'))['total'] or 0

        if request.method == 'POST':
            quantidade = int(request.POST.get('quantidade', 0))
            justificativa = request.POST.get('justificativa', '').strip()

            if quantidade <= 0:
                messages.error(request, 'Quantidade deve ser maior que zero.')
            elif quantidade > quantidade_disponivel:
                messages.error(
                    request, f'Quantidade solicitada excede o estoque disponível ({quantidade_disponivel} unidades).')
            elif not justificativa:
                messages.error(request, 'Justificativa é obrigatória.')
            else:
                # Criar solicitação
                from .models import SolicitacaoProduto
                solicitacao = SolicitacaoProduto.objects.create(
                    usuario=request.user,
                    produto=produto,
                    local=local,
                    quantidade=quantidade,
                    justificativa=justificativa
                )                # Enviar email para administradores usando o email do usuário logado
                try:
                    from .email_utils import send_email_from_user, get_admin_emails

                    admin_emails = get_admin_emails()

                    if admin_emails:
                        subject = f'Nova Solicitação de Produto - {produto.nome}'
                        message = f"""
Nova solicitação de produto recebida:

Solicitante: {request.user.get_full_name() or request.user.username}
Email: {request.user.email}
Produto: {produto.nome} ({produto.codigo})
Local: {local.nome} ({local.estoque.nome})
Quantidade: {quantidade}
Justificativa: {justificativa}

Para aprovar ou rejeitar esta solicitação, acesse:
{request.build_absolute_uri(reverse('admin_solicitacoes'))}

ID da Solicitação: {solicitacao.id}
                        """

                        send_email_from_user(
                            user=request.user,
                            subject=subject,
                            message=message,
                            recipient_list=admin_emails,
                            fail_silently=True
                        )
                    else:
                        print("Nenhum administrador com email configurado encontrado")

                except Exception as e:
                    print(f"Erro ao enviar email: {e}")
                    # Não falha a solicitação se o email não for enviado

                messages.success(
                    request, 'Solicitação criada com sucesso! O administrador será notificado.')
                return redirect('usuario_estoque_detalhes', estoque_id=local.estoque.id)

        contexto = {
            'sidebar_links': get_sidebar_links(request.user),
            'local': local,
            'produto': produto,
            'quantidade_disponivel': quantidade_disponivel,
        }
        return render(request, 'pages/user/solicitar_produto.html', contexto)

    except (LocalArmazenamento.DoesNotExist, Produto.DoesNotExist):
        messages.error(request, 'Local ou produto não encontrado.')
        return redirect('usuario_estoques')


@login_required
def usuario_minhas_solicitacoes(request):
    """Lista das solicitações do usuário"""
    from .models import SolicitacaoProduto

    solicitacoes_list = SolicitacaoProduto.objects.filter(
        usuario=request.user
    ).select_related('produto', 'local', 'local__estoque').order_by('-data_solicitacao')

    # Paginação
    paginator = Paginator(solicitacoes_list, 10)
    page_number = request.GET.get('page')
    solicitacoes = paginator.get_page(page_number)

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'solicitacoes': solicitacoes,
    }
    return render(request, 'pages/user/minhas_solicitacoes.html', contexto)


@login_required
def admin_solicitacoes(request):
    """Lista de solicitações para administradores"""
    if request.user.profile.role != 'ADMIN':
        return redirect('login')

    from .models import SolicitacaoProduto

    status_filter = request.GET.get('status', 'PENDENTE')
    solicitacoes_list = SolicitacaoProduto.objects.select_related(
        'usuario', 'produto', 'local', 'local__estoque'
    ).order_by('-data_solicitacao')

    if status_filter and status_filter != 'TODAS':
        solicitacoes_list = solicitacoes_list.filter(status=status_filter)

    # Paginação
    paginator = Paginator(solicitacoes_list, 15)
    page_number = request.GET.get('page')
    solicitacoes = paginator.get_page(page_number)

    contexto = {
        'sidebar_links': get_sidebar_links(request.user),
        'solicitacoes': solicitacoes,
        'status_filter': status_filter,
    }
    return render(request, 'pages/admin/solicitacoes_list.html', contexto)


@login_required
def admin_processar_solicitacao(request, solicitacao_id):
    """Processar (aprovar/rejeitar) solicitação"""
    if request.user.profile.role != 'ADMIN':
        return redirect('login')

    from .models import SolicitacaoProduto
    from django.core.mail import send_mail
    from django.conf import settings
    from django.utils import timezone

    try:
        solicitacao = SolicitacaoProduto.objects.select_related(
            'usuario', 'produto', 'local'
        ).get(id=solicitacao_id)

        if solicitacao.status != 'PENDENTE':
            messages.error(request, 'Esta solicitação já foi processada.')
            return redirect('admin_solicitacoes')

        if request.method == 'POST':
            acao = request.POST.get('acao')
            resposta_admin = request.POST.get('resposta_admin', '').strip()

            if acao == 'aprovar':
                # Verificar se ainda há estoque suficiente
                quantidade_disponivel = ItemCompra.objects.filter(
                    local=solicitacao.local, produto=solicitacao.produto
                ).aggregate(total=Sum('quantidade'))['total'] or 0

                if solicitacao.quantidade > quantidade_disponivel:
                    messages.error(
                        request, f'Estoque insuficiente. Disponível: {quantidade_disponivel} unidades.')
                    return redirect('admin_processar_solicitacao', solicitacao_id=solicitacao_id)

                # Reduzir do estoque
                itens_compra = ItemCompra.objects.filter(
                    local=solicitacao.local, produto=solicitacao.produto
                ).order_by('compra__data')

                quantidade_restante = solicitacao.quantidade

                with transaction.atomic():
                    for item in itens_compra:
                        if quantidade_restante <= 0:
                            break

                        if item.quantidade <= quantidade_restante:
                            quantidade_restante -= item.quantidade
                            item.delete()
                        else:
                            item.quantidade -= quantidade_restante
                            item.save()
                            quantidade_restante = 0

                    solicitacao.status = 'APROVADA'
                    solicitacao.data_resposta = timezone.now()
                    solicitacao.admin_responsavel = request.user
                    solicitacao.resposta_admin = resposta_admin
                    solicitacao.save()

                status_msg = 'aprovada'
                messages.success(request, 'Solicitação aprovada com sucesso!')

            elif acao == 'rejeitar':
                solicitacao.status = 'REJEITADA'
                solicitacao.data_resposta = timezone.now()
                solicitacao.admin_responsavel = request.user
                solicitacao.resposta_admin = resposta_admin
                solicitacao.save()

                status_msg = 'rejeitada'
                messages.success(request, 'Solicitação rejeitada.')

            else:
                messages.error(request, 'Ação inválida.')
                # Enviar email ao usuário usando o email do admin logado
                return redirect('admin_processar_solicitacao', solicitacao_id=solicitacao_id)
            try:
                if solicitacao.usuario.email:
                    from .email_utils import send_email_from_user

                    subject = f'Solicitação {status_msg.capitalize()} - {solicitacao.produto.nome}'
                    message = f"""
Sua solicitação foi {status_msg}:

Produto: {solicitacao.produto.nome} ({solicitacao.produto.codigo})
Quantidade: {solicitacao.quantidade}
Status: {solicitacao.get_status_display()}
Processado por: {request.user.get_full_name() or request.user.username}
Data: {solicitacao.data_resposta.strftime('%d/%m/%Y às %H:%M')}

{f'Resposta do administrador: {resposta_admin}' if resposta_admin else ''}

Você pode verificar suas solicitações em: {request.build_absolute_uri('/usuario/solicitacoes/')}
                    """

                    send_email_from_user(
                        user=request.user,  # Admin logado envia
                        subject=subject,
                        message=message,
                        # Usuário recebe
                        recipient_list=[solicitacao.usuario.email],
                        fail_silently=True
                    )
            except Exception as e:
                print(f"Erro ao enviar email: {e}")

            return redirect('admin_solicitacoes')

        contexto = {
            'sidebar_links': get_sidebar_links(request.user),
            'solicitacao': solicitacao,
        }
        return render(request, 'pages/admin/processar_solicitacao.html', contexto)

    except SolicitacaoProduto.DoesNotExist:
        messages.error(request, 'Solicitação não encontrada.')
        return redirect('admin_solicitacoes')


def get_sidebar_links(user):
    role = getattr(user.profile, 'role', None)
    if role == 'ADMIN':        return [
            {'url': '/administrador/painel/', 'label': 'Painel Administrador'},
            {'url': '/administrador/usuarios/', 'label': 'Gerenciar Usuários'},
            {'url': '/administrador/produtos/', 'label': 'Gerenciar Produtos'},
            {'url': '/administrador/fornecedores/', 'label': 'Gerenciar Fornecedores'},
            {'url': '/administrador/solicitacoes/',
                'label': 'Solicitações de Produtos'},
        ]
    elif role == 'USUARIO':
        return [
            {'url': '/usuario/painel/', 'label': 'Dashboard'},
            {'url': '/usuario/perfil/', 'label': 'Perfil'},
            {'url': '/usuario/estoques/', 'label': 'Estoques'},
            {'url': '/usuario/solicitacoes/', 'label': 'Minhas Solicitações'},
        ]
    return []
