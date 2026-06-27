"""
Testes automatizados para o app Payments.
Cobre: simulação de pagamento, métodos válidos/inválidos,
       bloqueios de estado, atualização sincronizada.
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Produto
from artists.models import Artista
from creations.models import Arte, Personalizacao
from orders.models import Pedido
from orders.services import PedidoService
from payments.models import Payment

User = get_user_model()


def criar_usuario(email="pag_user@teste.com", nome="Pag User", senha="senha123"):
    return User.objects.create_user(email=email, nome=nome, password=senha)


def criar_artista(usuario):
    return Artista.objects.create(
        usuario=usuario,
        nome_artistico="Artista Pag",
        status_aprovacao="aprovado",
        ativo=True,
    )


def criar_produto():
    return Produto.objects.create(
        nome="GreenCase Pag",
        categoria="capinha",
        preco_base=Decimal("49.90"),
        estoque=10,
        ativo=True,
    )


def criar_setup_pedido():
    usuario = criar_usuario()
    artista_user = criar_usuario("artista_pag@t.com", "Artista Pag")
    artista = criar_artista(artista_user)
    produto = criar_produto()
    arte = Arte.objects.create(
        artista=artista,
        nome="Arte Pag",
        arquivo="artes/pag.jpg",
        ativa=True,
    )
    personalizacao = Personalizacao.objects.create(
        produto=produto,
        arte=arte,
        texto="Teste Pag",
    )
    pedido = PedidoService.criar_pedido(usuario, artista)
    PedidoService.adicionar_item(
        pedido=pedido,
        produto=produto,
        personalizacao=personalizacao,
        quantidade=1,
        preco_unitario=Decimal("49.90"),
    )
    return usuario, artista, produto, arte, personalizacao, pedido


class SimularPagamentoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        (
            self.usuario,
            self.artista,
            self.produto,
            self.arte,
            self.personalizacao,
            self.pedido,
        ) = criar_setup_pedido()

    def test_pagamento_sem_login_redireciona(self):
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 301])
        self.assertIn("login", response["Location"])

    def test_tela_pagamento_retorna_200(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_pagamento_com_pix(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.post(url, {"method": "pix"})
        self.assertEqual(response.status_code, 302)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status_pedido, "pago")

    def test_pagamento_com_cartao_credito(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.post(url, {"method": "credit_card"})
        self.assertEqual(response.status_code, 302)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status_pedido, "pago")

    def test_pagamento_com_cartao_debito(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.post(url, {"method": "debit_card"})
        self.assertEqual(response.status_code, 302)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status_pedido, "pago")

    def test_pagamento_metodo_invalido_redireciona(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.post(url, {"method": "criptomoeda"})
        # Deve redirecionar com mensagem de erro, não mudar status do pedido
        self.assertEqual(response.status_code, 302)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status_pedido, "criado")

    def test_pagamento_duplicado_nao_recria_payment(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        self.client.post(url, {"method": "pix"})
        self.client.post(url, {"method": "pix"})
        # Payment é OneToOne, deve haver apenas 1 registro
        count = Payment.objects.filter(pedido=self.pedido).count()
        self.assertEqual(count, 1)

    def test_pagamento_pedido_ja_pago_redireciona(self):
        """Tentar pagar um pedido já pago deve redirecionar sem criar novo pagamento."""
        PedidoService.confirmar_pagamento(self.pedido, "pix", "confirmado")
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_pagamento_pedido_cancelado_redireciona(self):
        PedidoService.cancelar_pedido(self.pedido)
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_status_payment_e_pedido_sincronizados(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": self.pedido.pk})
        self.client.post(url, {"method": "pix"})
        self.pedido.refresh_from_db()
        payment = Payment.objects.get(pedido=self.pedido)
        self.assertEqual(payment.status, "paid")
        self.assertEqual(self.pedido.status_pedido, "pago")

    def test_pagamento_pedido_inexistente_retorna_404(self):
        self.client.force_login(self.usuario)
        url = reverse("payments:simular-pagamento", kwargs={"pedido_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
