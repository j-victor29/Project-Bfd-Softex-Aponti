from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArtistaViewSet, artista_list, artista_detail

router = DefaultRouter()
router.register(r'artistas', ArtistaViewSet)

urlpatterns = [
    path('', artista_list, name='artista-list'),
    path('<int:pk>/', artista_detail, name='artista-detail'),
    path('api/', include(router.urls)),
]
