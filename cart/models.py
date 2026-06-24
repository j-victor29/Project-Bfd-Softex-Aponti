from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Carrinho(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='carrinhos'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aberto'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        return f"Carrinho {self.id} ({self.status}) - {self.usuario.email}"

    @property
    def total(self):
        return sum((item.subtotal for item in self.itens.all()), Decimal('0.00'))


class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(
        Carrinho,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    personalizacao = models.ForeignKey(
        'creations.Personalizacao',
        on_delete=models.CASCADE,
        related_name='itens_carrinho'
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        editable=False
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(self.quantidade) * self.preco_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item {self.id} in Cart {self.carrinho.id} - Qty: {self.quantidade}"
