from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecompensaViewSet, UsuarioRecompensaViewSet, GamificationRootAPIView, GamificationUIView

app_name = 'gamification'

router = DefaultRouter()
router.register(r'recompensas', RecompensaViewSet, basename='recompensa')
router.register(r'usuario-recompensas', UsuarioRecompensaViewSet, basename='usuario-recompensa')

urlpatterns = [
    # UI de documentação (sem autenticação, URLs hardcoded)
    path('ui/', GamificationUIView.as_view(), name='ui'),
    # API Root customizado
    path('', GamificationRootAPIView.as_view(), name='gamification-root'),
    # API Endpoints
    path('', include(router.urls)),
]