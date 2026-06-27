"""
Testes automatizados para o app Orders.
Cobre: criação de pedido, status, privacidade, duplicidade.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Produto
from artists.models import Artista
from creations.models import Arte, Personalizacao
from orders.models import Pedido, ItemPedido
from orders.services import PedidoService

User = get_user_model()


def criar_usuario(email="usuario@teste.com", nome="Usuário Teste", senha="senha123", staff=False):
    u = User.objects.create_user(email=email, nome=nome, password=senha)
    if staff:
        u.is_staff = True
        u.save()
    return u


def criar_artista(usuario):
    return Artista.objects.create(
        usuario=usuario,
        nome_artistico="Artista Teste",
        status_aprovacao="aprovado",
        ativo=True,
    )


def criar_produto(nome="GreenCase Teste"):
    return Produto.objects.create(
        nome=nome,
        categoria="capinha",
        preco_base=Decimal("49.90"),
        estoque=10,
        ativo=True,
    )


def criar_setup_base():
    """Cria usuário, artista, produto, arte e personalização para testes."""
    usuario = criar_usuario()
    artista_user = criar_usuario("artista@t.com", "Artista")
    artista = criar_artista(artista_user)
    produto = criar_produto()
    arte = Arte.objects.create(
        artista=artista,
        nome="Arte Base",
        arquivo="artes/base.jpg",
        ativa=True,
    )
    personalizacao = Personalizacao.objects.create(
        produto=produto,
        arte=arte,
        texto="Minha GreenCase",
        fonte="Arial",
        cor="#FF0000",
    )
    return usuario, artista, produto, arte, personalizacao


class PedidoCriacaoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario, self.artista, self.produto, self.arte, self.personalizacao = criar_setup_base()

    def test_criar_pedido_sem_login_redireciona(self):
        url = reverse("orders:criar-do-item") + f"?personalizacao={self.personalizacao.pk}"
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])
        self.assertIn("login", response["Location"])

    def test_criar_pedido_com_login(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:criar-do-item") + f"?personalizacao={self.personalizacao.pk}"
        response = self.client.get(url)
        # Deve redirecionar para detalhe do pedido criado
        self.assertEqual(response.status_code, 302)
        # Pedido foi criado
        self.assertEqual(Pedido.objects.filter(usuario=self.usuario).count(), 1)

    def test_pedido_vinculado_ao_usuario_logado(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:criar-do-item") + f"?personalizacao={self.personalizacao.pk}"
        self.client.get(url)
        pedido = Pedido.objects.filter(usuario=self.usuario).first()
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.usuario, self.usuario)

    def test_status_inicial_pedido_e_criado(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:criar-do-item") + f"?personalizacao={self.personalizacao.pk}"
        self.client.get(url)
        pedido = Pedido.objects.filter(usuario=self.usuario).first()
        self.assertEqual(pedido.status_pedido, "criado")

    def test_item_pedido_vinculado_a_personalizacao(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:criar-do-item") + f"?personalizacao={self.personalizacao.pk}"
        self.client.get(url)
        pedido = Pedido.objects.filter(usuario=self.usuario).first()
        self.assertEqual(pedido.itens.count(), 1)
        item = pedido.itens.first()
        self.assertEqual(item.personalizacao, self.personalizacao)

    def test_prevencao_pedido_duplicado(self):
        """Criar o mesmo pedido duas vezes deve redirecionar para o existente."""
        self.client.force_login(self.usuario)
        url = reverse("orders:criar-do-item") + f"?personalizacao={self.personalizacao.pk}"
        self.client.get(url)
        self.client.get(url)
        # Deve haver apenas 1 pedido
        self.assertEqual(Pedido.objects.filter(usuario=self.usuario).count(), 1)

    def test_personalizacao_inexistente_retorna_404(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:criar-do-item") + "?personalizacao=99999"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_personalizacao_id_invalido_redireciona(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:criar-do-item") + "?personalizacao=abc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class PedidoListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario, self.artista, self.produto, self.arte, self.personalizacao = criar_setup_base()
        self.outro_usuario = criar_usuario("outro@teste.com", "Outro")

    def test_lista_pedidos_sem_login_redireciona(self):
        response = self.client.get(reverse("orders:pedido-list"))
        self.assertIn(response.status_code, [302, 301])

    def test_usuario_ve_apenas_seus_pedidos(self):
        # Criar pedido para usuario
        pedido_usuario = PedidoService.criar_pedido(self.usuario, self.artista)
        # Criar pedido para outro_usuario
        PedidoService.criar_pedido(self.outro_usuario, self.artista)

        self.client.force_login(self.usuario)
        response = self.client.get(reverse("orders:pedido-list"))
        self.assertEqual(response.status_code, 200)

        pedidos_no_context = response.context["pedidos"]
        for p in pedidos_no_context:
            self.assertEqual(p.usuario, self.usuario)


class PedidoDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario, self.artista, self.produto, self.arte, self.personalizacao = criar_setup_base()
        self.outro_usuario = criar_usuario("outro2@teste.com", "Outro2")
        self.pedido = PedidoService.criar_pedido(self.usuario, self.artista)

    def test_detalhe_pedido_proprio_retorna_200(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse("orders:pedido-detail", kwargs={"pk": self.pedido.pk}))
        self.assertEqual(response.status_code, 200)

    def test_usuario_nao_pode_ver_pedido_de_outro(self):
        self.client.force_login(self.outro_usuario)
        response = self.client.get(reverse("orders:pedido-detail", kwargs={"pk": self.pedido.pk}))
        self.assertEqual(response.status_code, 404)


class PedidoServiceTest(TestCase):
    def setUp(self):
        self.usuario, self.artista, self.produto, self.arte, self.personalizacao = criar_setup_base()

    def test_criar_pedido_via_service(self):
        pedido = PedidoService.criar_pedido(self.usuario, self.artista)
        self.assertEqual(pedido.status_pedido, "criado")
        self.assertEqual(pedido.usuario, self.usuario)

    def test_adicionar_item_ao_pedido(self):
        pedido = PedidoService.criar_pedido(self.usuario, self.artista)
        item = PedidoService.adicionar_item(
            pedido=pedido,
            produto=self.produto,
            personalizacao=self.personalizacao,
            quantidade=1,
            preco_unitario=Decimal("49.90"),
        )
        self.assertEqual(item.produto, self.produto)
        self.assertEqual(item.subtotal, Decimal("49.90"))

    def test_confirmar_pagamento_muda_status(self):
        pedido = PedidoService.criar_pedido(self.usuario, self.artista)
        PedidoService.adicionar_item(pedido, self.produto, self.personalizacao, 1, Decimal("49.90"))
        pedido = PedidoService.confirmar_pagamento(pedido, "pix", "confirmado")
        pedido.refresh_from_db()
        self.assertEqual(pedido.status_pedido, "pago")

    def test_nao_pode_pagar_pedido_ja_pago(self):
        pedido = PedidoService.criar_pedido(self.usuario, self.artista)
        PedidoService.adicionar_item(pedido, self.produto, self.personalizacao, 1, Decimal("49.90"))
        PedidoService.confirmar_pagamento(pedido, "pix", "confirmado")
        with self.assertRaises(ValueError):
            PedidoService.confirmar_pagamento(pedido, "pix", "confirmado")

    def test_nao_pode_pagar_pedido_cancelado(self):
        pedido = PedidoService.criar_pedido(self.usuario, self.artista)
        PedidoService.adicionar_item(pedido, self.produto, self.personalizacao, 1, Decimal("49.90"))
        PedidoService.cancelar_pedido(pedido)
        with self.assertRaises(ValueError):
            PedidoService.confirmar_pagamento(pedido, "pix", "confirmado")

    def test_transicao_status_invalida_levanta_excecao(self):
        pedido = PedidoService.criar_pedido(self.usuario, self.artista)
        with self.assertRaises(ValueError):
            PedidoService.marcar_como_impresso(pedido)

    def test_pode_mudar_status_valida_transicoes(self):
        pedido = PedidoService.criar_pedido(self.usuario, self.artista)
        self.assertTrue(pedido.pode_mudar_status("pago"))
        self.assertTrue(pedido.pode_mudar_status("cancelado"))
        self.assertFalse(pedido.pode_mudar_status("impresso"))
        self.assertFalse(pedido.pode_mudar_status("em_producao"))
