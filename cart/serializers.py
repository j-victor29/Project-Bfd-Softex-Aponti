from rest_framework import serializers
from .models import Carrinho, ItemCarrinho
from creations.serializers import PersonalizacaoSerializer


class ItemCarrinhoSerializer(serializers.ModelSerializer):
    personalizacao_detalhe = PersonalizacaoSerializer(source='personalizacao', read_only=True)

    class Meta:
        model = ItemCarrinho
        fields = [
            'id', 'carrinho', 'personalizacao', 'personalizacao_detalhe',
            'quantidade', 'preco_unitario', 'subtotal', 'criado_em'
        ]
        read_only_fields = ['id', 'carrinho', 'subtotal', 'criado_em']


class CarrinhoSerializer(serializers.ModelSerializer):
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Carrinho
        fields = ['id', 'usuario', 'status', 'itens', 'total', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'usuario', 'status', 'total', 'criado_em', 'atualizado_em']
