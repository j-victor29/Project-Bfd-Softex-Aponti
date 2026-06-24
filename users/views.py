from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import make_password, check_password
from typing import Optional
from .models import user
from .serializers import UserListSerializer, UserDetailSerializer, UserCreateSerializer


def user_list_view(request):
    """View de template para listar usuários"""
    users = user.objects.all()
    return render(request, 'users/user_list.html', {'users': users})


class UserViewSet(viewsets.ModelViewSet):
    queryset = user.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_usuario_autenticado(self, request) -> Optional['user']:
        """Obtém o usuário autenticado do modelo customizado"""
        try:
            return user.objects.get(email=request.user.email)
        except user.DoesNotExist:
            return None
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        return UserListSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def perfil(self, request):
        """Retorna dados do usuário autenticado"""
        usuario = self.get_usuario_autenticado(request)
        if not usuario:
            return Response(
                {'erro': 'Usuário não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = UserDetailSerializer(usuario)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def alterar_senha(self, request):
        """Altera a senha do usuário autenticado"""
        usuario = self.get_usuario_autenticado(request)
        if not usuario:
            return Response(
                {'erro': 'Usuário não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        senha_atual = request.data.get('senha_atual')
        senha_nova = request.data.get('senha_nova')
        
        if not senha_atual or not senha_nova:
            return Response(
                {'erro': 'Senha atual e nova são obrigatórias'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not usuario.check_password(senha_atual):
            return Response(
                {'erro': 'Senha atual incorreta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario.set_password(senha_nova)
        usuario.save()
        return Response({'mensagem': 'Senha alterada com sucesso'})


@login_required
def perfil_view(request):
    return render(request, 'users/perfil.html', {'user': request.user})
