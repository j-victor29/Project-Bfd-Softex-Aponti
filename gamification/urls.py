from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecompensaViewSet, 
    UsuarioRecompensaViewSet, 
    GamificationRootAPIView, 
    GamificationUIView,
    dashboard_view,
    badges_view,
    ranking_view
)

app_name = 'gamification'

router = DefaultRouter()
router.register(r'recompensas', RecompensaViewSet, basename='recompensa')
router.register(r'usuario-recompensas', UsuarioRecompensaViewSet, basename='usuario-recompensa')

urlpatterns = [
    # HTML Templates
    path('', dashboard_view, name='gamification-dashboard'),
    path('badges/', badges_view, name='badges-list'),
    path('ranking/', ranking_view, name='ranking-list'),
    
    # UI de documentação
    path('ui/', GamificationUIView.as_view(), name='ui'),
    
    # API REST
    path('api-root/', GamificationRootAPIView.as_view(), name='gamification-root'),
    path('api/', include(router.urls)),
]