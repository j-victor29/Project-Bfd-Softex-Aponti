from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PedidoViewSet, ItemPedidoViewSet, OrdersRootAPIView, OrdersUIView

app_name = 'orders'

router = DefaultRouter()
router.register(r"orders", PedidoViewSet, basename="orders")

urlpatterns = [
    # UI de documentação (sem autenticação, URLs hardcoded)
    path("ui/", OrdersUIView.as_view(), name="ui"),
    # API Root customizado
    path("", OrdersRootAPIView.as_view(), name="orders-root"),
    # API Endpoints
    path("", include(router.urls)),
    path(
        "items/<int:pk>/",
        ItemPedidoViewSet.as_view({"put": "update", "delete": "destroy"}),
        name="order-item-detail",
    ),
]