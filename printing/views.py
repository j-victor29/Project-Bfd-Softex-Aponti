from django.db.models import Q
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from .models import Impressora, FilaImpressao
from .serializers import ImpressoraListSerializer, ImpressoraDetailSerializer, ImpressoraCreateUpdateSerializer


class ImpressoraViewSet(viewsets.ModelViewSet):
    queryset = Impressora.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
            return ImpressoraCreateUpdateSerializer
        elif self.action == 'retrieve':
            return ImpressoraDetailSerializer
        return ImpressoraListSerializer
    
    @action(detail=False, methods=['get'])
    def ativas(self, request):
        """Retorna apenas impressoras ativas"""
        impressoras = self.queryset.filter(status='ativo')
        serializer = ImpressoraListSerializer(impressoras, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marcar_manutencao(self, request):
        """Marca impressora como em manutenção"""
        impressora = self.get_object()
        impressora.status = 'manutencao'
        impressora.save()
        serializer = ImpressoraDetailSerializer(impressora)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ativar(self, request):
        """Ativa impressora"""
        impressora = self.get_object()
        impressora.status = 'ativo'
        impressora.save()
        serializer = ImpressoraDetailSerializer(impressora)
        return Response(serializer.data)


class PrintingRootAPIView(APIView):
    """
    API Root customizada para o módulo de Printing.
    Exibe descrição do módulo e lista de endpoints disponíveis.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        """Retorna informações sobre o módulo de impressoras e endpoints disponíveis"""
        return Response({
            'module': 'Printing',
            'description': 'Gerenciamento de impressoras e filas de impressão',
            'version': '1.0',
            'endpoints': {
                'impressoras': {
                    'url': reverse('printing:impressora-list', request=request),
                    'description': 'Lista todas as impressoras cadastradas',
                    'methods': ['GET', 'POST'],
                    'details': 'GET retorna lista paginada; POST cria nova impressora'
                },
                'impressoras-detail': {
                    'url': reverse('printing:impressora-detail', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Detalhes, atualização e exclusão de uma impressora',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'details': 'Substitua {id} pelo ID da impressora'
                },
                'impressoras-ativas': {
                    'url': reverse('printing:impressora-ativas', request=request),
                    'description': 'Lista apenas impressoras em status ativo',
                    'methods': ['GET'],
                    'details': 'Útil para encontrar impressoras disponíveis'
                },
                'impressoras-marcar-manutencao': {
                    'url': reverse('printing:impressora-marcar-manutencao', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Marca uma impressora como em manutenção',
                    'methods': ['POST'],
                    'details': 'Substitua {id} pelo ID da impressora'
                },
                'impressoras-ativar': {
                    'url': reverse('printing:impressora-ativar', request=request, kwargs={'pk': '{id}'}),
                    'description': 'Ativa uma impressora',
                    'methods': ['POST'],
                    'details': 'Substitua {id} pelo ID da impressora'
                },
            },
            'printer_statuses': ['ativo', 'manutencao', 'inativo'],
            'authentication': 'Token/JWT required (optional for API Root)',
            'pagination': 'Suportado para listagens',
            'use_cases': {
                'check_availability': 'Use /impressoras/ativas/ para encontrar impressoras disponíveis',
                'schedule_printing': 'POST para /orders/ para criar pedidos e associar impressoras',
                'maintenance': 'Use /impressoras/{id}/marcar-manutencao/ quando precisar fazer manutenção'
            }
        })


class PrintingUIView(TemplateView):
    """
    View para renderizar documentação HTML da API Printing.
    Sem autenticação, sem reverse(), URLs hardcoded.
    """
    template_name = 'printing/ui.html'


@login_required
def impressora_list_view(request):
    impressoras = Impressora.objects.all()
    total_ativas = impressoras.filter(status='ativo').count()
    total_manutencao = impressoras.filter(status='manutencao').count()
    total_inativas = impressoras.filter(status='inativo').count()
    
    return render(request, 'printing/impressora_list.html', {
        'impressoras': impressoras,
        'total_ativas': total_ativas,
        'total_manutencao': total_manutencao,
        'total_inativas': total_inativas,
    })


@login_required
def impressora_detail_view(request, pk):
    impressora = get_object_or_404(Impressora, pk=pk)
    return render(request, 'printing/impressora_detail.html', {'impressora': impressora})


@login_required
def fila_lista_view(request):
    fila = FilaImpressao.objects.all().order_by('posicao')
    aguardando = fila.filter(status='aguardando').count()
    imprimindo = fila.filter(status='imprimindo').count()
    erro = fila.filter(status='erro').count()
    
    return render(request, 'printing/fila_lista.html', {
        'fila': fila,
        'aguardando': aguardando,
        'imprimindo': imprimindo,
        'erro': erro,
    })
