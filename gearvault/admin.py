from django.contrib import admin
from .models import Fornecedor, Comprador, LocalArmazenamento, Produto, Compra, ItemCompra, Estoque, Endereco, LoteEstoque


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


@admin.register(LocalArmazenamento)
class LocalArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "fornecedor", "imagem")
    search_fields = ("nome", "codigo" )
    list_filter = ("fornecedor",)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "fornecedor",
                    "comprador", "valor_total")
    search_fields = ("id", "fornecedor__nome", "comprador__user__username")
    list_filter = ("fornecedor",)
    date_hierarchy = "data"


@admin.register(ItemCompra)
class ItemCompraAdmin(admin.ModelAdmin):
    list_display = ("compra", "produto", "quantidade", "valor_unitario")
    search_fields = ("produto__nome", "compra__id")


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ("lote_display", "produto_display", "local", "quantidade", "valor_total_display")
    list_filter = ("local",)
    search_fields = ("lote__item_compra__produto__nome",)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "lote":
    #         from .models import Estoque, LoteEstoque
    #         usados = Estoque.objects.values_list("lote_id", flat=True)
    #         kwargs["queryset"] = LoteEstoque.objects.exclude(id__in=usados)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def lote_display(self, obj):
        return f"Lote {obj.lote.id}" if obj.lote else "-"
    lote_display.short_description = "Lote"

    def produto_display(self, obj):
        return obj.lote.item_compra.produto.nome if obj.lote and obj.lote.item_compra else "-"
    produto_display.short_description = "Produto"

    def valor_total_display(self, obj):
        if obj.lote and obj.lote.item_compra:
            return f"R$ {obj.quantidade * float(obj.lote.item_compra.valor_unitario):,.2f}"
        return "-"
    valor_total_display.short_description = "Valor Item no Estoque"


@admin.register(LoteEstoque)
class LoteEstoqueAdmin(admin.ModelAdmin):
    list_display = ("estoque", "item_compra", "data_entrada", "compra_id")
    search_fields = ("estoque__produto__nome", "item_compra__produto__nome", "item_compra__compra__id")
    list_filter = ("estoque__local",)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "item_compra":
    #         from .models import LoteEstoque, ItemCompra
    #         usados = LoteEstoque.objects.values_list("item_compra_id", flat=True)
    #         kwargs["queryset"] = ItemCompra.objects.exclude(id__in=usados)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def compra_id(self, obj):
        return obj.item_compra.compra.id
    compra_id.short_description = "ID da Compra"
