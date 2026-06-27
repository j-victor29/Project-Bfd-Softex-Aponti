from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from products.models import Produto
from artists.models import Artista
from creations.models import Arte, Personalizacao
from cart.models import Carrinho, ItemCarrinho
from orders.models import Pedido, ItemPedido

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


def criar_produto(nome="GreenCase Teste", preco_base="49.90", ativo=True):
    return Produto.objects.create(
        nome=nome,
        categoria="capinha",
        preco_base=preco_base,
        estoque=10,
        ativo=ativo,
    )


class CarrinhoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario("cliente@teste.com", "Cliente Teste")
        self.outro_usuario = criar_usuario("outro@teste.com", "Outro Teste")
        
        self.artista_user = criar_usuario("artista@teste.com", "Artista Teste")
        self.artista = criar_artista(self.artista_user)
        
        self.produto = criar_produto("GreenCase Top", "50.00")
        self.arte = Arte.objects.create(
            artista=self.artista,
            nome="Arte Massa",
            arquivo="artes/massa.jpg",
            ativa=True
        )
        self.personalizacao = Personalizacao.objects.create(
            produto=self.produto,
            arte=self.arte,
            texto="Meu Nome",
            fonte="Arial",
            cor="#ffffff",
            preco_extra=Decimal("15.00")  # Preço total = 50 + 15 = 65
        )

    def test_usuario_anonimo_nao_acessa_carrinho(self):
        """Usuário anônimo deve ser redirecionado para login."""
        response = self.client.get(reverse('cart:carrinho-detalhe'))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response["Location"])

    def test_usuario_logado_acessa_carrinho_vazio(self):
        """Usuário logado vê a tela do carrinho com indicação de que está vazio."""
        self.client.force_login(self.usuario)
        response = self.client.get(reverse('cart:carrinho-detalhe'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seu carrinho está vazio")

    def test_adicionar_personalizacao_ao_carrinho(self):
        """Adiciona um item ao carrinho."""
        self.client.force_login(self.usuario)
        response = self.client.get(reverse('cart:carrinho-adicionar', kwargs={'personalizacao_id': self.personalizacao.id}))
        self.assertEqual(response.status_code, 302)  # Redireciona para o detalhe do carrinho

        carrinho = Carrinho.objects.filter(usuario=self.usuario, status='aberto').first()
        self.assertIsNotNone(carrinho)
        self.assertEqual(carrinho.itens.count(), 1)
        
        item = carrinho.itens.first()
        self.assertEqual(item.personalizacao, self.personalizacao)
        self.assertEqual(item.quantidade, 1)
        self.assertEqual(item.preco_unitario, Decimal("65.00"))
        self.assertEqual(item.subtotal, Decimal("65.00"))

    def test_nao_duplica_item_no_carrinho(self):
        """Se o item já existe, apenas incrementa a quantidade."""
        self.client.force_login(self.usuario)
        self.client.get(reverse('cart:carrinho-adicionar', kwargs={'personalizacao_id': self.personalizacao.id}))
        self.client.get(reverse('cart:carrinho-adicionar', kwargs={'personalizacao_id': self.personalizacao.id}))

        carrinho = Carrinho.objects.get(usuario=self.usuario, status='aberto')
        self.assertEqual(carrinho.itens.count(), 1)
        item = carrinho.itens.first()
        self.assertEqual(item.quantidade, 2)
        self.assertEqual(item.subtotal, Decimal("130.00"))

    def test_atualizar_quantidade(self):
        """Atualiza a quantidade do item no carrinho."""
        self.client.force_login(self.usuario)
        carrinho = Carrinho.objects.create(usuario=self.usuario, status='aberto')
        item = ItemCarrinho.objects.create(
            carrinho=carrinho,
            personalizacao=self.personalizacao,
            quantidade=1,
            preco_unitario=Decimal("65.00")
        )

        url = reverse('cart:carrinho-atualizar', kwargs={'item_id': item.id})
        response = self.client.post(url, {'quantidade': 5})
        self.assertEqual(response.status_code, 302)

        item.refresh_from_db()
        self.assertEqual(item.quantidade, 5)
        self.assertEqual(item.subtotal, Decimal("325.00"))

    def test_remover_item(self):
        """Remove um item do carrinho."""
        self.client.force_login(self.usuario)
        carrinho = Carrinho.objects.create(usuario=self.usuario, status='aberto')
        item = ItemCarrinho.objects.create(
            carrinho=carrinho,
            personalizacao=self.personalizacao,
            quantidade=1,
            preco_unitario=Decimal("65.00")
        )

        url = reverse('cart:carrinho-remover', kwargs={'item_id': item.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ItemCarrinho.objects.filter(id=item.id).exists())

    def test_bloquear_item_de_outro_usuario(self):
        """Um usuário não pode atualizar/remover itens do carrinho de outro usuário."""
        carrinho = Carrinho.objects.create(usuario=self.outro_usuario, status='aberto')
        item = ItemCarrinho.objects.create(
            carrinho=carrinho,
            personalizacao=self.personalizacao,
            quantidade=1,
            preco_unitario=Decimal("65.00")
        )

        self.client.force_login(self.usuario)
        # Tenta atualizar
        url_atualizar = reverse('cart:carrinho-atualizar', kwargs={'item_id': item.id})
        response = self.client.post(url_atualizar, {'quantidade': 5})
        self.assertEqual(response.status_code, 404)  # Espera 404 pois a view busca filtrando pelo usuário logado

        # Tenta remover
        url_remover = reverse('cart:carrinho-remover', kwargs={'item_id': item.id})
        response = self.client.get(url_remover)
        self.assertEqual(response.status_code, 404)

    def test_finalizar_carrinho_cria_pedido(self):
        """Finaliza o carrinho e gera um Pedido correspondente."""
        self.client.force_login(self.usuario)
        carrinho = Carrinho.objects.create(usuario=self.usuario, status='aberto')
        ItemCarrinho.objects.create(
            carrinho=carrinho,
            personalizacao=self.personalizacao,
            quantidade=2,
            preco_unitario=Decimal("65.00")
        )

        response = self.client.get(reverse('cart:carrinho-finalizar'))
        self.assertEqual(response.status_code, 302)  # Redireciona para o detalhe do pedido

        carrinho.refresh_from_db()
        self.assertEqual(carrinho.status, 'finalizado')

        pedido = Pedido.objects.filter(usuario=self.usuario).first()
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.valor_total, Decimal("130.00"))
        self.assertEqual(pedido.itens.count(), 1)

        item_pedido = pedido.itens.first()
        self.assertEqual(item_pedido.personalizacao, self.personalizacao)
        self.assertEqual(item_pedido.quantidade, 2)
        self.assertEqual(item_pedido.preco_unitario, Decimal("65.00"))

    def test_nao_finaliza_carrinho_vazio(self):
        """Não permite finalizar um carrinho sem itens."""
        self.client.force_login(self.usuario)
        carrinho = Carrinho.objects.create(usuario=self.usuario, status='aberto')

        response = self.client.get(reverse('cart:carrinho-finalizar'))
        self.assertEqual(response.status_code, 302)  # Redireciona de volta para o carrinho
        carrinho.refresh_from_db()
        self.assertEqual(carrinho.status, 'aberto')  # Não deve finalizar

    def test_fluxo_completo(self):
        """Testa o fluxo completo da personalização ao pedido e pagamento simulado."""
        self.client.force_login(self.usuario)
        
        # 1. Salvar personalização
        response_salvar = self.client.post(reverse('personalizacao-salvar'), {
            'produto_id': self.produto.id,
            'arte_id': self.arte.id,
            'texto': 'Fluxo Completo',
            'fonte': 'Arial',
            'cor': '#ff0000',
            'preco_extra': '10.00'
        })
        self.assertEqual(response_salvar.status_code, 302)
        response_salvar = self.client.get(response_salvar["Location"], follow=True)

        # 2. Verificar que foi criado no carrinho
        carrinho = Carrinho.objects.get(usuario=self.usuario, status='aberto')
        self.assertEqual(carrinho.itens.count(), 1)

        # 3. Finalizar carrinho
        response_checkout = self.client.get(reverse('cart:carrinho-finalizar'))
        self.assertEqual(response_checkout.status_code, 302)
        
        pedido = Pedido.objects.filter(usuario=self.usuario).first()
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.status_pedido, 'criado')

        # 4. Simular pagamento
        url_pagamento = reverse('payments:simular-pagamento', kwargs={'pedido_id': pedido.pk})
        response_pagamento = self.client.post(url_pagamento, {'method': 'pix'})
        self.assertEqual(response_pagamento.status_code, 302)
        pedido.refresh_from_db()
        self.assertEqual(pedido.status_pedido, 'pago')
