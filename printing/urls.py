from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImpressoraViewSet, 
    PrintingRootAPIView, 
    PrintingUIView,
    impressora_list_view,
    impressora_detail_view,
    fila_lista_view,
    fila_status_update_view
)

app_name = 'printing'

router = DefaultRouter()
router.register(r'impressoras', ImpressoraViewSet, basename='impressora')

urlpatterns = [
    # HTML Templates
    path('', impressora_list_view, name='impressora-list'),
    path('<int:pk>/', impressora_detail_view, name='impressora-detail'),
    path('fila/', fila_lista_view, name='fila-lista'),
    path('fila/<int:pk>/status/', fila_status_update_view, name='fila-status-update'),
    
    # UI de documentação
    path('ui/', PrintingUIView.as_view(), name='ui'),
    
    # API REST
    path('api-root/', PrintingRootAPIView.as_view(), name='printing-root'),
    path('api/', include(router.urls)),
]