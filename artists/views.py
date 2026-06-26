from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.db.models import Sum, Count

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Artista
from .serializers import ArtistaSerializer


# ─── REST API ViewSet ──────────────────────────────────────────────────────────

class ArtistaViewSet(ModelViewSet):
    queryset = Artista.objects.filter(ativo=True)
    serializer_class = ArtistaSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


# ─── Páginas públicas ──────────────────────────────────────────────────────────

def artista_list(request):
    artistas = Artista.objects.filter(ativo=True)
    return render(request, 'artists/artista_list.html', {'artistas': artistas})


def artista_detail(request, pk):
    artista = get_object_or_404(Artista, pk=pk, ativo=True)
    return render(request, 'artists/artista_detail.html', {'artista': artista})


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _get_artista_ou_403(request):
    """
    Retorna o perfil de Artista do usuário logado.
    - Superuser sem perfil retorna None (acesso liberado sem dados de artista).
    - Usuário sem perfil ou com perfil não-aprovado retorna False → 403.
    """
    if request.user.is_superuser:
        return getattr(request.user, 'perfil_artista', None)

    try:
        artista = request.user.perfil_artista
    except Artista.DoesNotExist:
        return False

    if artista.status_aprovacao != 'aprovado':
        return False

    return artista


def _403(msg="Apenas artistas aprovados podem acessar o painel."):
    """Retorna resposta 403 com mensagem amigável."""
    return HttpResponseForbidden(
        f"<h1>403 — Acesso Negado</h1><p>{msg}</p>"
    )


# ─── Painel Principal ──────────────────────────────────────────────────────────

@login_required
def painel_principal(request):
    artista = _get_artista_ou_403(request)
    if artista is False:
        return _403()

    from orders.models import ItemPedido, Pedido
    from creations.models import Arte

    if artista:
        total_artes = artista.artes.count()
        total_colecoes = artista.colecoes.count()

        itens_do_artista = ItemPedido.objects.filter(
            personalizacao__arte__artista=artista
        ).select_related('pedido', 'pedido__usuario', 'personalizacao__arte')

        total_vendas = itens_do_artista.count()

        soma_subtotais = itens_do_artista.aggregate(
            total=Sum('subtotal')
        )['total'] or Decimal('0.00')
        comissao_estimada = soma_subtotais * Decimal('0.10')

        pedidos_ids = (
            itens_do_artista
            .values_list('pedido_id', flat=True)
            .distinct()
        )
        ultimos_pedidos = (
            Pedido.objects.filter(id__in=pedidos_ids)
            .order_by('-data_pedido')[:5]
        )

        artes_mais_usadas = (
            Arte.objects.filter(artista=artista)
            .annotate(total_uso=Count('personalizacoes__itens_pedido'))
            .order_by('-total_uso')[:5]
        )
    else:
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


# ─── Painel de Artes ───────────────────────────────────────────────────────────

@login_required
def painel_artes(request):
    artista = _get_artista_ou_403(request)
    if artista is False:
        return _403()

    colecao_selecionada = None
    if artista:
        artes = (
            artista.artes
            .select_related('colecao')
            .annotate(total_uso=Count('personalizacoes__itens_pedido'))
            .order_by('-criado_em')
        )
        colecao_id = request.GET.get('colecao')
        if colecao_id:
            from creations.models import Colecao
            colecao_selecionada = get_object_or_404(Colecao, id=colecao_id, artista=artista)
            artes = artes.filter(colecao=colecao_selecionada)
    else:
        from creations.models import Arte
        artes = Arte.objects.none()

    return render(request, 'artists/painel_artes.html', {
        'artista': artista,
        'artes': artes,
        'colecao_selecionada': colecao_selecionada,
    })


# ─── Painel de Colecoes ────────────────────────────────────────────────────────

@login_required
def painel_colecoes(request):
    artista = _get_artista_ou_403(request)
    if artista is False:
        return _403()

    if artista:
        colecoes = (
            artista.colecoes
            .annotate(total_artes_count=Count('artes'))
            .order_by('-criado_em')
        )
    else:
        from creations.models import Colecao
        colecoes = Colecao.objects.none()

    return render(request, 'artists/painel_colecoes.html', {
        'artista': artista,
        'colecoes': colecoes,
    })


# ─── CRUD de Artes ─────────────────────────────────────────────────────────────

@login_required
def painel_arte_nova(request):
    """Cria uma nova arte vinculada ao artista logado."""
    artista = _get_artista_ou_403(request)
    if artista is False or artista is None:
        return _403()

    from .forms import ArteForm

    if request.method == 'POST':
        form = ArteForm(request.POST, request.FILES)
        form.set_artista(artista)
        if form.is_valid():
            arte = form.save(commit=False)
            arte.artista = artista
            arte.save()
            messages.success(request, f'Arte "{arte.nome}" criada com sucesso!')
            return redirect('painel-artes')
    else:
        form = ArteForm()
        form.set_artista(artista)

    return render(request, 'artists/painel_arte_form.html', {
        'artista': artista,
        'form': form,
        'titulo': 'Nova Arte',
        'editando': False,
    })


@login_required
def painel_arte_editar(request, pk):
    """Edita uma arte existente; garante que pertence ao artista logado."""
    artista = _get_artista_ou_403(request)
    if artista is False or artista is None:
        return _403()

    from creations.models import Arte
    from .forms import ArteForm

    arte = get_object_or_404(Arte, pk=pk)
    if arte.artista != artista:
        return _403("Você nao tem permissao para editar esta arte.")

    if request.method == 'POST':
        form = ArteForm(request.POST, request.FILES, instance=arte)
        form.set_artista(artista)
        if form.is_valid():
            form.save()
            messages.success(request, f'Arte "{arte.nome}" atualizada com sucesso!')
            return redirect('painel-artes')
    else:
        form = ArteForm(instance=arte)
        form.set_artista(artista)

    return render(request, 'artists/painel_arte_form.html', {
        'artista': artista,
        'form': form,
        'arte': arte,
        'titulo': f'Editar Arte',
        'editando': True,
    })


@login_required
def painel_arte_status(request, pk):
    """Toggle ativa/inativa de uma arte. Aceita apenas POST."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    artista = _get_artista_ou_403(request)
    if artista is False or artista is None:
        return _403()

    from creations.models import Arte
    arte = get_object_or_404(Arte, pk=pk)
    if arte.artista != artista:
        return _403("Você nao tem permissao para alterar o status desta arte.")

    arte.ativa = not arte.ativa
    arte.save(update_fields=['ativa'])
    status_label = 'ativada' if arte.ativa else 'inativada'
    messages.success(request, f'Arte "{arte.nome}" {status_label} com sucesso!')
    return redirect('painel-artes')


# ─── CRUD de Colecoes ──────────────────────────────────────────────────────────

@login_required
def painel_colecao_nova(request):
    """Cria uma nova colecao vinculada ao artista logado."""
    artista = _get_artista_ou_403(request)
    if artista is False or artista is None:
        return _403()

    from .forms import ColecaoForm

    if request.method == 'POST':
        form = ColecaoForm(request.POST, request.FILES)
        if form.is_valid():
            colecao = form.save(commit=False)
            colecao.artista = artista
            colecao.save()
            messages.success(request, f'Colecao "{colecao.nome}" criada com sucesso!')
            return redirect('painel-colecoes')
    else:
        form = ColecaoForm()

    return render(request, 'artists/painel_colecao_form.html', {
        'artista': artista,
        'form': form,
        'titulo': 'Nova Colecao',
        'editando': False,
    })


@login_required
def painel_colecao_editar(request, pk):
    """Edita uma colecao existente; garante que pertence ao artista logado."""
    artista = _get_artista_ou_403(request)
    if artista is False or artista is None:
        return _403()

    from creations.models import Colecao
    from .forms import ColecaoForm

    colecao = get_object_or_404(Colecao, pk=pk)
    if colecao.artista != artista:
        return _403("Você nao tem permissao para editar esta colecao.")

    if request.method == 'POST':
        form = ColecaoForm(request.POST, request.FILES, instance=colecao)
        if form.is_valid():
            form.save()
            messages.success(request, f'Colecao "{colecao.nome}" atualizada com sucesso!')
            return redirect('painel-colecoes')
    else:
        form = ColecaoForm(instance=colecao)

    return render(request, 'artists/painel_colecao_form.html', {
        'artista': artista,
        'form': form,
        'colecao': colecao,
        'titulo': f'Editar Colecao',
        'editando': True,
    })


@login_required
def painel_colecao_status(request, pk):
    """Toggle ativa/inativa de uma colecao. Aceita apenas POST."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    artista = _get_artista_ou_403(request)
    if artista is False or artista is None:
        return _403()

    from creations.models import Colecao
    colecao = get_object_or_404(Colecao, pk=pk)
    if colecao.artista != artista:
        return _403("Você nao tem permissao para alterar o status desta colecao.")

    colecao.ativa = not colecao.ativa
    colecao.save(update_fields=['ativa'])
    status_label = 'ativada' if colecao.ativa else 'inativada'
    messages.success(request, f'Colecao "{colecao.nome}" {status_label} com sucesso!')
    return redirect('painel-colecoes')
