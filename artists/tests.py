"""
Testes automatizados para o Painel do Artista.
Cobertura:
  - Permissões de acesso (anônimo, comum, pendente, aprovado, superuser)
  - Métricas do painel (artes, coleções, vendas, comissão)
  - Isolamento de dados (artista só vê seus dados)
  - Cálculo de comissão estimada
"""
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from artists.models import Artista
from creations.models import Colecao, Arte, Personalizacao
from orders.models import Pedido, ItemPedido
from products.models import Produto

User = get_user_model()

# ─── Helpers de criação ─────────────────────────────────────────────────────


def criar_usuario(email, nome="Usuário", senha="senha123", is_superuser=False, is_staff=False):
    u = User.objects.create_user(email=email, nome=nome, password=senha)
    if is_superuser:
        u.is_superuser = True
        u.is_staff = True
        u.save()
    elif is_staff:
        u.is_staff = True
        u.save()
    return u


def criar_artista(usuario, status="aprovado"):
    return Artista.objects.create(
        usuario=usuario,
        nome_artistico=f"Artista de {usuario.nome}",
        status_aprovacao=status,
        ativo=True,
    )


def criar_produto(nome="GreenCase Padrão"):
    return Produto.objects.create(
        nome=nome,
        categoria="capinha",
        preco_base=Decimal("50.00"),
        estoque=10,
        ativo=True,
    )


def criar_pedido_com_arte(usuario, artista, arte, produto):
    """Cria um pedido com um item que usa a arte do artista e retorna (pedido, item)."""
    personalizacao = Personalizacao.objects.create(
        produto=produto,
        arte=arte,
        texto="Teste",
        fonte="Arial",
        cor="#fff",
        preco_extra=Decimal("10.00"),
    )
    pedido = Pedido.objects.create(
        usuario=usuario,
        artista=artista,
        status_pedido="pago",
        valor_total=Decimal("60.00"),
    )
    item = ItemPedido.objects.create(
        pedido=pedido,
        produto=produto,
        personalizacao=personalizacao,
        quantidade=2,
        preco_unitario=Decimal("30.00"),
    )
    return pedido, item


# ─── Fixture base ─────────────────────────────────────────────────────────────

class PainelBaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Usuário comum (cliente)
        self.usuario_comum = criar_usuario("cliente@test.com", "Cliente")

        # Artista aprovado
        self.artista_user = criar_usuario("artista@test.com", "Artista Aprovado")
        self.artista = criar_artista(self.artista_user, status="aprovado")

        # Artista pendente
        self.pendente_user = criar_usuario("pendente@test.com", "Artista Pendente")
        self.artista_pendente = criar_artista(self.pendente_user, status="pendente")

        # Superuser sem perfil de artista
        self.superuser = criar_usuario("super@test.com", "Admin", is_superuser=True)

        # Produto e coleção
        self.produto = criar_produto()
        self.colecao = Colecao.objects.create(
            artista=self.artista,
            nome="Coleção Principal",
            descricao="Descrição.",
            ativa=True,
        )
        self.arte = Arte.objects.create(
            artista=self.artista,
            colecao=self.colecao,
            nome="Arte Principal",
            arquivo="artes/teste.jpg",
            ativa=True,
        )


# ─── 1. Testes de Permissão ───────────────────────────────────────────────────

class PainelPermissaoTest(PainelBaseTestCase):

    def test_anonimo_redireciona_para_login(self):
        """Usuário anônimo deve ser redirecionado para a tela de login."""
        for url_name in ['painel-principal', 'painel-artes', 'painel-colecoes']:
            response = self.client.get(reverse(url_name))
            self.assertIn(response.status_code, [302, 301], msg=f"URL {url_name} não redirecionou")
            self.assertIn('/login', response['Location'], msg=f"URL {url_name} não redirecionou para login")

    def test_usuario_comum_recebe_403(self):
        """Usuário logado sem perfil de artista deve receber 403."""
        self.client.force_login(self.usuario_comum)
        for url_name in ['painel-principal', 'painel-artes', 'painel-colecoes']:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 403, msg=f"URL {url_name} não retornou 403 para usuário comum")

    def test_artista_pendente_recebe_403(self):
        """Artista com status pendente deve receber 403."""
        self.client.force_login(self.pendente_user)
        for url_name in ['painel-principal', 'painel-artes', 'painel-colecoes']:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 403, msg=f"URL {url_name} não retornou 403 para artista pendente")

    def test_artista_aprovado_acessa_painel(self):
        """Artista aprovado deve acessar o painel com sucesso (200)."""
        self.client.force_login(self.artista_user)
        for url_name in ['painel-principal', 'painel-artes', 'painel-colecoes']:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, msg=f"URL {url_name} não retornou 200 para artista aprovado")

    def test_superuser_acessa_painel(self):
        """Superuser deve acessar o painel mesmo sem perfil de artista."""
        self.client.force_login(self.superuser)
        for url_name in ['painel-principal', 'painel-artes', 'painel-colecoes']:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, msg=f"URL {url_name} não retornou 200 para superuser")


# ─── 2. Testes de Métricas ────────────────────────────────────────────────────

class PainelMetricasTest(PainelBaseTestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.artista_user)

        # Criar segunda arte e segunda coleção
        self.colecao2 = Colecao.objects.create(
            artista=self.artista,
            nome="Coleção Secundária",
            ativa=True,
        )
        self.arte2 = Arte.objects.create(
            artista=self.artista,
            colecao=self.colecao2,
            nome="Arte Secundária",
            arquivo="artes/teste2.jpg",
            ativa=True,
        )

        # Criar pedido usando arte do artista
        self.pedido, self.item = criar_pedido_com_arte(
            usuario=self.usuario_comum,
            artista=self.artista,
            arte=self.arte,
            produto=self.produto,
        )
        # subtotal = 2 * 30 = 60.00

    def test_total_artes_correto(self):
        """O painel deve exibir a contagem correta de artes do artista."""
        response = self.client.get(reverse('painel-principal'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_artes'], 2)

    def test_total_colecoes_correto(self):
        """O painel deve exibir a contagem correta de coleções do artista."""
        response = self.client.get(reverse('painel-principal'))
        self.assertEqual(response.context['total_colecoes'], 2)

    def test_total_vendas_correto(self):
        """O total de vendas deve ser igual ao número de itens de pedido com artes do artista."""
        response = self.client.get(reverse('painel-principal'))
        # 1 item criado no setUp
        self.assertEqual(response.context['total_vendas'], 1)

    def test_calculo_comissao_estimada(self):
        """Comissão estimada deve ser 10% do subtotal dos itens do artista."""
        # subtotal do item = 60.00, comissão = 6.00
        response = self.client.get(reverse('painel-principal'))
        comissao = response.context['comissao_estimada']
        self.assertAlmostEqual(float(comissao), 6.00, places=2)

    def test_ultimos_pedidos_no_contexto(self):
        """O contexto do painel deve conter lista de últimos pedidos."""
        response = self.client.get(reverse('painel-principal'))
        self.assertIn('ultimos_pedidos', response.context)
        self.assertEqual(len(response.context['ultimos_pedidos']), 1)

    def test_artes_mais_usadas_no_contexto(self):
        """O contexto deve conter a lista de artes mais utilizadas."""
        response = self.client.get(reverse('painel-principal'))
        self.assertIn('artes_mais_usadas', response.context)


# ─── 3. Testes de Isolamento de Dados ────────────────────────────────────────

class PainelIsolamentoTest(PainelBaseTestCase):

    def setUp(self):
        super().setUp()

        # Segundo artista com seus próprios dados
        self.outro_artista_user = criar_usuario("outro@test.com", "Outro Artista")
        self.outro_artista = criar_artista(self.outro_artista_user, status="aprovado")

        self.colecao_outro = Colecao.objects.create(
            artista=self.outro_artista,
            nome="Coleção do Outro",
            ativa=True,
        )
        self.arte_outro = Arte.objects.create(
            artista=self.outro_artista,
            nome="Arte do Outro",
            arquivo="artes/outro.jpg",
            ativa=True,
        )

        self.client.force_login(self.artista_user)

    def test_artista_ve_apenas_suas_artes(self):
        """O painel de artes deve exibir apenas as artes do artista logado."""
        response = self.client.get(reverse('painel-artes'))
        self.assertEqual(response.status_code, 200)
        artes_ids = list(response.context['artes'].values_list('artista_id', flat=True))
        for artista_id in artes_ids:
            self.assertEqual(artista_id, self.artista.pk)

    def test_artista_ve_apenas_suas_colecoes(self):
        """O painel de coleções deve exibir apenas as coleções do artista logado."""
        response = self.client.get(reverse('painel-colecoes'))
        self.assertEqual(response.status_code, 200)
        colecoes_ids = list(response.context['colecoes'].values_list('artista_id', flat=True))
        for artista_id in colecoes_ids:
            self.assertEqual(artista_id, self.artista.pk)

    def test_metricas_nao_incluem_dados_de_outro_artista(self):
        """As métricas do painel não devem incluir dados de outros artistas."""
        produto2 = criar_produto("Produto Outro")
        pedido_outro, _ = criar_pedido_com_arte(
            usuario=self.usuario_comum,
            artista=self.outro_artista,
            arte=self.arte_outro,
            produto=produto2,
        )
        response = self.client.get(reverse('painel-principal'))
        # Artista principal não tem pedidos com suas artes (ainda)
        self.assertEqual(response.context['total_vendas'], 0)


# ─── 4. Testes de Comissão Múltipla ──────────────────────────────────────────

class PainelComissaoTest(PainelBaseTestCase):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.artista_user)

        # Arte extra do mesmo artista
        self.arte2 = Arte.objects.create(
            artista=self.artista,
            colecao=self.colecao,
            nome="Arte 2",
            arquivo="artes/arte2.jpg",
            ativa=True,
        )

        # Pedido 1: subtotal = 2 * 30 = 60
        pedido1, _ = criar_pedido_com_arte(
            usuario=self.usuario_comum,
            artista=self.artista,
            arte=self.arte,
            produto=self.produto,
        )
        # Pedido 2 (mesma arte, 1 item): subtotal = 1 * 30 = 30
        personalizacao2 = Personalizacao.objects.create(
            produto=self.produto,
            arte=self.arte2,
            texto="Pedido 2",
            preco_extra=Decimal("5.00"),
        )
        pedido2 = Pedido.objects.create(
            usuario=self.usuario_comum,
            artista=self.artista,
            status_pedido="pago",
            valor_total=Decimal("30.00"),
        )
        ItemPedido.objects.create(
            pedido=pedido2,
            produto=self.produto,
            personalizacao=personalizacao2,
            quantidade=1,
            preco_unitario=Decimal("30.00"),
        )

    def test_comissao_soma_varios_itens(self):
        """A comissão deve ser 10% da soma de todos os subtotais dos itens do artista."""
        # subtotal pedido1 = 60, subtotal pedido2 = 30 → total = 90 → comissão = 9.00
        response = self.client.get(reverse('painel-principal'))
        comissao = response.context['comissao_estimada']
        self.assertAlmostEqual(float(comissao), 9.00, places=2)

    def test_total_vendas_acumulado(self):
        """O total de vendas deve contabilizar todos os itens."""
        response = self.client.get(reverse('painel-principal'))
        # 2 itens (um em cada pedido)
        self.assertEqual(response.context['total_vendas'], 2)


# ─── 5. Testes de Gerenciamento de Artes e Coleções ────────────────────────────

class GerenciamentoArteTest(PainelBaseTestCase):

    def setUp(self):
        super().setUp()
        # Outro artista para testar isolamento/permissões
        self.outro_user = criar_usuario("outro_artist@test.com", "Outro Artista")
        self.outro_artista = criar_artista(self.outro_user, status="aprovado")
        self.arte_outro = Arte.objects.create(
            artista=self.outro_artista,
            nome="Arte de Outro",
            arquivo="artes/outro.jpg",
            ativa=True
        )

    def test_anonimo_nao_acessa_criacao_arte(self):
        response = self.client.get(reverse('painel-arte-nova'))
        self.assertEqual(response.status_code, 302)

    def test_usuario_comum_nao_acessa_criacao_arte(self):
        self.client.force_login(self.usuario_comum)
        response = self.client.get(reverse('painel-arte-nova'))
        self.assertEqual(response.status_code, 403)

    def test_artista_pendente_nao_acessa_criacao_arte(self):
        self.client.force_login(self.pendente_user)
        response = self.client.get(reverse('painel-arte-nova'))
        self.assertEqual(response.status_code, 403)

    def test_artista_aprovado_cria_arte_com_sucesso(self):
        self.client.force_login(self.artista_user)
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile
        with tempfile.NamedTemporaryFile(suffix=".gif") as temp_file:
            img = SimpleUploadedFile("nova_arte.gif", b'GIF89a\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b', content_type="image/gif")
            data = {
                'nome': 'Minha Nova Arte Maravilhosa',
                'descricao': 'Uma arte incrível para GreenCases.',
                'arquivo': img,
                'colecao': self.colecao.pk,
                'ativa': True,
            }
            response = self.client.post(reverse('painel-arte-nova'), data=data)
            self.assertEqual(response.status_code, 302) # Redirect to painel-artes
            self.assertTrue(Arte.objects.filter(nome='Minha Nova Arte Maravilhosa', artista=self.artista).exists())

    def test_artista_edita_propria_arte(self):
        self.client.force_login(self.artista_user)
        data = {
            'nome': 'Arte Principal Editada',
            'descricao': 'Descrição alterada.',
            'colecao': self.colecao.pk,
            'ativa': True,
        }
        # arquivo é opcional na edição se já tiver
        response = self.client.post(reverse('painel-arte-editar', args=[self.arte.pk]), data=data)
        self.assertEqual(response.status_code, 302)
        self.arte.refresh_from_db()
        self.assertEqual(self.arte.nome, 'Arte Principal Editada')

    def test_artista_nao_edita_arte_de_outro_artista(self):
        self.client.force_login(self.artista_user)
        data = {
            'nome': 'Tentando Hackear',
            'ativa': True,
        }
        response = self.client.post(reverse('painel-arte-editar', args=[self.arte_outro.pk]), data=data)
        self.assertEqual(response.status_code, 403)

    def test_artista_ativa_inativa_propria_arte(self):
        self.client.force_login(self.artista_user)
        self.assertTrue(self.arte.ativa)
        response = self.client.post(reverse('painel-arte-status', args=[self.arte.pk]))
        self.assertEqual(response.status_code, 302)
        self.arte.refresh_from_db()
        self.assertFalse(self.arte.ativa)

    def test_artista_filtra_artes_por_colecao(self):
        self.client.force_login(self.artista_user)
        colecao_extra = Colecao.objects.create(
            artista=self.artista,
            nome="Coleção Extra",
            ativa=True
        )
        arte_extra = Arte.objects.create(
            artista=self.artista,
            colecao=colecao_extra,
            nome="Arte Extra",
            arquivo="artes/extra.jpg",
            ativa=True
        )
        response = self.client.get(reverse('painel-artes') + f'?colecao={self.colecao.pk}')
        self.assertEqual(response.status_code, 200)
        artes_list = list(response.context['artes'])
        self.assertIn(self.arte, artes_list)
        self.assertNotIn(arte_extra, artes_list)


class GerenciamentoColecaoTest(PainelBaseTestCase):

    def setUp(self):
        super().setUp()
        self.outro_user = criar_usuario("outro_artist2@test.com", "Outro Artista 2")
        self.outro_artista = criar_artista(self.outro_user, status="aprovado")
        self.colecao_outro = Colecao.objects.create(
            artista=self.outro_artista,
            nome="Colecao de Outro",
            ativa=True
        )

    def test_artista_aprovado_cria_colecao_com_sucesso(self):
        self.client.force_login(self.artista_user)
        data = {
            'nome': 'Minha Nova Colecao',
            'descricao': 'Minha colecao especial.',
            'ativa': True,
        }
        response = self.client.post(reverse('painel-colecao-nova'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Colecao.objects.filter(nome='Minha Nova Colecao', artista=self.artista).exists())

    def test_artista_edita_propria_colecao(self):
        self.client.force_login(self.artista_user)
        data = {
            'nome': 'Coleção Principal Editada',
            'descricao': 'Descrição nova.',
            'ativa': True,
        }
        response = self.client.post(reverse('painel-colecao-editar', args=[self.colecao.pk]), data=data)
        self.assertEqual(response.status_code, 302)
        self.colecao.refresh_from_db()
        self.assertEqual(self.colecao.nome, 'Coleção Principal Editada')

    def test_artista_nao_edita_colecao_de_outro_artista(self):
        self.client.force_login(self.artista_user)
        data = {
            'nome': 'Colecao Invadida',
            'ativa': True,
        }
        response = self.client.post(reverse('painel-colecao-editar', args=[self.colecao_outro.pk]), data=data)
        self.assertEqual(response.status_code, 403)

    def test_artista_ativa_inativa_propria_colecao(self):
        self.client.force_login(self.artista_user)
        self.assertTrue(self.colecao.ativa)
        response = self.client.post(reverse('painel-colecao-status', args=[self.colecao.pk]))
        self.assertEqual(response.status_code, 302)
        self.colecao.refresh_from_db()
        self.assertFalse(self.colecao.ativa)

