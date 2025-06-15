from django.contrib import admin
from .models import Fornecedor, Comprador, LocalArmazenamento, Produto, Compra, ItemCompra, Estoque


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "email", "telefone")
    search_fields = ("nome", "cnpj")


@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ("user", "departamento")
    search_fields = ("user__username", "departamento")


@admin.register(LocalArmazenamento)
class LocalArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "fornecedor")
    search_fields = ("nome", "codigo")
    list_filter = ("fornecedor",)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "fornecedor",
                    "comprador", "valor_total", "status")
    search_fields = ("id", "fornecedor__nome", "comprador__user__username")
    list_filter = ("status", "fornecedor")
    date_hierarchy = "data"


@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = ("compra", "produto", "quantidade", "valor_unitario")
    search_fields = ("produto__nome", "compra__id")


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ("produto", "local", "quantidade")
    list_filter = ("local",)
    search_fields = ("produto__nome",)
