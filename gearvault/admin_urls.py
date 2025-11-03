from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.admin_painel, name='admin_painel'),
    path('usuarios/', views.admin_usuarios_list, name='admin_usuarios_list'),
    path('fornecedores/', views.admin_fornecedor_list, name='admin_fornecedor_list'),
    path('produtos/', views.admin_produto_list, name='admin_produto_list'),
    path('estoques/', views.admin_estoque_list, name='admin_estoque_list'),
    path('estoques/<int:estoque_id>/', views.admin_estoque_detalhes, name='admin_estoque_detalhes'),
    path('locais/', views.admin_local_list, name='admin_local_list'),
    path('compradores/', views.admin_comprador_list, name='admin_comprador_list'),
    path('compradores/<int:comprador_id>/compras/', views.admin_comprador_compras, name='admin_comprador_compras'),
    path('compras/', views.admin_compra_list, name='admin_compra_list'),
    path('compras/process-invoice/', views.admin_process_invoice, name='admin_process_invoice'),
    path('compras/<int:compra_id>/detalhes-ajax/', views.admin_compra_detalhes_ajax, name='admin_compra_detalhes_ajax'),
    path('compras/<int:compra_id>/detalhes/', views.admin_compra_detalhes, name='admin_compra_detalhes'),
    path('compras/<int:compra_id>/', views.admin_compra_detalhes_pagina, name='admin_compra_detalhes_pagina'),
    # Solicitações de produtos
    path('solicitacoes/', views.admin_solicitacoes, name='admin_solicitacoes'),
    path('solicitacoes/<int:solicitacao_id>/processar/',
         views.admin_processar_solicitacao, name='admin_processar_solicitacao'),
]