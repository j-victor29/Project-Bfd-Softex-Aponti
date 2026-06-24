from django.db.models import Sum, Count
from django.views.generic import TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from .models import (
    Recompensa, UsuarioRecompensa, Pontos, Nivel, Badge, Ranking
)
from .serializers import RecompensaSerializer, UsuarioRecompensaSerializer


class RecompensaViewSet(viewsets.ModelViewSet):
    queryset = Recompensa.objects.all()
    serializer_class = RecompensaSerializer


class UsuarioRecompensaViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRecompensa.objects.all()
    serializer_class = UsuarioRecompensaSerializer
    
    @action(detail=False, methods=['get'])
    def por_usuario(self, request):
        usuario_id = request.query_params.get('usuario_id')
        if not usuario_id:
            return Response({'erro': 'usuario_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        recompensas = UsuarioRecompensa.objects.filter(usuario_id=usuario_id)
        serializer = self.get_serializer(recompensas, many=True)
        return Response(serializer.data)


class GamificationRootAPIView(APIView):
    """
    API Root customizada para o módulo de Gamification.
    Exibe descrição do módulo e lista de endpoints disponíveis.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        """Retorna informações sobre o módulo de gamificação e endpoints disponíveis"""
        return Response({
            'module': 'Gamification',
            'description': 'Sistema de recompensas, pontos, níveis, badges e ranking do usuário',
            'version': '1.0',
            'endpoints': {
                'recompensas': {
                    'url': reverse('gamification:recompensa-list', request=request),
                    'description': 'Lista todas as recompensas disponíveis',
                    'methods': ['GET', 'POST'],
                    'details': 'GET retorna lista de todas as recompensas; POST cria nova recompensa (admin)'
                },
                'recompensas-detail': {
                    'url': reverse('gamification:recompensa-detail', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Detalhes, atualização e exclusão de uma recompensa',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'details': 'Substitua {id} pelo ID da recompensa'
                },
                'usuario-recompensas': {
                    'url': reverse('gamification:usuario-recompensa-list', request=request),
                    'description': 'Lista recompensas conquistadas pelo usuário',
                    'methods': ['GET', 'POST'],
                    'details': 'GET retorna recompensas do usuário autenticado'
                },
                'usuario-recompensas-por-usuario': {
                    'url': reverse('gamification:usuario-recompensa-por-usuario', request=request),
                    'description': 'Lista recompensas de um usuário específico',
                    'methods': ['GET'],
                    'details': 'Query param: usuario_id (obrigatório)'
                },
                'usuario-recompensas-detail': {
                    'url': reverse('gamification:usuario-recompensa-detail', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Detalhes de uma recompensa conquistada',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'details': 'Substitua {id} pelo ID do registro'
                },
            },
            'features': {
                'points': 'Acúmulo de pontos por ações do usuário',
                'levels': 'Progressão de níveis baseada em pontos',
                'badges': 'Conquistas desbloqueáveis por ações específicas',
                'ranking': 'Posicionamento do usuário entre todos os usuários'
            },
            'authentication': 'Opcional para listagens públicas, recomendado para usuário',
            'pagination': 'Suportado para listagens',
        })


class GamificationUIView(TemplateView):
    """
    View para renderizar documentação HTML da API Gamification.
    Sem autenticação, sem reverse(), URLs hardcoded.
    """
    template_name = 'gamification/ui.html'
