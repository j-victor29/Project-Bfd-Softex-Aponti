from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArtistaViewSet,
    artista_list,
    artista_detail,
    painel_principal,
    painel_artes,
    painel_colecoes,
    painel_arte_nova,
    painel_arte_editar,
    painel_arte_status,
    painel_colecao_nova,
    painel_colecao_editar,
    painel_colecao_status,
)

router = DefaultRouter()
router.register(r'artistas', ArtistaViewSet)

urlpatterns = [
    # Paginas publicas
    path('', artista_list, name='artista-list'),
    path('<int:pk>/', artista_detail, name='artista-detail'),

    # Painel do Artista — visao geral
    path('painel/', painel_principal, name='painel-principal'),
    path('painel/artes/', painel_artes, name='painel-artes'),
    path('painel/colecoes/', painel_colecoes, name='painel-colecoes'),

    # Painel do Artista — CRUD de Artes
    path('painel/artes/nova/', painel_arte_nova, name='painel-arte-nova'),
    path('painel/artes/<int:pk>/editar/', painel_arte_editar, name='painel-arte-editar'),
    path('painel/artes/<int:pk>/status/', painel_arte_status, name='painel-arte-status'),

    # Painel do Artista — CRUD de Colecoes
    path('painel/colecoes/nova/', painel_colecao_nova, name='painel-colecao-nova'),
    path('painel/colecoes/<int:pk>/editar/', painel_colecao_editar, name='painel-colecao-editar'),
    path('painel/colecoes/<int:pk>/status/', painel_colecao_status, name='painel-colecao-status'),

    # API REST
    path('api/', include(router.urls)),
]
