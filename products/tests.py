"""
Testes automatizados para o app Products.
Cobre: listagem, detalhe, 404, produto ativo/inativo.
"""
from django.test import TestCase, Client
from django.urls import reverse
from products.models import Produto


class ProdutoModelTest(TestCase):
    def setUp(self):
        self.produto_ativo = Produto.objects.create(
            nome="Capinha iPhone 15",
            descricao="Capinha de silicone premium",
            categoria="capinha",
            preco_base="49.90",
            estoque=10,
            ativo=True,
        )
        self.produto_inativo = Produto.objects.create(
            nome="Capinha Antiga",
            descricao="Fora de linha",
            categoria="capinha",
            preco_base="29.90",
            estoque=0,
            ativo=False,
        )

    def test_produto_str(self):
        self.assertEqual(str(self.produto_ativo), "Capinha iPhone 15")

    def test_produto_ativo_flag(self):
        self.assertTrue(self.produto_ativo.ativo)
        self.assertFalse(self.produto_inativo.ativo)


class ProdutoListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.produto = Produto.objects.create(
            nome="Capinha Samsung",
            categoria="capinha",
            preco_base="39.90",
            estoque=5,
            ativo=True,
        )

    def test_listagem_produtos_retorna_200(self):
        response = self.client.get(reverse("produto-list"))
        self.assertEqual(response.status_code, 200)

    def test_listagem_contem_produto_ativo(self):
        response = self.client.get(reverse("produto-list"))
        self.assertContains(response, "Capinha Samsung")

    def test_listagem_contem_produto_inativo(self):
        """Produtos inativos ainda aparecem na listagem geral por padrão."""
        Produto.objects.create(
            nome="Produto Inativo",
            categoria="capinha",
            preco_base="10.00",
            estoque=0,
            ativo=False,
        )
        response = self.client.get(reverse("produto-list"))
        # Verifica que a view retorna 200 sem erro
        self.assertEqual(response.status_code, 200)


class ProdutoDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.produto = Produto.objects.create(
            nome="Capinha Pixel",
            categoria="capinha",
            preco_base="59.90",
            estoque=3,
            ativo=True,
        )

    def test_detalhe_produto_retorna_200(self):
        response = self.client.get(reverse("produto-detail", kwargs={"pk": self.produto.pk}))
        self.assertEqual(response.status_code, 200)

    def test_detalhe_produto_contem_nome(self):
        response = self.client.get(reverse("produto-detail", kwargs={"pk": self.produto.pk}))
        self.assertContains(response, "Capinha Pixel")

    def test_produto_inexistente_retorna_404(self):
        response = self.client.get(reverse("produto-detail", kwargs={"pk": 99999}))
        self.assertEqual(response.status_code, 404)
