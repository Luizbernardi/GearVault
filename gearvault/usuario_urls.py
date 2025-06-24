from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.usuario_painel, name='usuario_painel'),
    path('perfil/', views.usuario_perfil, name='usuario_perfil'),
    path('estoques/', views.usuario_estoques, name='usuario_estoques'),
    path('estoques/<int:estoque_id>/', views.usuario_estoque_detalhes,
         name='usuario_estoque_detalhes'),
    path('estoques/<int:estoque_id>/locais/',
         views.usuario_estoque_locais, name='usuario_estoque_locais'),
    # Solicitações de produtos
    path('solicitacoes/', views.usuario_minhas_solicitacoes,
         name='usuario_minhas_solicitacoes'),
    path('solicitar/<int:local_id>/<int:produto_id>/',
         views.usuario_solicitar_produto, name='usuario_solicitar_produto'),
]
