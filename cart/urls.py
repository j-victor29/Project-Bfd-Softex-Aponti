from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    carrinho_detalhe_view,
    adicionar_ao_carrinho_view,
    atualizar_carrinho_view,
    remover_do_carrinho_view,
    finalizar_carrinho_view,
    CarrinhoViewSet,
    ItemCarrinhoViewSet,
)

app_name = 'cart'

router = DefaultRouter()
router.register(r'carrinho', CarrinhoViewSet, basename='api-carrinho')
router.register(r'itens', ItemCarrinhoViewSet, basename='api-item-carrinho')

urlpatterns = [
    # HTML Views
    path('', carrinho_detalhe_view, name='carrinho-detalhe'),
    path('adicionar/<int:personalizacao_id>/', adicionar_ao_carrinho_view, name='carrinho-adicionar'),
    path('atualizar/<int:item_id>/', atualizar_carrinho_view, name='carrinho-atualizar'),
    path('remover/<int:item_id>/', remover_do_carrinho_view, name='carrinho-remover'),
    path('finalizar/', finalizar_carrinho_view, name='carrinho-finalizar'),

    # REST API
    path('api/', include(router.urls)),
]
