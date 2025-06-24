from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.usuario_painel, name='usuario_painel'),
    path('perfil/', views.usuario_perfil, name='usuario_perfil'),
    path('estoques/', views.usuario_estoques, name='usuario_estoques'),
    path('estoques/<int:estoque_id>/locais/',
         views.usuario_estoque_locais, name='usuario_estoque_locais'),
    path('compras/', views.usuario_compras, name='usuario_compras'),
    path('compras/nova/', views.usuario_compra_add, name='usuario_compra_add'),
    path('compras/<int:compra_id>/detalhes/',
         views.usuario_compra_detalhes, name='usuario_compra_detalhes'),
]
