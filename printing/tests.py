"""
Testes automatizados para o app Printing.
Cobre: permissões, fila, transições de status, regras de negócio.
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
from printing.models import Impressora, FilaImpressao

User = get_user_model()


def criar_usuario(email="print_user@teste.com", nome="Print User", senha="senha123", staff=False):
    u = User.objects.create_user(email=email, nome=nome, password=senha)
    if staff:
        u.is_staff = True
        u.save()
    return u


def criar_artista(usuario):
    return Artista.objects.create(
        usuario=usuario,
        nome_artistico="Artista Print",
        status_aprovacao="aprovado",
        ativo=True,
    )


def criar_produto():
    return Produto.objects.create(
        nome="GreenCase Print",
        categoria="capinha",
        preco_base=Decimal("49.90"),
        estoque=10,
        ativo=True,
    )


def criar_impressora():
    return Impressora.objects.create(
        nome="Impressora UV-01",
        tipo="uv",
        status="ativo",
    )


def criar_setup_pedido_pago():
    usuario = criar_usuario()
    artista_user = criar_usuario("artista_pr@t.com", "Artista Print")
    artista = criar_artista(artista_user)
    produto = criar_produto()
    arte = Arte.objects.create(
        artista=artista,
        nome="Arte Print",
        arquivo="artes/print.jpg",
        ativa=True,
    )
    personalizacao = Personalizacao.objects.create(
        produto=produto,
        arte=arte,
        texto="GreenCase Print",
    )
    pedido = PedidoService.criar_pedido(usuario, artista)
    PedidoService.adicionar_item(
        pedido=pedido,
        produto=produto,
        personalizacao=personalizacao,
        quantidade=1,
        preco_unitario=Decimal("49.90"),
    )
    PedidoService.confirmar_pagamento(pedido, "pix", "confirmado")
    return usuario, artista, produto, pedido


class FilaImpressaoPermissaoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario_comum = criar_usuario()
        self.usuario_staff = criar_usuario("staff@t.com", "Staff", staff=True)

    def test_usuario_anonimo_e_redirecionado_da_fila(self):
        response = self.client.get(reverse("printing:fila-lista"))
        self.assertIn(response.status_code, [302, 301])

    def test_usuario_comum_recebe_403_na_fila(self):
        self.client.force_login(self.usuario_comum)
        response = self.client.get(reverse("printing:fila-lista"))
        self.assertEqual(response.status_code, 403)

    def test_staff_pode_acessar_fila(self):
        self.client.force_login(self.usuario_staff)
        response = self.client.get(reverse("printing:fila-lista"))
        self.assertEqual(response.status_code, 200)

    def test_usuario_comum_recebe_403_em_impressoras(self):
        self.client.force_login(self.usuario_comum)
        response = self.client.get(reverse("printing:impressora-list"))
        self.assertEqual(response.status_code, 403)

    def test_staff_pode_acessar_lista_impressoras(self):
        self.client.force_login(self.usuario_staff)
        response = self.client.get(reverse("printing:impressora-list"))
        self.assertEqual(response.status_code, 200)


class EnviarImpressaoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario, self.artista, self.produto, self.pedido_pago = criar_setup_pedido_pago()
        # Pedido não pago
        usuario2 = criar_usuario("u2@t.com", "U2")
        artista2 = criar_artista(criar_usuario("a2@t.com", "A2"))
        self.pedido_nao_pago = PedidoService.criar_pedido(usuario2, artista2)

    def test_pedido_pago_pode_ir_para_fila(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:enviar-impressao", kwargs={"pk": self.pedido_pago.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(FilaImpressao.objects.filter(pedido=self.pedido_pago).exists())

    def test_pedido_nao_pago_nao_vai_para_fila(self):
        self.client.force_login(self.pedido_nao_pago.usuario)
        url = reverse("orders:enviar-impressao", kwargs={"pk": self.pedido_nao_pago.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(FilaImpressao.objects.filter(pedido=self.pedido_nao_pago).exists())

    def test_sem_login_redireciona(self):
        url = reverse("orders:enviar-impressao", kwargs={"pk": self.pedido_pago.pk})
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 301])
        self.assertIn("login", response["Location"])

    def test_nao_cria_entrada_duplicada_na_fila(self):
        self.client.force_login(self.usuario)
        url = reverse("orders:enviar-impressao", kwargs={"pk": self.pedido_pago.pk})
        self.client.post(url)
        self.client.post(url)
        count = FilaImpressao.objects.filter(pedido=self.pedido_pago).count()
        self.assertEqual(count, 1)


class FilaStatusUpdateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = criar_usuario("staff2@t.com", "Staff2", staff=True)
        self.usuario_comum = criar_usuario("common@t.com", "Common")
        usuario, artista, produto, pedido = criar_setup_pedido_pago()
        # Enviar para impressão via service direto
        PedidoService.enviar_para_producao(pedido)
        self.fila = FilaImpressao.objects.create(pedido=pedido, status="aguardando")
        self.pedido = pedido

    def test_staff_pode_mudar_status_aguardando_para_imprimindo(self):
        self.client.force_login(self.staff)
        url = reverse("printing:fila-status-update", kwargs={"pk": self.fila.pk})
        self.client.post(url, {"status": "imprimindo"})
        self.fila.refresh_from_db()
        self.assertEqual(self.fila.status, "imprimindo")

    def test_nao_pode_concluir_sem_iniciar(self):
        """Não deve ser possível ir de 'aguardando' para 'concluido'."""
        self.client.force_login(self.staff)
        url = reverse("printing:fila-status-update", kwargs={"pk": self.fila.pk})
        self.client.post(url, {"status": "concluido"})
        self.fila.refresh_from_db()
        # Status deve permanecer 'aguardando'
        self.assertEqual(self.fila.status, "aguardando")

    def test_ao_concluir_pedido_muda_para_impresso(self):
        # Primeiro iniciar
        self.fila.status = "imprimindo"
        self.fila.save()
        self.client.force_login(self.staff)
        url = reverse("printing:fila-status-update", kwargs={"pk": self.fila.pk})
        self.client.post(url, {"status": "concluido"})
        self.fila.refresh_from_db()
        self.pedido.refresh_from_db()
        self.assertEqual(self.fila.status, "concluido")
        self.assertEqual(self.pedido.status_pedido, "impresso")

    def test_fluxo_erro_impressao(self):
        self.fila.status = "imprimindo"
        self.fila.save()
        self.client.force_login(self.staff)
        url = reverse("printing:fila-status-update", kwargs={"pk": self.fila.pk})
        self.client.post(url, {"status": "erro"})
        self.fila.refresh_from_db()
        self.assertEqual(self.fila.status, "erro")

    def test_retomar_apos_erro(self):
        self.fila.status = "erro"
        self.fila.save()
        self.client.force_login(self.staff)
        url = reverse("printing:fila-status-update", kwargs={"pk": self.fila.pk})
        self.client.post(url, {"status": "imprimindo"})
        self.fila.refresh_from_db()
        self.assertEqual(self.fila.status, "imprimindo")

    def test_usuario_comum_recebe_403_no_update_status(self):
        self.client.force_login(self.usuario_comum)
        url = reverse("printing:fila-status-update", kwargs={"pk": self.fila.pk})
        response = self.client.post(url, {"status": "imprimindo"})
        self.assertEqual(response.status_code, 403)


class FilaImpressaoModelTest(TestCase):
    def test_criacao_fila_str(self):
        usuario = criar_usuario("fila_model@t.com", "Fila User")
        artista_user = criar_usuario("art_fila@t.com", "Art Fila")
        artista = criar_artista(artista_user)
        produto = criar_produto()
        arte = Arte.objects.create(
            artista=artista,
            nome="Arte Fila",
            arquivo="artes/fila.jpg",
            ativa=True,
        )
        personalizacao = Personalizacao.objects.create(produto=produto, arte=arte)
        pedido = PedidoService.criar_pedido(usuario, artista)
        PedidoService.adicionar_item(pedido, produto, personalizacao, 1, Decimal("49.90"))
        PedidoService.confirmar_pagamento(pedido, "pix", "confirmado")
        PedidoService.enviar_para_producao(pedido)
        fila = FilaImpressao.objects.create(pedido=pedido, status="aguardando")
        self.assertIn(str(pedido.id), str(fila))
