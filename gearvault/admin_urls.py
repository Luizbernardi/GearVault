from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.admin_painel, name='admin_painel'),
    path('usuarios/', views.admin_usuarios_list, name='admin_usuarios_list'),
    path('fornecedores/', views.admin_fornecedor_list, name='admin_fornecedor_list'),
    path('produtos/', views.admin_produto_list, name='admin_produto_list'),
    path('estoques/', views.admin_estoque_list, name='admin_estoque_list'),
    path('locais/', views.admin_local_list, name='admin_local_list'),
    path('compradores/', views.admin_comprador_list, name='admin_comprador_list'),
    path('compras/', views.admin_compra_list, name='admin_compra_list'),
    path('compras/<int:compra_id>/detalhes/', views.admin_compra_detalhes, name='admin_compra_detalhes'),
    # Solicitações de produtos
    path('solicitacoes/', views.admin_solicitacoes, name='admin_solicitacoes'),
    path('solicitacoes/<int:solicitacao_id>/processar/',
         views.admin_processar_solicitacao, name='admin_processar_solicitacao'),
]