from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, Count, Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Artista
from .serializers import ArtistaSerializer


# ─── REST API ViewSet (já existente) ──────────────────────────────────────────

class ArtistaViewSet(ModelViewSet):
    queryset = Artista.objects.filter(ativo=True)
    serializer_class = ArtistaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# ─── Páginas públicas (já existentes) ─────────────────────────────────────────

def artista_list(request):
    artistas = Artista.objects.filter(ativo=True)
    return render(request, 'artists/artista_list.html', {'artistas': artistas})


def artista_detail(request, pk):
    artista = get_object_or_404(Artista, pk=pk, ativo=True)
    return render(request, 'artists/artista_detail.html', {'artista': artista})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_artista_ou_403(request):
    """
    Retorna o perfil de Artista do usuário logado.
    - Superuser sem perfil retorna None (acesso liberado sem dados de artista).
    - Usuário sem perfil ou com perfil não-aprovado retorna False → 403.
    """
    if request.user.is_superuser:
        # Superuser pode acessar; tenta obter perfil próprio, se existir
        return getattr(request.user, 'perfil_artista', None)

    try:
        artista = request.user.perfil_artista
    except Artista.DoesNotExist:
        return False

    if artista.status_aprovacao != 'aprovado':
        return False

    return artista


# ─── Painel Principal ─────────────────────────────────────────────────────────

@login_required
def painel_principal(request):
    artista = _get_artista_ou_403(request)
    if artista is False:
        return HttpResponseForbidden(
            "<h1>403 — Acesso Negado</h1>"
            "<p>Apenas artistas aprovados podem acessar o painel.</p>"
        )

    from orders.models import ItemPedido
    from creations.models import Arte

    if artista:
        # Métricas de artes e coleções
        total_artes = artista.artes.count()
        total_colecoes = artista.colecoes.count()

        # Pedidos que usam artes deste artista
        itens_do_artista = ItemPedido.objects.filter(
            personalizacao__arte__artista=artista
        ).select_related('pedido', 'pedido__usuario', 'personalizacao__arte')

        total_vendas = itens_do_artista.count()

        # Comissão estimada: 10% do subtotal dos itens
        soma_subtotais = itens_do_artista.aggregate(
            total=Sum('subtotal')
        )['total'] or Decimal('0.00')
        comissao_estimada = soma_subtotais * Decimal('0.10')

        # Últimos 5 pedidos que usam artes do artista
        pedidos_ids = (
            itens_do_artista
            .values_list('pedido_id', flat=True)
            .distinct()
        )
        from orders.models import Pedido
        ultimos_pedidos = (
            Pedido.objects.filter(id__in=pedidos_ids)
            .order_by('-data_pedido')[:5]
        )

        # Artes mais utilizadas (top 5)
        artes_mais_usadas = (
            Arte.objects.filter(artista=artista)
            .annotate(total_uso=Count('personalizacoes__itens_pedido'))
            .order_by('-total_uso')[:5]
        )
    else:
        # Superuser sem perfil: painel vazio
        total_artes = 0
        total_colecoes = 0
        total_vendas = 0
        comissao_estimada = Decimal('0.00')
        ultimos_pedidos = []
        artes_mais_usadas = []

    context = {
        'artista': artista,
        'total_artes': total_artes,
        'total_colecoes': total_colecoes,
        'total_vendas': total_vendas,
        'comissao_estimada': comissao_estimada,
        'ultimos_pedidos': ultimos_pedidos,
        'artes_mais_usadas': artes_mais_usadas,
    }
    return render(request, 'artists/painel.html', context)


# ─── Painel de Artes ──────────────────────────────────────────────────────────

@login_required
def painel_artes(request):
    artista = _get_artista_ou_403(request)
    if artista is False:
        return HttpResponseForbidden(
            "<h1>403 — Acesso Negado</h1>"
            "<p>Apenas artistas aprovados podem acessar o painel.</p>"
        )

    from orders.models import ItemPedido

    if artista:
        artes = (
            artista.artes
            .select_related('colecao')
            .annotate(total_uso=Count('personalizacoes__itens_pedido'))
            .order_by('-criado_em')
        )
    else:
        from creations.models import Arte
        artes = Arte.objects.none()

    context = {
        'artista': artista,
        'artes': artes,
    }
    return render(request, 'artists/painel_artes.html', context)


# ─── Painel de Coleções ───────────────────────────────────────────────────────

@login_required
def painel_colecoes(request):
    artista = _get_artista_ou_403(request)
    if artista is False:
        return HttpResponseForbidden(
            "<h1>403 — Acesso Negado</h1>"
            "<p>Apenas artistas aprovados podem acessar o painel.</p>"
        )

    if artista:
        colecoes = (
            artista.colecoes
            .annotate(total_artes_count=Count('artes'))
            .order_by('-criado_em')
        )
    else:
        from creations.models import Colecao
        colecoes = Colecao.objects.none()

    context = {
        'artista': artista,
        'colecoes': colecoes,
    }
    return render(request, 'artists/painel_colecoes.html', context)
