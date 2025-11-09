from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from decimal import Decimal

from contas.models import Profile
from .models import (
    Estoque,
    LocalArmazenamento,
    Fornecedor,
    Produto,
    Comprador,
    Compra,
    ItemCompra,
    Endereco,
    SolicitacaoProduto,
)


class BaseTestCase(TestCase):
    """Base class com setup comum para todos os testes."""

    def setUp(self):
        # Usuários
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='pass',
            email='admin@test.com',
            first_name='Admin',
            last_name='User'
        )
        # Signal may auto-create Profile on User creation, update role if exists
        admin_profile = getattr(self.admin_user, 'profile', None)
        if admin_profile:
            admin_profile.role = 'ADMIN'
            admin_profile.save()
        else:
            Profile.objects.create(user=self.admin_user, role='ADMIN')

        self.user = User.objects.create_user(
            username='user', 
            password='pass',
            email='user@test.com',
            first_name='Regular',
            last_name='User'
        )
        user_profile = getattr(self.user, 'profile', None)
        if user_profile:
            user_profile.role = 'USUARIO'
            user_profile.save()
        else:
            Profile.objects.create(user=self.user, role='USUARIO')

        # Endereço
        self.endereco = Endereco.objects.create(
            logradouro='Rua Teste',
            numero='123',
            bairro='Centro',
            cidade='São Paulo',
            estado='SP',
            cep='01234567'
        )

        # Fornecedor
        self.fornecedor = Fornecedor.objects.create(
            nome='Fornecedor Teste',
            cnpj='12345678000190',
            email='fornecedor@test.com',
            telefone='11999999999',
            endereco=self.endereco,
        )

        # Estoque e Local
        self.estoque = Estoque.objects.create(
            nome='Estoque Principal',
            descricao='Estoque de teste'
        )
        self.local = LocalArmazenamento.objects.create(
            estoque=self.estoque, 
            nome='Prateleira A1',
            descricao='Local de teste'
        )

        # Produtos
        self.produto1 = Produto.objects.create(
            nome='Resistor 10K',
            codigo='RES-10K-0805',
            categoria='Resistores',
            descricao='Resistor SMD 10K 0805'
        )
        self.produto2 = Produto.objects.create(
            nome='Capacitor 100nF',
            codigo='CAP-100N-0805',
            categoria='Capacitores'
        )

        # Comprador
        self.comprador = Comprador.objects.create(user=self.user)

        # Compra com itens
        self.compra = Compra.objects.create(
            estoque=self.estoque,
            fornecedor=self.fornecedor,
            comprador=self.comprador
        )
        self.item_compra = ItemCompra.objects.create(
            compra=self.compra,
            produto=self.produto1,
            local=self.local,
            quantidade=100,
            valor_unitario=Decimal('0.50'),
        )

        # Solicitação
        self.solicitacao = SolicitacaoProduto.objects.create(
            usuario=self.user,
            produto=self.produto1,
            local=self.local,
            quantidade=10,
            justificativa='Necessário para projeto X',
            status='PENDENTE'
        )

        self.client = Client()


# ========== TESTES ADMIN ==========

class AdminPainelTests(BaseTestCase):
    """Testes para o painel administrativo."""

    def test_admin_painel_requires_admin_role(self):
        """Apenas admins podem acessar o painel admin."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('admin_painel'))
        self.assertEqual(resp.status_code, 302)  # Redirect

    def test_admin_painel_accessible_by_admin(self):
        """Admin pode acessar o painel."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_painel'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Painel')


class AdminUsuariosTests(BaseTestCase):
    """Testes para gestão de usuários."""

    def test_admin_usuarios_list_accessible(self):
        """Admin pode listar usuários."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_usuarios_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'admin')
        self.assertContains(resp, 'user')

    def test_admin_usuarios_requires_admin(self):
        """Usuário comum não pode acessar lista de usuários."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('admin_usuarios_list'))
        self.assertEqual(resp.status_code, 302)


class AdminFornecedoresTests(BaseTestCase):
    """Testes para gestão de fornecedores."""

    def test_admin_fornecedor_list_accessible(self):
        """Admin pode listar fornecedores."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_fornecedor_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Fornecedor Teste')

    def test_admin_fornecedor_create(self):
        """Admin pode criar fornecedor."""
        self.client.login(username='admin', password='pass')
        data = {
            'add-fornecedor': '',
            'add-nome': 'Novo Fornecedor',
            'add-cnpj': '98765432000199',
            'add-email': 'novo@test.com',
            'add-telefone': '11988888888',
            'add-logradouro': 'Rua Nova',
            'add-numero': '456',
            'add-bairro': 'Bairro',
            'add-cidade': 'Rio',
            'add-estado': 'RJ',
            'add-cep': '20000000'
        }
        resp = self.client.post(reverse('admin_fornecedor_list'), data)
        self.assertEqual(resp.status_code, 302)  # Redirect após sucesso
        self.assertTrue(Fornecedor.objects.filter(nome='Novo Fornecedor').exists())


class AdminProdutosTests(BaseTestCase):
    """Testes para gestão de produtos."""

    def test_admin_produto_list_accessible(self):
        """Admin pode listar produtos."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_produto_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'RES-10K-0805')
        self.assertContains(resp, 'CAP-100N-0805')

    def test_admin_produto_create(self):
        """Admin pode criar produto."""
        self.client.login(username='admin', password='pass')
        data = {
            'add-produto': '',
            'add-nome': 'LED Vermelho',
            'add-codigo': 'LED-RED-5MM',
            'add-categoria': 'LEDs',
            'add-descricao': 'LED vermelho 5mm'
        }
        resp = self.client.post(reverse('admin_produto_list'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Produto.objects.filter(codigo='LED-RED-5MM').exists())


class AdminEstoquesTests(BaseTestCase):
    """Testes para gestão de estoques."""

    def test_admin_estoque_list_accessible(self):
        """Admin pode listar estoques."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_estoque_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Estoque Principal')

    def test_admin_estoque_detalhes_accessible(self):
        """Admin pode ver detalhes do estoque."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_estoque_detalhes', args=[self.estoque.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Estoque Principal')

    def test_admin_estoque_create(self):
        """Admin pode criar estoque."""
        self.client.login(username='admin', password='pass')
        data = {
            'add-estoque': '',
            'add-nome': 'Estoque Secundário',
            'add-descricao': 'Estoque de backup'
        }
        resp = self.client.post(reverse('admin_estoque_list'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Estoque.objects.filter(nome='Estoque Secundário').exists())


class AdminLocaisTests(BaseTestCase):
    """Testes para gestão de locais de armazenamento."""

    def test_admin_local_list_accessible(self):
        """Admin pode listar locais."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_local_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Prateleira A1')

    def test_admin_local_create(self):
        """Admin pode criar local."""
        self.client.login(username='admin', password='pass')
        data = {
            'add-local': '',
            'add-estoque': self.estoque.id,
            'add-nome': 'Prateleira B2',
            'add-descricao': 'Segunda prateleira'
        }
        resp = self.client.post(reverse('admin_local_list'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(LocalArmazenamento.objects.filter(nome='Prateleira B2').exists())


class AdminCompradoresTests(BaseTestCase):
    """Testes para gestão de compradores."""

    def test_admin_comprador_list_accessible(self):
        """Admin pode listar compradores."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_comprador_list'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_comprador_compras_accessible(self):
        """Admin pode ver compras de um comprador."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_comprador_compras', args=[self.comprador.id]))
        self.assertEqual(resp.status_code, 200)


class AdminComprasTests(BaseTestCase):
    """Testes para gestão de compras."""

    def test_admin_compra_list_accessible_by_admin(self):
        """Admin pode acessar lista de compras."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_compra_list'))
        self.assertEqual(resp.status_code, 200)

    def test_admin_compra_list_forbidden_for_non_admin(self):
        """Usuário comum não pode acessar lista de compras."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('admin_compra_list'))
        self.assertIn(resp.status_code, (302, 301))

    def test_admin_compra_detalhes_ajax_returns_items(self):
        """AJAX retorna itens da compra corretamente."""
        self.client.login(username='admin', password='pass')
        url = reverse('admin_compra_detalhes_ajax', args=[self.compra.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(len(data.get('itens', [])), 1)
        item = data['itens'][0]
        self.assertEqual(item['produto_id'], self.produto1.id)
        self.assertEqual(item['quantidade'], 100)

    def test_admin_compra_create(self):
        """Admin pode criar compra com itens."""
        self.client.login(username='admin', password='pass')
        data = {
            'add-compra': '',
            'add-estoque': self.estoque.id,
            'add-fornecedor': self.fornecedor.id,
            'add-comprador': self.comprador.id,
            'produto_id[]': [self.produto2.id],
            'local_id[]': [self.local.id],
            'quantidade[]': ['50'],
            'valor_unitario[]': ['0.75']
        }
        resp = self.client.post(reverse('admin_compra_list'), data)
        self.assertEqual(resp.status_code, 302)
        # Verifica se criou nova compra
        self.assertEqual(Compra.objects.count(), 2)


class AdminSolicitacoesTests(BaseTestCase):
    """Testes para gestão de solicitações."""

    def test_admin_solicitacoes_list_accessible(self):
        """Admin pode listar solicitações."""
        self.client.login(username='admin', password='pass')
        resp = self.client.get(reverse('admin_solicitacoes'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'projeto X')

    def test_admin_processar_solicitacao_aprovar(self):
        """Admin pode aprovar solicitação."""
        self.client.login(username='admin', password='pass')
        data = {
            'acao': 'aprovar',
            'resposta': 'Aprovado para uso no projeto'
        }
        url = reverse('admin_processar_solicitacao', args=[self.solicitacao.id])
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.solicitacao.refresh_from_db()
        self.assertEqual(self.solicitacao.status, 'APROVADA')

    def test_admin_processar_solicitacao_rejeitar(self):
        """Admin pode rejeitar solicitação."""
        self.client.login(username='admin', password='pass')
        data = {
            'acao': 'rejeitar',
            'resposta': 'Estoque insuficiente'
        }
        url = reverse('admin_processar_solicitacao', args=[self.solicitacao.id])
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.solicitacao.refresh_from_db()
        self.assertEqual(self.solicitacao.status, 'REJEITADA')


# ========== TESTES USER ==========

class UserPainelTests(BaseTestCase):
    """Testes para painel do usuário."""

    def test_usuario_painel_requires_login(self):
        """Painel requer login."""
        resp = self.client.get(reverse('usuario_painel'))
        self.assertIn(resp.status_code, (302, 301))

    def test_usuario_painel_accessible_by_user(self):
        """Usuário logado pode acessar painel."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('usuario_painel'))
        self.assertEqual(resp.status_code, 200)


class UserPerfilTests(BaseTestCase):
    """Testes para perfil do usuário."""

    def test_usuario_perfil_accessible(self):
        """Usuário pode acessar seu perfil."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('usuario_perfil'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'user@test.com')


class UserEstoquesTests(BaseTestCase):
    """Testes para visualização de estoques."""

    def test_usuario_estoques_requires_login(self):
        """Lista de estoques requer login."""
        resp = self.client.get(reverse('usuario_estoques'))
        self.assertIn(resp.status_code, (302, 301))

    def test_usuario_estoques_accessible_by_user(self):
        """Usuário pode ver lista de estoques."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('usuario_estoques'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Estoque Principal')

    def test_usuario_estoque_detalhes_accessible(self):
        """Usuário pode ver detalhes do estoque."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('usuario_estoque_detalhes', args=[self.estoque.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Prateleira A1')


class UserSolicitacoesTests(BaseTestCase):
    """Testes para solicitações de produtos."""

    def test_usuario_minhas_solicitacoes_accessible(self):
        """Usuário pode ver suas solicitações."""
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('usuario_minhas_solicitacoes'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'projeto X')

    def test_usuario_solicitar_produto_accessible(self):
        """Usuário pode acessar formulário de solicitação."""
        self.client.login(username='user', password='pass')
        url = reverse('usuario_solicitar_produto', args=[self.local.id, self.produto1.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Resistor 10K')

    def test_usuario_solicitar_produto_create(self):
        """Usuário pode criar solicitação."""
        self.client.login(username='user', password='pass')
        # Usa produto1 que tem 100 unidades em estoque
        url = reverse('usuario_solicitar_produto', args=[self.local.id, self.produto1.id])
        data = {
            'quantidade': '20',
            'justificativa': 'Necessário para protótipo'
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        # Verifica se criou nova solicitação (existem 2: a do setUp + a nova)
        self.assertEqual(SolicitacaoProduto.objects.filter(
            usuario=self.user,
            produto=self.produto1
        ).count(), 2)
