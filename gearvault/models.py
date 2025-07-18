from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator

# Endereço (padrão Brasil)


class Endereco(models.Model):
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=8)

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.bairro}, {self.cidade} - {self.estado}, {self.cep}"

# Fornecedor

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(  max_length=14, validators=[
        MinLengthValidator(14),
            MaxLengthValidator(14)
        ], blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    telefone = models.CharField(max_length=11,  validators=[
            MinLengthValidator(11), 
            MaxLengthValidator(11)
        ], blank=False, null=False)
    endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, blank=False, null=True)

    def __str__(self):
        return self.nome

# Comprador (relacionado ao usuário do sistema)


class Comprador(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Estoque


class Estoque(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

# Local de Armazenamento


class LocalArmazenamento(models.Model):
    estoque = models.ForeignKey(Estoque, on_delete=models.CASCADE, related_name='locais')
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.nome} ({self.estoque.nome})'

# Produto (Componente)


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    codigo = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    fornecedores = models.ManyToManyField(
        Fornecedor, blank=True, related_name='produtos')
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

class Compra(models.Model):
    estoque = models.ForeignKey('Estoque', on_delete=models.PROTECT, related_name='compras')
    data = models.DateField(auto_now_add=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)
    comprador = models.ForeignKey(Comprador, on_delete=models.PROTECT)
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)

    @property
    def valor_total(self):
        return sum(item.quantidade * item.valor_unitario for item in self.itens.all())

    def __str__(self):
        return f"Compra #{self.id} - {self.fornecedor.nome} ({self.estoque.nome})"

# Itens da Compra


class ItemCompra(models.Model):
    compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    local = models.ForeignKey(LocalArmazenamento, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return f"{self.produto.nome} x {self.quantidade} em {self.local.nome}"

    class Meta:
        # Impede edição direta via admin, se necessário
        managed = True
        verbose_name = 'Item da Compra'
        verbose_name_plural = 'Itens da Compra'

# Solicitação de Produto


class SolicitacaoProduto(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
    ]

    usuario = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='solicitacoes')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    local = models.ForeignKey(LocalArmazenamento, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    justificativa = models.TextField(
        help_text="Justificativa para a solicitação")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    resposta_admin = models.TextField(
        blank=True, null=True, help_text="Resposta do administrador")
    admin_responsavel = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_processadas'
    )

    class Meta:
        ordering = ['-data_solicitacao']
        verbose_name = 'Solicitação de Produto'
        verbose_name_plural = 'Solicitações de Produtos'

    def __str__(self):
        return f"Solicitação #{self.id} - {self.produto.nome} ({self.quantidade}) - {self.status}"
