"""
Testes automatizados para o app Creations.
Cobre: artes, personalizações, permissões, validações.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Produto
from artists.models import Artista
from creations.models import Arte, Colecao, Personalizacao

User = get_user_model()


def criar_usuario(email="usuario@teste.com", nome="Usuário Teste", senha="senha123"):
    return User.objects.create_user(email=email, nome=nome, password=senha)


def criar_artista(usuario):
    return Artista.objects.create(
        usuario=usuario,
        nome_artistico="Artista Teste",
        status_aprovacao="aprovado",
        ativo=True,
    )


def criar_produto(nome="Capinha Teste", ativo=True):
    return Produto.objects.create(
        nome=nome,
        categoria="capinha",
        preco_base="49.90",
        estoque=10,
        ativo=ativo,
    )


class ArteListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario("artista@teste.com", "Artista")
        self.artista = criar_artista(self.usuario)
        self.colecao = Colecao.objects.create(
            artista=self.artista,
            nome="Coleção Verão",
            ativa=True,
        )
        self.arte = Arte.objects.create(
            artista=self.artista,
            colecao=self.colecao,
            nome="Arte Floral",
            arquivo="artes/teste.jpg",
            ativa=True,
        )

    def test_listagem_artes_retorna_200(self):
        response = self.client.get(reverse("arte-list"))
        self.assertEqual(response.status_code, 200)

    def test_listagem_contem_arte_ativa(self):
        response = self.client.get(reverse("arte-list"))
        self.assertContains(response, "Arte Floral")

    def test_arte_inativa_nao_aparece(self):
        Arte.objects.create(
            artista=self.artista,
            nome="Arte Inativa",
            arquivo="artes/inativa.jpg",
            ativa=False,
        )
        response = self.client.get(reverse("arte-list"))
        self.assertNotContains(response, "Arte Inativa")


class PersonalizacaoCriarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.artista_user = criar_usuario("artista2@teste.com", "Artista 2")
        self.artista = criar_artista(self.artista_user)
        self.produto = criar_produto()
        self.arte = Arte.objects.create(
            artista=self.artista,
            nome="Arte Digital",
            arquivo="artes/digital.jpg",
            ativa=True,
        )

    def test_criar_personalizacao_sem_login_redireciona(self):
        """Usuário anônimo deve ser redirecionado para login."""
        url = reverse("personalizacao-criar") + f"?produto={self.produto.pk}&arte={self.arte.pk}"
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])
        self.assertIn("login", response["Location"])

    def test_criar_personalizacao_com_produto_e_arte_validos(self):
        self.client.force_login(self.usuario)
        url = reverse("personalizacao-criar") + f"?produto={self.produto.pk}&arte={self.arte.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_criar_personalizacao_produto_invalido_redireciona(self):
        self.client.force_login(self.usuario)
        url = reverse("personalizacao-criar") + f"?produto=99999&arte={self.arte.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_criar_personalizacao_arte_invalida_redireciona(self):
        self.client.force_login(self.usuario)
        url = reverse("personalizacao-criar") + f"?produto={self.produto.pk}&arte=99999"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_criar_personalizacao_sem_produto_e_arte_redireciona(self):
        self.client.force_login(self.usuario)
        url = reverse("personalizacao-criar")
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])


class PersonalizacaoSalvarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.artista_user = criar_usuario("artista3@teste.com", "Artista 3")
        self.artista = criar_artista(self.artista_user)
        self.produto = criar_produto()
        self.arte = Arte.objects.create(
            artista=self.artista,
            nome="Arte Salvar",
            arquivo="artes/salvar.jpg",
            ativa=True,
        )

    def test_salvar_personalizacao_sem_login_redireciona(self):
        response = self.client.post(reverse("personalizacao-salvar"), {
            "produto_id": self.produto.pk,
            "arte_id": self.arte.pk,
            "texto": "Meu nome",
            "fonte": "Arial",
            "cor": "#FF0000",
        })
        self.assertIn(response.status_code, [302, 301])
        self.assertIn("login", response["Location"])

    def test_salvar_personalizacao_com_dados_validos(self):
        self.client.force_login(self.usuario)
        response = self.client.post(reverse("personalizacao-salvar"), {
            "produto_id": self.produto.pk,
            "arte_id": self.arte.pk,
            "texto": "Meu nome",
            "fonte": "Arial",
            "cor": "#FF0000",
            "preco_extra": "0",
        })
        # Deve redirecionar para criação de pedido
        self.assertEqual(response.status_code, 302)
        self.assertIn("criar-do-item", response["Location"])

    def test_salvamento_persiste_campos(self):
        self.client.force_login(self.usuario)
        self.client.post(reverse("personalizacao-salvar"), {
            "produto_id": self.produto.pk,
            "arte_id": self.arte.pk,
            "texto": "Texto Único",
            "fonte": "Georgia",
            "cor": "#0000FF",
            "preco_extra": "5.00",
        })
        p = Personalizacao.objects.filter(texto="Texto Único").first()
        self.assertIsNotNone(p)
        self.assertEqual(p.fonte, "Georgia")
        self.assertEqual(p.cor, "#0000FF")

    def test_salvar_com_produto_inativo_retorna_404(self):
        produto_inativo = criar_produto("Produto Inativo", ativo=False)
        self.client.force_login(self.usuario)
        response = self.client.post(reverse("personalizacao-salvar"), {
            "produto_id": produto_inativo.pk,
            "arte_id": self.arte.pk,
            "texto": "Teste",
        })
        self.assertEqual(response.status_code, 404)

    def test_salvar_com_arte_inativa_retorna_404(self):
        arte_inativa = Arte.objects.create(
            artista=self.artista,
            nome="Arte Inativa Salvar",
            arquivo="artes/inativa_s.jpg",
            ativa=False,
        )
        self.client.force_login(self.usuario)
        response = self.client.post(reverse("personalizacao-salvar"), {
            "produto_id": self.produto.pk,
            "arte_id": arte_inativa.pk,
            "texto": "Teste",
        })
        self.assertEqual(response.status_code, 404)
