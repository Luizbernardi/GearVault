from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.admin_painel, name='admin_painel'),
    path('usuarios/', views.admin_usuarios_list, name='admin_usuarios_list'),
    path('produtos/adicionar/', views.admin_produto_add, name='admin_produto_add'),
    path('fornecedores/adicionar/', views.admin_fornecedor_add,
         name='admin_fornecedor_add'),
]