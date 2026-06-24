from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArtistaViewSet,
    artista_list,
    artista_detail,
    painel_principal,
    painel_artes,
    painel_colecoes,
)

router = DefaultRouter()
router.register(r'artistas', ArtistaViewSet)

urlpatterns = [
    # Páginas públicas
    path('', artista_list, name='artista-list'),
    path('<int:pk>/', artista_detail, name='artista-detail'),

    # Painel do Artista (protegido)
    path('painel/', painel_principal, name='painel-principal'),
    path('painel/artes/', painel_artes, name='painel-artes'),
    path('painel/colecoes/', painel_colecoes, name='painel-colecoes'),

    # API REST
    path('api/', include(router.urls)),
]
