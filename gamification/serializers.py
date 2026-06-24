from rest_framework import serializers
from .models import Recompensa, UsuarioRecompensa, Ranking


class RecompensaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recompensa
        fields = [
            'id',
            'nome',
            'descricao',
            'tipo',
        ]

class UsuarioRecompensaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioRecompensa
        fields = [
            'id',
            'usuario',
            'recompensa',
            'data_recompensa',
        ]
        read_only_fields = ['data_recompensa']


class RankingSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    
    class Meta:
        model = Ranking
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'usuario_email',
            'tipo',
            'posicao',
            'pontos',
            'mes',
            'atualizado_em',
        ]
        read_only_fields = ['atualizado_em']
