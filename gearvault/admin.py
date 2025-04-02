from django.contrib import admin

# Register your models here.
from .models import Produto


@admin.register(Produto)
class AdminProduto(admin.ModelAdmin):
    list_display = ('nome',)
    list_filter = ('nome',)
