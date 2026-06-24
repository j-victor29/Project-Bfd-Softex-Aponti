from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Carrinho, ItemCarrinho
from creations.models import Personalizacao
from orders.models import Pedido, ItemPedido
from orders.services import PedidoService
from .serializers import CarrinhoSerializer, ItemCarrinhoSerializer


# ============================================================================
# HTML VIEWS (Templates)
# ============================================================================

@login_required
def carrinho_detalhe_view(request):
    """Exibe o carrinho aberto do usuário."""
    carrinho, created = Carrinho.objects.get_or_create(
        usuario=request.user,
        status='aberto'
    )
    return render(request, 'cart/carrinho.html', {
        'carrinho': carrinho,
    })


@login_required
@transaction.atomic
def adicionar_ao_carrinho_view(request, personalizacao_id):
    """Adiciona uma personalização ao carrinho do usuário."""
    personalizacao = get_object_or_404(Personalizacao, id=personalizacao_id)
    carrinho, created = Carrinho.objects.get_or_create(
        usuario=request.user,
        status='aberto'
    )

    # Verifica se já existe o mesmo item no carrinho
    item_existente = ItemCarrinho.objects.filter(
        carrinho=carrinho,
        personalizacao=personalizacao
    ).first()

    if item_existente:
        item_existente.quantidade += 1
        item_existente.save()
    else:
        # Preço unitário = preço base do produto + preço extra da personalização
        preco_unitario = personalizacao.produto.preco_base + personalizacao.preco_extra
        ItemCarrinho.objects.create(
            carrinho=carrinho,
            personalizacao=personalizacao,
            quantidade=1,
            preco_unitario=preco_unitario
        )

    messages.success(request, "Personalização adicionada ao carrinho com sucesso.")
    return redirect('cart:carrinho-detalhe')


@login_required
@transaction.atomic
def atualizar_carrinho_view(request, item_id):
    """Atualiza a quantidade de um item do carrinho."""
    if request.method == 'POST':
        item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user, carrinho__status='aberto')
        try:
            quantidade = int(request.POST.get('quantidade', 1))
            if quantidade < 1:
                messages.error(request, "A quantidade deve ser pelo menos 1.")
            else:
                item.quantidade = quantidade
                item.save()
                messages.success(request, "Quantidade atualizada com sucesso.")
        except ValueError:
            messages.error(request, "Quantidade inválida.")
    return redirect('cart:carrinho-detalhe')


@login_required
@transaction.atomic
def remover_do_carrinho_view(request, item_id):
    """Remove um item do carrinho."""
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user, carrinho__status='aberto')
    item.delete()
    messages.success(request, "Item removido do carrinho.")
    return redirect('cart:carrinho-detalhe')


@login_required
def finalizar_carrinho_view(request):
    """Finaliza o carrinho e cria o pedido correspondente."""
    carrinho = get_object_or_404(Carrinho, usuario=request.user, status='aberto')

    if not carrinho.itens.exists():
        messages.error(request, "Não é possível finalizar um carrinho vazio.")
        return redirect('cart:carrinho-detalhe')

    # Identificar o artista do primeiro item para criar o pedido
    primeiro_item = carrinho.itens.first()
    artista = primeiro_item.personalizacao.arte.artista

    # Forçar ativação do artista se necessário (idêntico ao criar_pedido_do_item_view original)
    if not artista.ativo:
        artista.ativo = True
        artista.save()

    with transaction.atomic():
        # Criar o pedido
        pedido = PedidoService.criar_pedido(request.user, artista)

        # Adicionar os itens
        for item in carrinho.itens.all():
            PedidoService.adicionar_item(
                pedido=pedido,
                produto=item.personalizacao.produto,
                personalizacao=item.personalizacao,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario
            )

        # Atualizar status do carrinho
        carrinho.status = 'finalizado'
        carrinho.save()

    messages.success(request, "Pedido finalizado com sucesso!")
    return redirect('orders:pedido-detail', pk=pedido.id)


# ============================================================================
# API VIEWSETS (REST)
# ============================================================================

class CarrinhoViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para gerenciar o carrinho do usuário.
    """
    serializer_class = CarrinhoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Carrinho.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def atual(self, request):
        """Retorna o carrinho aberto atual do usuário."""
        carrinho, created = Carrinho.objects.get_or_create(
            usuario=request.user,
            status='aberto'
        )
        serializer = self.get_serializer(carrinho)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def finalizar(self, request):
        """Finaliza o carrinho atual criando um pedido."""
        carrinho = get_object_or_404(Carrinho, usuario=request.user, status='aberto')
        if not carrinho.itens.exists():
            return Response(
                {"detail": "Não é possível finalizar um carrinho vazio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        primeiro_item = carrinho.itens.first()
        artista = primeiro_item.personalizacao.arte.artista

        if not artista.ativo:
            artista.ativo = True
            artista.save()

        with transaction.atomic():
            pedido = PedidoService.criar_pedido(request.user, artista)
            for item in carrinho.itens.all():
                PedidoService.adicionar_item(
                    pedido=pedido,
                    produto=item.personalizacao.produto,
                    personalizacao=item.personalizacao,
                    quantidade=item.quantidade,
                    preco_unitario=item.preco_unitario
                )
            carrinho.status = 'finalizado'
            carrinho.save()

        return Response(
            {"detail": "Pedido finalizado com sucesso!", "pedido_id": pedido.id},
            status=status.HTTP_201_CREATED
        )


class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para gerenciar itens no carrinho.
    """
    serializer_class = ItemCarrinhoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ItemCarrinho.objects.filter(carrinho__usuario=self.request.user)

    def perform_create(self, serializer):
        carrinho, created = Carrinho.objects.get_or_create(
            usuario=self.request.user,
            status='aberto'
        )
        personalizacao = serializer.validated_data['personalizacao']

        # Prevenir duplicidades na API
        item_existente = ItemCarrinho.objects.filter(
            carrinho=carrinho,
            personalizacao=personalizacao
        ).first()

        if item_existente:
            item_existente.quantidade += serializer.validated_data.get('quantidade', 1)
            item_existente.save()
            # Retornar o serializer atualizado
            serializer.instance = item_existente
        else:
            preco_unitario = personalizacao.produto.preco_base + personalizacao.preco_extra
            serializer.save(carrinho=carrinho, preco_unitario=preco_unitario)
