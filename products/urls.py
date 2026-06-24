from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProdutoViewSet, produto_list_view, produto_detail_view

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet, basename='api-produto')

urlpatterns = [
    # Rotas HTML (templates)
    path('', produto_list_view, name='produto-list'),
    path('<int:pk>/', produto_detail_view, name='produto-detail'),
    
    # Rotas API REST
    path('api/', include(router.urls)),
]