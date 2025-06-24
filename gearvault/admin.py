from django.contrib import admin
from .models import Fornecedor, Comprador, LocalArmazenamento, Produto, Compra, ItemCompra, Estoque, Endereco, SolicitacaoProduto, SolicitacaoProduto


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cnpj", "email", "telefone")
    search_fields = ("nome", "cnpj")
    
@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ("logradouro", "numero", "complemento", "bairro", "cidade", "estado", "cep")
    search_fields = ("bairro", "numero")

@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username",)


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)

@admin.register(LocalArmazenamento)
class LocalArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "estoque", "descricao")
    search_fields = ("nome", "estoque__nome")
    list_filter = ("estoque",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "fornecedor", "imagem")
    search_fields = ("nome", "codigo" )
    list_filter = ("fornecedor",)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("id", "estoque", "data", "fornecedor",
                    "comprador", "valor_total")
    search_fields = ("id", "fornecedor__nome", "comprador__user__username", "estoque__nome")
    list_filter = ("fornecedor", "estoque")
    date_hierarchy = "data"


@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = ("compra", "produto", "local", "quantidade", "valor_unitario")
    search_fields = ("produto__nome", "compra__id", "local__nome")
    list_filter = ("local",)


@admin.register(SolicitacaoProduto)
class SolicitacaoProdutoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "produto", "local",
                    "quantidade", "status", "data_solicitacao")
    search_fields = ("usuario__username", "produto__nome", "local__nome")
    list_filter = ("status", "data_solicitacao")
    date_hierarchy = "data_solicitacao"
    readonly_fields = ("data_solicitacao", "data_resposta")

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'PENDENTE':
            return self.readonly_fields + ("status", "resposta_admin", "admin_responsavel")
        return self.readonly_fields
