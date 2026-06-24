from django.db.models import Sum, Count
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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


@login_required
def dashboard_view(request):
    usuario = request.user
    # Obter ou criar pontos do usuário
    pontos, _ = Pontos.objects.get_or_create(usuario=usuario)
    
    # Calcular badges desbloqueados
    badges_desbloqueados = UsuarioRecompensa.objects.filter(usuario=usuario).exclude(badge=None).count()
    
    # Posição no ranking
    ranking_obj = Ranking.objects.filter(usuario=usuario, tipo='usuarios').first()
    posicao_ranking = ranking_obj.posicao if ranking_obj else "-"
    
    # Nível atual
    nivel_atual = Nivel.objects.filter(pontos_minimos__lte=pontos.total_acumulado).order_by('-pontos_minimos').first()
    if not nivel_atual:
        nivel_atual = Nivel.objects.filter(numero=1).first()
        
    proximo_nivel = Nivel.objects.filter(pontos_minimos__gt=pontos.total_acumulado).order_by('pontos_minimos').first()
    
    progresso_nivel = 0
    pontos_necessarios = 0
    if proximo_nivel and nivel_atual:
        total_nivel = proximo_nivel.pontos_minimos - nivel_atual.pontos_minimos
        acumulado_nivel = pontos.total_acumulado - nivel_atual.pontos_minimos
        if total_nivel > 0:
            progresso_nivel = min(int((acumulado_nivel / total_nivel) * 100), 100)
            progresso_nivel = max(progresso_nivel, 0)
        pontos_necessarios = proximo_nivel.pontos_minimos - pontos.total_acumulado

    stats = {
        'pontos_saldo': pontos.saldo,
        'pontos_total': pontos.total_acumulado,
        'badges_desbloqueados': badges_desbloqueados,
        'posicao_ranking': posicao_ranking,
        'nivel_atual': nivel_atual,
        'proximo_nivel': proximo_nivel,
        'progresso_nivel': progresso_nivel,
        'pontos_necessarios': pontos_necessarios,
    }
    
    ultimas_conquistas = UsuarioRecompensa.objects.filter(usuario=usuario).exclude(badge=None).order_by('-data_desbloqueio')[:5]
    
    return render(request, 'gamification/dashboard.html', {
        'stats': stats,
        'ultimas_conquistas': ultimas_conquistas
    })


@login_required
def badges_view(request):
    usuario = request.user
    categoria = request.GET.get('categoria')
    
    badges = Badge.objects.all()
    if categoria:
        badges = badges.filter(categoria=categoria)
        
    desbloqueados_ids = list(UsuarioRecompensa.objects.filter(usuario=usuario).exclude(badge=None).values_list('badge_id', flat=True))
    
    categories = [choice[0] for choice in Badge.CATEGORIA_CHOICES]
    
    return render(request, 'gamification/badges_list.html', {
        'badges': badges,
        'badges_desbloqueados': desbloqueados_ids,
        'badges_categories': categories,
    })


@login_required
def ranking_view(request):
    usuario = request.user
    ranking = Ranking.objects.filter(tipo='usuarios').order_by('posicao')[:20]
    posicao_usuario = Ranking.objects.filter(usuario=usuario, tipo='usuarios').first()
    
    return render(request, 'gamification/ranking_list.html', {
        'ranking': ranking,
        'posicao_usuario': posicao_usuario,
    })
