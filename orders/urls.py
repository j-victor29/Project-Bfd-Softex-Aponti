from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PedidoViewSet, 
    ItemPedidoViewSet, 
    OrdersRootAPIView, 
    OrdersUIView,
    order_list_html,
    order_detail_html
)

app_name = 'orders'

router = DefaultRouter()
router.register(r"orders", PedidoViewSet, basename="orders")

urlpatterns = [
    # HTML Templates
    path("", order_list_html, name="pedido-list"),
    path("<int:pk>/", order_detail_html, name="pedido-detail"),
    path("ui/", OrdersUIView.as_view(), name="ui"),
    
    # API REST
    path("api/", include(router.urls)),
    path("api-root/", OrdersRootAPIView.as_view(), name="orders-root"),
    path(
        "api/items/<int:pk>/",
        ItemPedidoViewSet.as_view({"put": "update", "delete": "destroy"}),
        name="order-item-detail",
    ),
]