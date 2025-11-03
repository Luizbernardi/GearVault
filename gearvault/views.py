from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Fornecedor, Compra, ItemCompra, Estoque, LocalArmazenamento, Endereco, Comprador
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, FloatField, Count
from django.contrib.auth.models import User
from contas.models import Profile
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


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
    compras = Compra.objects.all().order_by('-data')
    estoques = Estoque.objects.prefetch_related('locais', 'compras')
    fornecedores = Fornecedor.objects.all()
    movimentacoes = ItemCompra.objects.select_related(
        'produto', 'local', 'compra', 'compra__estoque').order_by('-id')[:5]
    
    # Buscar solicitações pendentes para administradores
    from .models import SolicitacaoProduto
    solicitacoes_pendentes = SolicitacaoProduto.objects.filter(
        status='PENDENTE'
    ).select_related('produto', 'local', 'usuario').order_by('-data_solicitacao')[:5]

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
        'solicitacoes_pendentes': solicitacoes_pendentes,
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
        print("=== DEBUG FORNECEDOR ===")
        print("POST data:", request.POST)
        
        nome = request.POST.get('add-nome')
        cnpj = request.POST.get('add-cnpj')
        email = request.POST.get('add-email')
        telefone = request.POST.get('add-telefone')
        
        print(f"Dados fornecedor: nome={nome}, cnpj={cnpj}, email={email}, telefone={telefone}")
        
        # Verificar se foi selecionado um endereço existente ou se criará um novo
        endereco_existente_id = request.POST.get('add-endereco-existente')
        
        # Campos do novo endereço
        logradouro = request.POST.get('add-logradouro')
        numero = request.POST.get('add-numero')
        bairro = request.POST.get('add-bairro')
        cidade = request.POST.get('add-cidade')
        estado = request.POST.get('add-estado')
        cep = request.POST.get('add-cep')
        complemento = request.POST.get('add-complemento', '')

        print(f"Endereco existente ID: {endereco_existente_id}")
        print(f"Dados endereco novo: logradouro={logradouro}, numero={numero}, bairro={bairro}, cidade={cidade}, estado={estado}, cep={cep}")

        endereco = None
        
        # Se foi selecionado um endereço existente
        if endereco_existente_id:
            endereco = Endereco.objects.filter(id=endereco_existente_id).first()
            print(f"Endereco encontrado: {endereco}")
        # Se foram preenchidos campos para novo endereço
        elif logradouro and numero and bairro and cidade and estado and cep:
            try:
                # Remove formatação do CEP se houver
                cep_limpo = cep.replace('-', '').replace(' ', '') if cep else ''
                
                endereco = Endereco.objects.create(
                    logradouro=logradouro,
                    numero=numero,
                    bairro=bairro,
                    cidade=cidade,
                    estado=estado,
                    cep=cep_limpo,
                    complemento=complemento
                )
                print(f"Endereco criado: {endereco}")
            except Exception as e:
                print(f"Erro ao criar endereco: {e}")
                messages.error(request, f'Erro ao criar endereço: {str(e)}')
                return redirect('admin_fornecedor_list')

        print(f"Endereco final: {endereco}")
        print(f"Validacao: nome={bool(nome)}, cnpj={bool(cnpj)}, email={bool(email)}, telefone={bool(telefone)}, endereco={bool(endereco)}")

        if nome and cnpj and email and telefone:
            try:
                # Remove formatação do CNPJ e telefone se houver
                cnpj_limpo = cnpj.replace('.', '').replace('/', '').replace('-', '') if cnpj else ''
                telefone_limpo = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '') if telefone else ''
                
                fornecedor = Fornecedor.objects.create(
                    nome=nome,
                    cnpj=cnpj_limpo,
                    email=email,
                    telefone=telefone_limpo,
                    endereco=endereco
                )
                print(f"Fornecedor criado: {fornecedor}")
                messages.success(request, 'Fornecedor cadastrado com sucesso!')
            except Exception as e:
                print(f"Erro ao criar fornecedor: {e}")
                messages.error(request, f'Erro ao cadastrar fornecedor: {str(e)}')
        else:
            missing_fields = []
            if not nome: missing_fields.append('nome')
            if not cnpj: missing_fields.append('cnpj')
            if not email: missing_fields.append('email')
            if not telefone: missing_fields.append('telefone')
            
            print(f"Campos obrigatórios faltando: {missing_fields}")
            messages.error(request, f'Preencha todos os campos obrigatórios: {", ".join(missing_fields)}')
        return redirect('admin_fornecedor_list')

    # Edição de fornecedor
    if request.method == 'POST' and 'fornecedor_id' in request.POST and 'nome' in request.POST:
        fornecedor_id = request.POST.get('fornecedor_id')
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        
        # Verificar se foi selecionado um endereço existente
        endereco_existente_id = request.POST.get('edit-endereco-existente')
        
        # Campos do endereço
        logradouro = request.POST.get('logradouro')
        numero = request.POST.get('numero')
        bairro = request.POST.get('bairro')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')
        complemento = request.POST.get('complemento', '')

        try:
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            
            # Atualizar dados do fornecedor
            fornecedor.nome = nome
            fornecedor.cnpj = cnpj
            fornecedor.email = email
            fornecedor.telefone = telefone
            
            # Se foi selecionado um endereço existente diferente
            if endereco_existente_id:
                novo_endereco = Endereco.objects.filter(id=endereco_existente_id).first()
                if novo_endereco:
                    fornecedor.endereco = novo_endereco
            # Se foi editado o endereço atual
            elif logradouro and numero and bairro and cidade and estado and cep:
                if fornecedor.endereco:
                    # Atualizar endereço existente
                    endereco = fornecedor.endereco
                    endereco.logradouro = logradouro
                    endereco.numero = numero
                    endereco.bairro = bairro
                    endereco.cidade = cidade
                    endereco.estado = estado
                    endereco.cep = cep
                    endereco.complemento = complemento
                    endereco.save()
                else:
                    # Criar novo endereço se não existir
                    endereco = Endereco.objects.create(
                        logradouro=logradouro,
                        numero=numero,
                        bairro=bairro,
                        cidade=cidade,
                        estado=estado,
                        cep=cep,
                        complemento=complemento
                    )
                    fornecedor.endereco = endereco
            
            fornecedor.save()
            messages.success(request, 'Fornecedor editado com sucesso!')
        except Fornecedor.DoesNotExist:
            messages.error(request, 'Fornecedor não encontrado.')
        except Exception as e:
            messages.error(request, f'Erro ao editar fornecedor: {str(e)}')
        return redirect('admin_fornecedor_list')

    # Exclusão de fornecedor
    if request.method == 'POST' and 'fornecedor_id' in request.POST and 'delete-fornecedor-id' in request.POST:
        fornecedor_id = request.POST.get('fornecedor_id')
        try:
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            # Deletar o endereço associado se existir e não for usado por outros fornecedores
            if fornecedor.endereco:
                endereco = fornecedor.endereco
                # Verificar se o endereço é usado por outros fornecedores
                outros_fornecedores = Fornecedor.objects.filter(endereco=endereco).exclude(id=fornecedor.id)
                if not outros_fornecedores.exists():
                    endereco.delete()
            fornecedor.delete()
            messages.success(request, 'Fornecedor excluído com sucesso!')
        except Fornecedor.DoesNotExist:
            messages.error(request, 'Fornecedor não encontrado.')
        except Exception as e:
            messages.error(request, f'Erro ao excluir fornecedor: {str(e)}')
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
        imagem = request.FILES.get('add-imagem')
        descricao = request.POST.get('add-descricao')
        fornecedores_ids = request.POST.getlist('add-fornecedores')
        
        if nome and codigo:
            try:
                produto = Produto.objects.create(
                    nome=nome,
                    codigo=codigo,
                    categoria=categoria,
                    imagem=imagem,
                    descricao=descricao,
                )
                # Adiciona os fornecedores selecionados
                if fornecedores_ids:
                    produto.fornecedores.set(fornecedores_ids)
                messages.success(request, 'Produto cadastrado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar produto: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        return redirect('admin_produto_list')

    # Edição de produto
    if request.method == 'POST' and 'produto_id' in request.POST and 'nome' in request.POST and 'codigo' in request.POST:
        produto_id = request.POST.get('produto_id')
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        categoria = request.POST.get('categoria')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get('descricao')
        fornecedores_ids = request.POST.getlist('fornecedores')
        
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.nome = nome
            produto.codigo = codigo
            produto.categoria = categoria
            if imagem:
                produto.imagem = imagem
            produto.descricao = descricao
            produto.save()
            # Atualiza os fornecedores
            produto.fornecedores.set(fornecedores_ids)
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

    produtos = Produto.objects.all().prefetch_related('fornecedores').order_by('id')
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

    status_filter = request.GET.get('status', 'TODAS')
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


@login_required
def admin_compra_list(request):
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return redirect('login')

    per_page = int(request.GET.get('per_page', 10))

    # Adicionar compra
    if request.method == 'POST' and 'add-compra' in request.POST:
        estoque_id = request.POST.get('add-estoque')
        fornecedor_id = request.POST.get('add-fornecedor')
        comprador_id = request.POST.get('add-comprador')
        invoice = request.FILES.get('add-invoice')
        
        # Itens da compra
        produtos_ids = request.POST.getlist('produto_id[]')
        locais_ids = request.POST.getlist('local_id[]')
        quantidades = request.POST.getlist('quantidade[]')
        valores_unitarios = request.POST.getlist('valor_unitario[]')
        
        if estoque_id and fornecedor_id and comprador_id:
            try:
                with transaction.atomic():
                    # Buscar objetos
                    estoque = Estoque.objects.get(id=estoque_id)
                    fornecedor = Fornecedor.objects.get(id=fornecedor_id)
                    comprador = Comprador.objects.get(id=comprador_id)
                    
                    # Criar compra
                    compra = Compra.objects.create(
                        estoque=estoque,
                        fornecedor=fornecedor,
                        comprador=comprador,
                        invoice=invoice
                    )
                    
                    # Criar itens da compra
                    for i in range(len(produtos_ids)):
                        if produtos_ids[i] and locais_ids[i] and quantidades[i] and valores_unitarios[i]:
                            produto = Produto.objects.get(id=produtos_ids[i])
                            local = LocalArmazenamento.objects.get(id=locais_ids[i])
                            
                            ItemCompra.objects.create(
                                compra=compra,
                                produto=produto,
                                local=local,
                                quantidade=int(quantidades[i]),
                                valor_unitario=float(valores_unitarios[i])
                            )
                    
                    messages.success(request, 'Compra cadastrada com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar compra: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        return redirect('admin_compra_list')

    # Editar compra
    if request.method == 'POST' and 'edit-compra' in request.POST:
        compra_id = request.POST.get('compra_id')
        estoque_id = request.POST.get('edit-estoque')
        fornecedor_id = request.POST.get('edit-fornecedor')
        comprador_id = request.POST.get('edit-comprador')
        invoice = request.FILES.get('edit-invoice')
        
        try:
            compra = Compra.objects.get(id=compra_id)
            compra.estoque = Estoque.objects.get(id=estoque_id)
            compra.fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            compra.comprador = Comprador.objects.get(id=comprador_id)
            if invoice:
                compra.invoice = invoice
            compra.save()
            messages.success(request, 'Compra editada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao editar compra: {str(e)}')
        return redirect('admin_compra_list')

    # Excluir compra
    if request.method == 'POST' and 'delete-compra' in request.POST:
        compra_id = request.POST.get('compra_id')
        try:
            compra = Compra.objects.get(id=compra_id)
            compra.delete()
            messages.success(request, 'Compra excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir compra: {str(e)}')
        return redirect('admin_compra_list')

    # Listar compras
    compras = Compra.objects.select_related('estoque', 'fornecedor', 'comprador', 'comprador__user').prefetch_related('itens__produto', 'itens__local').order_by('-data')
    paginator = Paginator(compras, per_page)
    page_number = request.GET.get('page')
    compras_page = paginator.get_page(page_number)

    # Dados para os formulários
    estoques = Estoque.objects.all()
    fornecedores = Fornecedor.objects.all()
    compradores = Comprador.objects.select_related('user').all()
    produtos = Produto.objects.all()
    locais = LocalArmazenamento.objects.select_related('estoque').all()

    context = {
        'sidebar_links': get_sidebar_links(request.user),
        'compras': compras_page,
        'estoques': estoques,
        'fornecedores': fornecedores,
        'compradores': compradores,
        'produtos': produtos,
        'locais': locais,
    }
    
    return render(request, 'pages/admin/compra_list.html', context)


@login_required
def admin_compra_detalhes_ajax(request, compra_id):
    """
    View AJAX para buscar detalhes de uma compra (itens)
    """
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    try:
        compra = Compra.objects.prefetch_related('itens__produto', 'itens__local').get(id=compra_id)
        
        itens = []
        for item in compra.itens.all():
            itens.append({
                'produto_id': item.produto.id,
                'produto_nome': item.produto.nome,
                'produto_codigo': item.produto.codigo,
                'local_id': item.local.id,
                'local_nome': item.local.nome,
                'quantidade': item.quantidade,
                'valor_unitario': float(item.valor_unitario),
            })
        
        return JsonResponse({
            'success': True,
            'itens': itens
        })
    
    except Compra.DoesNotExist:
        return JsonResponse({'error': 'Compra não encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes da compra: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def admin_process_invoice(request):
    """
    View AJAX para processar invoice e extrair itens automaticamente
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return JsonResponse({'error': 'Não autorizado'}, status=403)
    
    invoice_file = request.FILES.get('invoice')
    if not invoice_file:
        return JsonResponse({'error': 'Nenhum arquivo enviado'}, status=400)
    
    # Verifica se é PDF
    if not invoice_file.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Apenas arquivos PDF são suportados'}, status=400)
    
    try:
        # Salva temporariamente o arquivo
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in invoice_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Processa a invoice
        from .invoice_processor import process_invoice_file, match_products_with_database
        
        invoice_data = process_invoice_file(temp_file_path)
        
        # Remove arquivo temporário
        os.unlink(temp_file_path)
        
        if not invoice_data or not invoice_data.get('itens'):
            return JsonResponse({
                'warning': 'Nenhum item foi identificado na invoice',
                'items': [],
                'invoice_info': {
                    'fornecedor_nome': invoice_data.get('fornecedor_nome'),
                    'fornecedor_cnpj': invoice_data.get('fornecedor_cnpj'),
                    'data_emissao': invoice_data.get('data_emissao'),
                    'numero_nf': invoice_data.get('numero_nf'),
                }
            })
        
        # Tenta fazer match com produtos no banco
        produtos_db = Produto.objects.all()
        matched_items = match_products_with_database(invoice_data['itens'], produtos_db)
        
        # Prepara resposta
        items_response = []
        for item in matched_items:
            items_response.append({
                'codigo': item['codigo'],
                'descricao': item['descricao'],
                'quantidade': item['quantidade'],
                'valor_unitario': float(item['valor_unitario']),
                'produto_id': item.get('produto_id'),
                'produto_nome': item.get('produto_nome'),
                'match_score': item.get('match_score', 0),
            })
        
        return JsonResponse({
            'success': True,
            'items': items_response,
            'invoice_info': {
                'fornecedor_nome': invoice_data.get('fornecedor_nome'),
                'fornecedor_cnpj': invoice_data.get('fornecedor_cnpj'),
                'data_emissao': invoice_data.get('data_emissao'),
                'numero_nf': invoice_data.get('numero_nf'),
            },
            'message': f'{len(items_response)} itens identificados na invoice'
        })
    
    except Exception as e:
        logger.error(f"Erro ao processar invoice: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Erro ao processar invoice: {str(e)}'
        }, status=500)


@login_required
def admin_estoque_list(request):
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return redirect('login')

    per_page = int(request.GET.get('per_page', 10))

    # Adicionar estoque
    if request.method == 'POST' and 'add-estoque' in request.POST:
        nome = request.POST.get('add-nome')
        descricao = request.POST.get('add-descricao')
        
        if nome:
            try:
                Estoque.objects.create(
                    nome=nome,
                    descricao=descricao
                )
                messages.success(request, 'Estoque cadastrado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar estoque: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        return redirect('admin_estoque_list')

    # Editar estoque
    if request.method == 'POST' and 'edit-estoque' in request.POST:
        estoque_id = request.POST.get('estoque_id')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        
        try:
            estoque = Estoque.objects.get(id=estoque_id)
            estoque.nome = nome
            estoque.descricao = descricao
            estoque.save()
            messages.success(request, 'Estoque editado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao editar estoque: {str(e)}')
        return redirect('admin_estoque_list')

    # Excluir estoque
    if request.method == 'POST' and 'delete-estoque' in request.POST:
        estoque_id = request.POST.get('estoque_id')
        try:
            estoque = Estoque.objects.get(id=estoque_id)
            estoque.delete()
            messages.success(request, 'Estoque excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir estoque: {str(e)}')
        return redirect('admin_estoque_list')

    # Listar estoques com estatísticas
    estoques = Estoque.objects.annotate(
        total_locais=Count('locais', distinct=True)
    ).order_by('nome')
    
    # Calcular total de itens para cada estoque
    for estoque in estoques:
        total_itens = ItemCompra.objects.filter(
            local__estoque=estoque
        ).aggregate(total=Sum('quantidade'))['total'] or 0
        estoque.total_itens = total_itens

    paginator = Paginator(estoques, per_page)
    page_number = request.GET.get('page')
    estoques_page = paginator.get_page(page_number)

    context = {
        'sidebar_links': get_sidebar_links(request.user),
        'estoques': estoques_page,
    }
    
    return render(request, 'pages/admin/estoque_list.html', context)


@login_required
def admin_estoque_detalhes(request, estoque_id):
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return redirect('login')
    
    try:
        estoque = get_object_or_404(Estoque, id=estoque_id)
    except:
        messages.error(request, 'Estoque não encontrado.')
        return redirect('admin_estoque_list')
    
    # Buscar locais de armazenamento
    locais = LocalArmazenamento.objects.filter(estoque=estoque).order_by('nome')
    
    # Buscar compras realizadas neste estoque
    compras = Compra.objects.filter(estoque=estoque).select_related('fornecedor', 'comprador').order_by('-data')[:10]
    
    # Calcular estatísticas do estoque
    total_compras = Compra.objects.filter(estoque=estoque).count()
    total_locais = locais.count()
    
    # Calcular total de itens no estoque
    total_itens = ItemCompra.objects.filter(
        local__estoque=estoque
    ).aggregate(total=Sum('quantidade'))['total'] or 0
    
    # Calcular valor total dos itens
    valor_total = ItemCompra.objects.filter(
        local__estoque=estoque
    ).aggregate(
        total=Sum(F('quantidade') * F('valor_unitario'))
    )['total'] or 0
    
    # Produtos mais comuns no estoque (top 5)
    produtos_populares = ItemCompra.objects.filter(
        local__estoque=estoque
    ).values('produto__nome', 'produto__codigo').annotate(
        total_quantidade=Sum('quantidade'),
        total_valor=Sum(F('quantidade') * F('valor_unitario'))
    ).order_by('-total_quantidade')[:5]
    
    # Fornecedores que mais vendem para este estoque (top 5)
    fornecedores_top = Compra.objects.filter(
        estoque=estoque
    ).values('fornecedor__nome').annotate(
        total_compras=Count('id')
    ).order_by('-total_compras')[:5]
    
    # Calcular valor total para cada fornecedor
    for fornecedor in fornecedores_top:
        compras_fornecedor = Compra.objects.filter(
            estoque=estoque,
            fornecedor__nome=fornecedor['fornecedor__nome']
        )
        valor_total_fornecedor = 0
        for compra in compras_fornecedor:
            valor_total_fornecedor += compra.valor_total
        fornecedor['valor_total'] = valor_total_fornecedor
    
    context = {
        'sidebar_links': get_sidebar_links(request.user),
        'estoque': estoque,
        'locais': locais,
        'compras': compras,
        'total_compras': total_compras,
        'total_locais': total_locais,
        'total_itens': total_itens,
        'valor_total': valor_total,
        'produtos_populares': produtos_populares,
        'fornecedores_top': fornecedores_top,
    }
    
    return render(request, 'pages/admin/estoque_detalhes.html', context)


@login_required
def admin_local_list(request):
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return redirect('login')

    per_page = int(request.GET.get('per_page', 10))

    # Adicionar local
    if request.method == 'POST' and 'add-local' in request.POST:
        nome = request.POST.get('add-nome')
        descricao = request.POST.get('add-descricao')
        estoque_id = request.POST.get('add-estoque')
        
        if nome and estoque_id:
            try:
                estoque = Estoque.objects.get(id=estoque_id)
                LocalArmazenamento.objects.create(
                    nome=nome,
                    descricao=descricao,
                    estoque=estoque
                )
                messages.success(request, 'Local de armazenamento cadastrado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar local: {str(e)}')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        return redirect('admin_local_list')

    # Editar local
    if request.method == 'POST' and 'edit-local' in request.POST:
        local_id = request.POST.get('local_id')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        estoque_id = request.POST.get('estoque')
        
        try:
            local = LocalArmazenamento.objects.get(id=local_id)
            estoque = Estoque.objects.get(id=estoque_id)
            local.nome = nome
            local.descricao = descricao
            local.estoque = estoque
            local.save()
            messages.success(request, 'Local editado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao editar local: {str(e)}')
        return redirect('admin_local_list')

    # Excluir local
    if request.method == 'POST' and 'delete-local' in request.POST:
        local_id = request.POST.get('local_id')
        try:
            local = LocalArmazenamento.objects.get(id=local_id)
            local.delete()
            messages.success(request, 'Local excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir local: {str(e)}')
        return redirect('admin_local_list')

    # Listar locais
    locais = LocalArmazenamento.objects.select_related('estoque').order_by('estoque__nome', 'nome')
    
    # Calcular total de itens para cada local
    for local in locais:
        total_itens = ItemCompra.objects.filter(
            local=local
        ).aggregate(total=Sum('quantidade'))['total'] or 0
        local.total_itens = total_itens

    paginator = Paginator(locais, per_page)
    page_number = request.GET.get('page')
    locais_page = paginator.get_page(page_number)

    # Dados para formulários
    estoques = Estoque.objects.all().order_by('nome')

    context = {
        'sidebar_links': get_sidebar_links(request.user),
        'locais': locais_page,
        'estoques': estoques,
    }
    
    return render(request, 'pages/admin/local_list.html', context)


@login_required
def admin_comprador_list(request):
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return redirect('login')

    per_page = int(request.GET.get('per_page', 10))

    # Adicionar comprador
    if request.method == 'POST' and 'add-comprador' in request.POST:
        user_id = request.POST.get('add-user')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Verificar se já existe um comprador para este usuário
                if not Comprador.objects.filter(user=user).exists():
                    Comprador.objects.create(user=user)
                    messages.success(request, 'Comprador cadastrado com sucesso!')
                else:
                    messages.error(request, 'Já existe um comprador vinculado a este usuário.')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar comprador: {str(e)}')
        else:
            messages.error(request, 'Selecione um usuário.')
        return redirect('admin_comprador_list')

    # Excluir comprador
    if request.method == 'POST' and 'delete-comprador' in request.POST:
        comprador_id = request.POST.get('comprador_id')
        try:
            comprador = Comprador.objects.get(id=comprador_id)
            comprador.delete()
            messages.success(request, 'Comprador excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir comprador: {str(e)}')
        return redirect('admin_comprador_list')

    # Listar compradores
    compradores = Comprador.objects.select_related('user').order_by('user__username')

    # Calcular estatísticas para cada comprador
    for comprador in compradores:
        total_compras = Compra.objects.filter(comprador=comprador).count()
        comprador.total_compras = total_compras

    paginator = Paginator(compradores, per_page)
    page_number = request.GET.get('page')
    compradores_page = paginator.get_page(page_number)

    # Usuários disponíveis (que não são compradores ainda)
    usuarios_comprador_ids = Comprador.objects.values_list('user_id', flat=True)
    usuarios_disponiveis = User.objects.exclude(id__in=usuarios_comprador_ids).order_by('username')

    context = {
        'sidebar_links': get_sidebar_links(request.user),
        'compradores': compradores_page,
        'usuarios_disponiveis': usuarios_disponiveis,
    }
    
    return render(request, 'pages/admin/comprador_list.html', context)


@login_required
def admin_compra_detalhes(request, compra_id):
    """API endpoint para buscar detalhes de uma compra específica via AJAX"""
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return JsonResponse({'success': False, 'error': 'Acesso negado'})
    
    try:
        compra = Compra.objects.select_related(
            'estoque', 'fornecedor', 'comprador', 'comprador__user'
        ).prefetch_related(
            'itens__produto', 'itens__local'
        ).get(id=compra_id)
        
        # Preparar dados dos itens
        itens_data = []
        for item in compra.itens.all():
            subtotal = item.quantidade * item.valor_unitario
            itens_data.append({
                'produto_nome': item.produto.nome,
                'produto_codigo': item.produto.codigo,
                'local_nome': item.local.nome,
                'quantidade': item.quantidade,
                'valor_unitario': float(item.valor_unitario),
                'subtotal': float(subtotal),
            })
        
        # Preparar dados da compra
        compra_data = {
            'id': compra.id,
            'data': compra.data.strftime('%d/%m/%Y'),
            'estoque': compra.estoque.nome,
            'fornecedor': {
                'nome': compra.fornecedor.nome,
                'cnpj': compra.fornecedor.cnpj,
                'email': compra.fornecedor.email,
                'telefone': compra.fornecedor.telefone,
            },
            'comprador': {
                'nome': compra.comprador.user.get_full_name() or compra.comprador.user.username,
                'email': compra.comprador.user.email,
            },
            'valor_total': float(compra.valor_total),
            'invoice_url': compra.invoice.url if compra.invoice else None,
            'total_itens': len(itens_data),
            'itens': itens_data,
        }
        
        return JsonResponse({
            'success': True,
            'compra': compra_data
        })
        
    except Compra.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Compra não encontrada'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def admin_compra_detalhes_pagina(request, compra_id):
    """Página HTML para exibir detalhes completos de uma compra"""
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return redirect('login')
    
    try:
        compra = Compra.objects.select_related(
            'estoque', 'fornecedor', 'fornecedor__endereco', 'comprador', 'comprador__user'
        ).prefetch_related(
            'itens__produto', 'itens__local'
        ).get(id=compra_id)
        
        context = {
            'sidebar_links': get_sidebar_links(request.user),
            'compra': compra,
        }
        
        return render(request, 'pages/admin/compra_detalhes.html', context)
        
    except Compra.DoesNotExist:
        messages.error(request, 'Compra não encontrada.')
        return redirect('admin_compra_list')


@login_required
def admin_comprador_compras(request, comprador_id):
    """API endpoint para buscar compras de um comprador específico via AJAX"""
    if not request.user.is_authenticated or getattr(request.user.profile, 'role', None) != 'ADMIN':
        return JsonResponse({'success': False, 'error': 'Acesso negado'})
    
    try:
        print(f"Buscando compras para comprador ID: {comprador_id}")
        comprador = Comprador.objects.select_related('user').get(id=comprador_id)
        print(f"Comprador encontrado: {comprador.user.username}")
        
        # Buscar compras do comprador
        compras = Compra.objects.filter(comprador=comprador).select_related(
            'estoque', 'fornecedor'
        ).prefetch_related('itens').order_by('-data')
        
        print(f"Compras encontradas: {compras.count()}")
        
        # Buscar estoques únicos das compras para o filtro
        estoques = Estoque.objects.filter(compras__comprador=comprador).distinct().order_by('nome')
        
        # Serializar dados das compras
        compras_data = []
        for compra in compras:
            compras_data.append({
                'id': compra.id,
                'data': compra.data.strftime('%Y-%m-%d'),
                'fornecedor': compra.fornecedor.nome,
                'estoque': compra.estoque.nome,
                'estoque_id': compra.estoque.id,
                'valor_total': float(compra.valor_total),
            })
        
        # Serializar dados dos estoques
        estoques_data = []
        for estoque in estoques:
            estoques_data.append({
                'id': estoque.id,
                'nome': estoque.nome,
            })
        
        response_data = {
            'success': True,
            'compras': compras_data,
            'estoques': estoques_data,
            'comprador_nome': comprador.user.get_full_name() or comprador.user.username
        }
        
        print(f"Retornando: {len(compras_data)} compras e {len(estoques_data)} estoques")
        return JsonResponse(response_data)
        
    except Comprador.DoesNotExist:
        print(f"Comprador não encontrado: {comprador_id}")
        return JsonResponse({'success': False, 'error': 'Comprador não encontrado'})
    except Exception as e:
        print(f"Erro: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


def get_sidebar_links(user):
    role = getattr(user.profile, 'role', None)
    if role == 'ADMIN':
        return [
            {'url': '/administrador/painel/', 'label': 'Painel Administrador'},
            {'url': '/administrador/usuarios/', 'label': 'Usuários'},
            {'url': '/administrador/solicitacoes/', 'label': 'Solicitações'},
            {'url': '/administrador/estoques/', 'label': 'Estoques'},
            {'url': '/administrador/locais/', 'label': 'Locais de Armazenamento'},
            {'url': '/administrador/fornecedores/', 'label': 'Fornecedores'},
            {'url': '/administrador/produtos/', 'label': 'Produtos'},
            {'url': '/administrador/compradores/', 'label': 'Compradores'},
            {'url': '/administrador/compras/', 'label': 'Compras'},
        ]
    elif role == 'USUARIO':
        return [
            {'url': '/usuario/painel/', 'label': 'Dashboard'},
            {'url': '/usuario/perfil/', 'label': 'Perfil'},
            {'url': '/usuario/estoques/', 'label': 'Estoques'},
            {'url': '/usuario/solicitacoes/', 'label': 'Minhas Solicitações'},
        ]
    return []
