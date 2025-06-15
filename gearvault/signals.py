from django.db.models.signals import post_save
from django.dispatch import receiver
from gearvault.models import ItemCompra, Estoque, LocalArmazenamento, LoteEstoque
from django.db import transaction

@receiver(post_save, sender=ItemCompra)
def criar_lote_para_item_compra(sender, instance, created, **kwargs):
    if not created:
        return
    # Só cria lote se o item_compra ainda não tem lote
    if hasattr(instance, 'lotes_estoque') and instance.lotes_estoque.exists():
        return
    # Por padrão, usar o primeiro local de armazenamento
    local = None
    if hasattr(instance.compra, 'localarmazenamento'):
        local = instance.compra.localarmazenamento
    else:
        local = LocalArmazenamento.objects.first()
    if not local:
        return  # Não há local cadastrado
    # Cria o lote
    lote = LoteEstoque.objects.create(item_compra=instance)
    # Cria o estoque vinculado ao lote
    Estoque.objects.create(lote=lote, local=local)
