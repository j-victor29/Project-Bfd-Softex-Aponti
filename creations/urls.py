from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ColecaoViewSet, 
    ArteViewSet, 
    PersonalizacaoViewSet,
    api_root_view,
    colecao_list_view,
    colecao_detail_view,
    arte_list_view,
    arte_detail_view,
    personalizacao_list_view,
    personalizacao_criar_view,
    personalizacao_salvar_view,
)

router = DefaultRouter()
router.register(r'artes', ArteViewSet, basename='api-arte')
router.register(r'colecoes', ColecaoViewSet, basename='api-colecao')
router.register(r'personalizacoes', PersonalizacaoViewSet, basename='api-personalizacao')

urlpatterns = [
    # Página inicial (API Root)
    path('', api_root_view, name='creations-home'),
    
    # HTML Templates
    path('colecoes/', colecao_list_view, name='colecao-list'),
    path('colecoes/<int:pk>/', colecao_detail_view, name='colecao-detail'),
    path('artes/', arte_list_view, name='arte-list'),
    path('artes/<int:pk>/', arte_detail_view, name='arte-detail'),
    path('personalizacoes/', personalizacao_list_view, name='personalizacao-list'),
    path('personalizar/', personalizacao_criar_view, name='personalizacao-criar'),
    path('personalizar/salvar/', personalizacao_salvar_view, name='personalizacao-salvar'),
    
    # API REST
    path('api/', include(router.urls)),
]