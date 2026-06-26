"""
Testes automatizados para o app Creations.
Cobre: artes, personalizações, permissões, validações, editor visual.
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

    def test_criar_personalizacao_produto_inativo_retorna_404(self):
        """Produto inativo não deve abrir o editor."""
        produto_inativo = criar_produto("Produto Inativo", ativo=False)
        self.client.force_login(self.usuario)
        url = reverse("personalizacao-criar") + f"?produto={produto_inativo.pk}&arte={self.arte.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_criar_personalizacao_arte_inativa_retorna_404(self):
        """Arte inativa não deve abrir o editor."""
        arte_inativa = Arte.objects.create(
            artista=self.artista,
            nome="Arte Inativa Editor",
            arquivo="artes/inativa_e.jpg",
            ativa=False,
        )
        self.client.force_login(self.usuario)
        url = reverse("personalizacao-criar") + f"?produto={self.produto.pk}&arte={arte_inativa.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


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
        self.url_salvar = reverse("personalizacao-salvar")

    def _post(self, extra=None):
        """Helper: POST ao endpoint de salvar com dados base."""
        dados = {
            "produto_id": self.produto.pk,
            "arte_id": self.arte.pk,
            "texto": "Meu nome",
            "fonte": "Arial",
            "cor": "#FF0000",
            "tamanho_fonte": "24",
            "posicao_x": "50",
            "posicao_y": "50",
            "observacoes": "",
            "quantidade": "1",
            "preco_extra": "5.00",
        }
        if extra:
            dados.update(extra)
        return self.client.post(self.url_salvar, dados)

    def test_salvar_personalizacao_sem_login_redireciona(self):
        response = self._post()
        self.assertIn(response.status_code, [302, 301])
        self.assertIn("login", response["Location"])

    def test_salvar_personalizacao_com_dados_validos(self):
        self.client.force_login(self.usuario)
        response = self._post()
        # Deve redirecionar para adição ao carrinho
        self.assertEqual(response.status_code, 302)
        self.assertIn("/carrinho/adicionar/", response["Location"])

    def test_salvamento_persiste_campos(self):
        self.client.force_login(self.usuario)
        self._post({"texto": "Texto Único", "fonte": "Georgia", "cor": "#0000FF"})
        p = Personalizacao.objects.filter(texto="Texto Único").first()
        self.assertIsNotNone(p)
        self.assertEqual(p.fonte, "Georgia")
        self.assertEqual(p.cor, "#0000FF")

    def test_salvamento_persiste_novos_campos(self):
        """Novos campos (tamanho, posicao_x/y, observacoes, usuario) são salvos corretamente."""
        self.client.force_login(self.usuario)
        self._post({
            "texto": "Novo Editor",
            "tamanho_fonte": "36",
            "posicao_x": "25",
            "posicao_y": "75",
            "observacoes": "Atenção: usar tinta preta",
        })
        p = Personalizacao.objects.filter(texto="Novo Editor").first()
        self.assertIsNotNone(p)
        self.assertEqual(p.tamanho_fonte, 36)
        self.assertEqual(p.posicao_x, 25)
        self.assertEqual(p.posicao_y, 75)
        self.assertEqual(p.observacoes, "Atenção: usar tinta preta")
        self.assertEqual(p.usuario, self.usuario)

    def test_salvar_com_produto_inativo_retorna_404(self):
        produto_inativo = criar_produto("Produto Inativo", ativo=False)
        self.client.force_login(self.usuario)
        response = self._post({"produto_id": produto_inativo.pk})
        self.assertEqual(response.status_code, 404)

    def test_salvar_com_arte_inativa_retorna_404(self):
        arte_inativa = Arte.objects.create(
            artista=self.artista,
            nome="Arte Inativa Salvar",
            arquivo="artes/inativa_s.jpg",
            ativa=False,
        )
        self.client.force_login(self.usuario)
        response = self._post({"arte_id": arte_inativa.pk})
        self.assertEqual(response.status_code, 404)

    def test_bloqueia_cor_invalida(self):
        """Cor fora do padrão hex deve renderizar a página com erro, sem criar personalização."""
        self.client.force_login(self.usuario)
        count_antes = Personalizacao.objects.count()
        response = self._post({"texto": "teste_cor", "cor": "not-a-color"})
        # Deve retornar 200 (formulário com erro) ou 302 com mensagem de erro
        self.assertNotEqual(response.status_code, 404)
        count_depois = Personalizacao.objects.count()
        self.assertEqual(count_antes, count_depois, "Não deve criar personalização com cor inválida")

    def test_bloqueia_tamanho_fonte_invalido_pequeno(self):
        """Tamanho de fonte menor que 8 deve ser rejeitado."""
        self.client.force_login(self.usuario)
        count_antes = Personalizacao.objects.count()
        self._post({"tamanho_fonte": "3"})
        self.assertEqual(Personalizacao.objects.count(), count_antes)

    def test_bloqueia_tamanho_fonte_invalido_grande(self):
        """Tamanho de fonte maior que 72 deve ser rejeitado."""
        self.client.force_login(self.usuario)
        count_antes = Personalizacao.objects.count()
        self._post({"tamanho_fonte": "200"})
        self.assertEqual(Personalizacao.objects.count(), count_antes)

    def test_bloqueia_posicao_x_invalida(self):
        """Posição X fora de 0-100 deve ser rejeitada."""
        self.client.force_login(self.usuario)
        count_antes = Personalizacao.objects.count()
        self._post({"posicao_x": "150"})
        self.assertEqual(Personalizacao.objects.count(), count_antes)

    def test_bloqueia_posicao_y_invalida(self):
        """Posição Y fora de 0-100 deve ser rejeitada."""
        self.client.force_login(self.usuario)
        count_antes = Personalizacao.objects.count()
        self._post({"posicao_y": "-10"})
        self.assertEqual(Personalizacao.objects.count(), count_antes)

    def test_bloqueia_quantidade_menor_que_1(self):
        """Quantidade menor que 1 deve ser rejeitada."""
        self.client.force_login(self.usuario)
        count_antes = Personalizacao.objects.count()
        self._post({"quantidade": "0"})
        self.assertEqual(Personalizacao.objects.count(), count_antes)

    def test_redireciona_para_carrinho_apos_salvar(self):
        """Após salvar, deve redirecionar para a URL de adicionar ao carrinho."""
        self.client.force_login(self.usuario)
        response = self._post()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/carrinho/adicionar/", response["Location"])

    def test_carrinho_recebe_personalizacao_correta(self):
        """O item adicionado ao carrinho referencia a personalização criada."""
        self.client.force_login(self.usuario)
        response = self._post({"texto": "Para Carrinho"})
        # Segue o redirect para o carrinho
        self.client.get(response["Location"])
        from cart.models import ItemCarrinho
        p = Personalizacao.objects.filter(texto="Para Carrinho").first()
        self.assertIsNotNone(p)
        item = ItemCarrinho.objects.filter(personalizacao=p).first()
        self.assertIsNotNone(item)

    def test_carrinho_recebe_quantidade_correta(self):
        """A quantidade escolhida no editor chega corretamente ao item do carrinho."""
        self.client.force_login(self.usuario)
        response = self._post({"texto": "Qtd Tres", "quantidade": "3"})
        self.client.get(response["Location"])
        from cart.models import ItemCarrinho
        p = Personalizacao.objects.filter(texto="Qtd Tres").first()
        self.assertIsNotNone(p)
        item = ItemCarrinho.objects.filter(personalizacao=p).first()
        self.assertIsNotNone(item)
        self.assertEqual(item.quantidade, 3)

    def test_preview_nao_quebra_sem_imagem(self):
        """O editor deve carregar sem erro mesmo que produto e arte não tenham imagem."""
        self.client.force_login(self.usuario)
        url = reverse("personalizacao-criar") + f"?produto={self.produto.pk}&arte={self.arte.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
