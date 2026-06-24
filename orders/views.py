from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.reverse import reverse

from .models import Pedido, ItemPedido
from .serializers import (
    PedidoListSerializer, PedidoDetailSerializer, PedidoStatusUpdateSerializer,
    PedidoCreateSerializer,
    ItemPedidoSerializer, ItemPedidoCreateUpdateSerializer
)
from .services import PedidoService


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Pedidos.
    
    Endpoints:
    - GET /orders/ → Lista pedidos do usuário
    - POST /orders/ → Cria novo pedido
    - GET /orders/{id}/ → Detalhes do pedido
    - PATCH /orders/{id}/status/ → Atualiza status
    - POST /orders/{id}/items/ → Adiciona item
    - PATCH /orders/{id}/marcar-impresso/ → Marca como impresso
    - PATCH /orders/{id}/marcar-enviado/ → Marca como enviado
    - PATCH /orders/{id}/finalizar/ → Finaliza pedido
    """
    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all()

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-data_pedido')

    def get_serializer_class(self):
        if self.action == 'list':
            return PedidoListSerializer
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoDetailSerializer

    def create(self, request, *args, **kwargs):
        """Cria um novo pedido"""
        serializer = PedidoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()
        
        response_serializer = PedidoDetailSerializer(pedido, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def status(self, request, pk=None):
        """Atualiza o status do pedido com validação de fluxo"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        serializer = PedidoStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        novo_status = serializer.validated_data['status_pedido']

        try:
            if novo_status == 'pago':
                forma = request.data.get('forma_pagamento')
                if not forma:
                    return Response(
                        {'detail': 'forma_pagamento é obrigatória para status "pago".'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                pedido = PedidoService.confirmar_pagamento(
                    pedido, 
                    forma_pagamento=forma, 
                    status_pagamento=request.data.get('status_pagamento', 'confirmado')
                )
            elif novo_status == 'em_producao':
                pedido = PedidoService.enviar_para_producao(pedido)
            elif novo_status == 'impresso':
                pedido = PedidoService.marcar_como_impresso(pedido)
            elif novo_status == 'enviado':
                pedido = PedidoService.marcar_como_enviado(pedido)
            elif novo_status == 'concluido':
                pedido = PedidoService.finalizar_pedido(pedido)
            elif novo_status == 'cancelado':
                pedido = PedidoService.cancelar_pedido(pedido)
            else:
                return Response(
                    {'detail': 'Status não suportado.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='marcar-impresso')
    def marcar_impresso(self, request, pk=None):
        """Marca o pedido como impresso"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        
        try:
            pedido = PedidoService.marcar_como_impresso(pedido)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='marcar-enviado')
    def marcar_enviado(self, request, pk=None):
        """Marca o pedido como enviado"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        
        try:
            pedido = PedidoService.marcar_como_enviado(pedido)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['patch'], url_path='finalizar')
    def finalizar(self, request, pk=None):
        """Finaliza o pedido (marca como concluído)"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        
        try:
            pedido = PedidoService.finalizar_pedido(pedido)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoDetailSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """Adiciona um item ao pedido"""
        pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
        serializer = ItemPedidoCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            item = PedidoService.adicionar_item(
                pedido,
                data['produto'],
                data['personalizacao'],
                data['quantidade'],
                data['preco_unitario']
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ItemPedidoSerializer(item, context={'request': request}).data, 
            status=status.HTTP_201_CREATED
        )


class ItemPedidoViewSet(mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """ViewSet para gerenciar Itens de Pedido"""
    permission_classes = [IsAuthenticated]
    queryset = ItemPedido.objects.all()
    serializer_class = ItemPedidoSerializer

    def get_object(self):
        obj = get_object_or_404(ItemPedido, pk=self.kwargs['pk'], pedido__usuario=self.request.user)
        return obj

    def update(self, request, *args, **kwargs):
        """Atualiza quantidade e/ou preço de um item"""
        item = self.get_object()
        serializer = ItemPedidoCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            item = PedidoService.atualizar_item(
                item,
                quantidade=data.get('quantidade'),
                preco_unitario=data.get('preco_unitario')
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ItemPedidoSerializer(item, context={'request': request}).data)

    def destroy(self, request, *args, **kwargs):
        """Remove um item do pedido"""
        item = self.get_object()
        try:
            PedidoService.remover_item(item)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersRootAPIView(APIView):
    """
    API Root customizada para o módulo de Pedidos.
    Exibe descrição do módulo e lista de endpoints disponíveis.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        """Retorna informações sobre o módulo de pedidos e endpoints disponíveis"""
        return Response({
            'module': 'Orders',
            'description': 'Gerenciamento de pedidos e itens de pedido',
            'version': '1.0',
            'endpoints': {
                'orders': {
                    'url': reverse('orders:orders-list', request=request),
                    'description': 'Lista todos os pedidos do usuário',
                    'methods': ['GET', 'POST'],
                    'details': 'GET retorna lista paginada; POST cria novo pedido'
                },
                'orders-detail': {
                    'url': reverse('orders:orders-detail', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Detalhes, atualização e exclusão de um pedido específico',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'details': 'Substitua {id} pelo ID do pedido'
                },
                'orders-status': {
                    'url': reverse('orders:orders-status', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Atualiza o status do pedido',
                    'methods': ['PATCH'],
                    'details': 'Aceita: pago, em_producao, impresso, enviado, concluido, cancelado'
                },
                'orders-marcar-impresso': {
                    'url': reverse('orders:orders-marcar-impresso', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Marca o pedido como impresso',
                    'methods': ['PATCH'],
                    'details': ''
                },
                'orders-marcar-enviado': {
                    'url': reverse('orders:orders-marcar-enviado', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Marca o pedido como enviado',
                    'methods': ['PATCH'],
                    'details': ''
                },
                'orders-finalizar': {
                    'url': reverse('orders:orders-finalizar', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Finaliza o pedido',
                    'methods': ['PATCH'],
                    'details': ''
                },
                'order-items': {
                    'url': reverse('orders:order-item-detail', request=request, kwargs={'pk': '1'}).replace('/1', '/{item_id}'),
                    'description': 'Atualiza e remove itens de um pedido',
                    'methods': ['PUT', 'PATCH', 'DELETE'],
                    'details': 'Substitua {item_id} pelo ID do item'
                },
            },
            'authentication': 'Token/JWT required',
            'pagination': 'Suportado para listagens',
        })


class OrdersUIView(TemplateView):
    """
    View para renderizar documentação HTML da API Orders.
    Sem autenticação, sem reverse(), URLs hardcoded.
    """
    template_name = 'orders/ui.html'


@login_required
def order_list_html(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-data_pedido')
    return render(request, 'orders/pedido_list.html', {'pedidos': pedidos})


@login_required
def order_detail_html(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    return render(request, 'orders/pedido_detail.html', {'pedido': pedido})

