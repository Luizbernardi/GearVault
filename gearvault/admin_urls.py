from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.admin_painel, name='admin_painel'),
    path('usuarios/', views.admin_usuarios_list, name='admin_usuarios_list'),
    path('fornecedores/', views.admin_fornecedor_list, name='admin_fornecedor_list'),
    path('produtos/', views.admin_produto_list, name='admin_produto_list'),
    # Solicitações de produtos
    path('solicitacoes/', views.admin_solicitacoes, name='admin_solicitacoes'),
    path('solicitacoes/<int:solicitacao_id>/processar/',
         views.admin_processar_solicitacao, name='admin_processar_solicitacao'),
]