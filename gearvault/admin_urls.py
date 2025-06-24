from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.admin_painel, name='admin_painel'),
    path('usuarios/', views.admin_usuarios_list, name='admin_usuarios_list'),
    path('fornecedores/', views.admin_fornecedor_list, name='admin_fornecedor_list'),
    path('produtos/', views.admin_produto_list, name='admin_produto_list'),
]