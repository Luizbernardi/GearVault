from django import template
from django.db.models import Sum
from gearvault.models import ItemCompra

register = template.Library()

@register.simple_tag
def quantidade_disponivel(local, produto):
    """Retorna a quantidade disponível de um produto em um local específico"""
    total = ItemCompra.objects.filter(
        local=local, produto=produto
    ).aggregate(total=Sum('quantidade'))['total']
    return total or 0
