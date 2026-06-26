"""
Forms do Painel do Artista.

ArteForm  — criação/edição de Arte com queryset de coleção filtrado por artista.
ColecaoForm — criação/edição de Coleção.
"""
from django import forms
from creations.models import Arte, Colecao


class ArteForm(forms.ModelForm):
    """
    Formulário para criação e edição de Arte.
    O queryset do campo 'colecao' é restrito às coleções do artista logado
    via set_artista(), chamado na view após instanciar o form.
    """

    class Meta:
        model = Arte
        fields = ['nome', 'arquivo', 'descricao', 'colecao', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control form-control-dark',
                'placeholder': 'Ex.: Horizonte Urbano',
                'id': 'id_nome_arte',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control form-control-dark',
                'rows': 4,
                'placeholder': 'Descreva sua arte (opcional)...',
                'id': 'id_descricao_arte',
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control form-control-dark',
                'accept': 'image/*',
                'id': 'id_arquivo_arte',
            }),
            'colecao': forms.Select(attrs={
                'class': 'form-select form-select-dark',
                'id': 'id_colecao_arte',
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_ativa_arte',
            }),
        }
        labels = {
            'nome': 'Nome da Arte',
            'arquivo': 'Imagem da Arte',
            'descricao': 'Descrição',
            'colecao': 'Coleção (opcional)',
            'ativa': 'Arte ativa (visível no catálogo)',
        }
        error_messages = {
            'nome': {'required': 'O nome da arte é obrigatório.'},
            'arquivo': {'required': 'A imagem da arte é obrigatória.'},
        }

    def set_artista(self, artista):
        """Filtra coleções para mostrar apenas as do artista logado."""
        if artista:
            self.fields['colecao'].queryset = Colecao.objects.filter(
                artista=artista, ativa=True
            )
        else:
            self.fields['colecao'].queryset = Colecao.objects.none()
        # Campo vazio para "sem coleção"
        self.fields['colecao'].empty_label = '— Sem coleção —'
        self.fields['colecao'].required = False


class ColecaoForm(forms.ModelForm):
    """
    Formulário para criação e edição de Coleção.
    """

    class Meta:
        model = Colecao
        fields = ['nome', 'descricao', 'imagem_destaque', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control form-control-dark',
                'placeholder': 'Ex.: Natureza & Abstrato',
                'id': 'id_nome_colecao',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control form-control-dark',
                'rows': 4,
                'placeholder': 'Descreva a coleção (opcional)...',
                'id': 'id_descricao_colecao',
            }),
            'imagem_destaque': forms.FileInput(attrs={
                'class': 'form-control form-control-dark',
                'accept': 'image/*',
                'id': 'id_imagem_destaque_colecao',
            }),
            'ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_ativa_colecao',
            }),
        }
        labels = {
            'nome': 'Nome da Coleção',
            'descricao': 'Descrição',
            'imagem_destaque': 'Imagem de Capa (opcional)',
            'ativa': 'Coleção ativa (visível no catálogo)',
        }
        error_messages = {
            'nome': {'required': 'O nome da coleção é obrigatório.'},
        }
