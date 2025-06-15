from django.db import models
from django.contrib.auth import get_user_model

# Fornecedor


class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome

# Comprador (relacionado ao usuário do sistema)


class Comprador(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    departamento = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Local de Armazenamento


class LocalArmazenamento(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

# Produto (Componente)


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    fornecedor = models.ForeignKey(
        Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

# Compra (Aquisição)


class Compra(models.Model):
    data = models.DateField(auto_now_add=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)
    comprador = models.ForeignKey(Comprador, on_delete=models.PROTECT)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)
    status = models.CharField(max_length=50, default='Pendente')

    def __str__(self):
        return f"Compra #{self.id} - {self.fornecedor.nome}"

# Itens da Compra


class ItemCompra(models.Model):
    compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produto.nome} x {self.quantidade}"

# Estoque multi-localização


class Estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    local = models.ForeignKey(LocalArmazenamento, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('produto', 'local')

    def __str__(self):
        return f"{self.produto.nome} em {self.local.nome}: {self.quantidade}"
