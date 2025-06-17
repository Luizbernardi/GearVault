from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.usuario_painel, name='usuario_painel'),
    path('perfil/', views.usuario_perfil, name='usuario_perfil'),
]
