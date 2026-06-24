from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Produto
from .serializers import ProdutoSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.filter(ativo=True)
    serializer_class = ProdutoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao', 'categoria']
    ordering_fields = ['nome', 'preco_base', 'data_criacao']
    ordering = ['nome']

    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        categoria = request.query_params.get('categoria')
        if categoria:
            produtos = self.queryset.filter(categoria=categoria)
            serializer = self.get_serializer(produtos, many=True)
            return Response(serializer.data)
        return Response({'error': 'Categoria não especificada'}, status=400)

    @action(detail=False, methods=['get'])
    def disponiveis(self, request):
        produtos = self.queryset.filter(estoque__gt=0)
        serializer = self.get_serializer(produtos, many=True)
        return Response(serializer.data)


# Views HTML para templates
def produto_list_view(request):
    produtos = Produto.objects.filter(ativo=True).order_by('nome')
    categoria = request.GET.get('categoria')
    busca = request.GET.get('busca')

    if categoria:
        produtos = produtos.filter(categoria=categoria)
    if busca:
        produtos = produtos.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))

    categorias = Produto.CATEGORIA_CHOICES

    return render(request, 'products/produto_list.html', {
        'produtos': produtos,
        'categorias': categorias,
        'categoria_selecionada': categoria,
        'busca': busca
    })


def produto_detail_view(request, pk):
    produto = get_object_or_404(Produto, pk=pk, ativo=True)
    return render(request, 'products/produto_detail.html', {'produto': produto})
