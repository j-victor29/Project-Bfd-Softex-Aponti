from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, user_list_view, perfil_view

router = DefaultRouter()
router.register(r'api', UserViewSet, basename='user')

urlpatterns = [
    path('', user_list_view, name='user_list'),
    path('perfil/', perfil_view, name='user-profile'),
    path('api/', include(router.urls)),
]