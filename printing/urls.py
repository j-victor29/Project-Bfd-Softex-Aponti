from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImpressoraViewSet, PrintingRootAPIView, PrintingUIView

app_name = 'printing'

router = DefaultRouter()
router.register(r'impressoras', ImpressoraViewSet, basename='impressora')

urlpatterns = [
    # UI de documentação (sem autenticação, URLs hardcoded)
    path('ui/', PrintingUIView.as_view(), name='ui'),
    # API Root customizado
    path('', PrintingRootAPIView.as_view(), name='printing-root'),
    # API Endpoints
    path('', include(router.urls)),
]