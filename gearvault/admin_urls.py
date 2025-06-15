from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.admin_painel, name='admin_painel'),
]