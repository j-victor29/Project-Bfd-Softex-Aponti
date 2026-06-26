"""
Testes automatizados para o app core do projeto Capinha.

Cobre:
- Retorno HTTP 200 das páginas institucionais (home, sobre, como-testar)
- Comportamento da navbar para usuários anônimos, clientes, artistas aprovados e staff
- Isolamento de links exclusivos por perfil de usuário
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PaginasInstitucionaisTest(TestCase):
    """Valida que as páginas públicas retornam HTTP 200."""

    def setUp(self):
        self.client = Client()

    def test_home_retorna_200(self):
        """A página inicial deve estar acessível sem autenticação."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_sobre_retorna_200(self):
        """A página /sobre/ deve estar acessível sem autenticação."""
        response = self.client.get(reverse('sobre'))
        self.assertEqual(response.status_code, 200)

    def test_como_testar_retorna_200(self):
        """A página /como-testar/ deve estar acessível sem autenticação."""
        response = self.client.get(reverse('como-testar'))
        self.assertEqual(response.status_code, 200)

    def test_home_usa_template_correto(self):
        """A home deve usar o template home.html."""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_sobre_usa_template_correto(self):
        """A página sobre deve usar o template sobre.html."""
        response = self.client.get(reverse('sobre'))
        self.assertTemplateUsed(response, 'sobre.html')

    def test_como_testar_usa_template_correto(self):
        """A página como-testar deve usar o template como_testar.html."""
        response = self.client.get(reverse('como-testar'))
        self.assertTemplateUsed(response, 'como_testar.html')

    def test_home_contem_nome_projeto(self):
        """A home deve exibir o nome do projeto."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Capinha')

    def test_sobre_contem_descricao_projeto(self):
        """A página sobre deve conter informações do projeto."""
        response = self.client.get(reverse('sobre'))
        self.assertContains(response, 'Sobre')

    def test_como_testar_contem_credenciais(self):
        """A página como-testar deve conter as credenciais de acesso demo."""
        response = self.client.get(reverse('como-testar'))
        self.assertContains(response, 'cliente@capinha.com')
        self.assertContains(response, 'artista@capinha.com')
        self.assertContains(response, 'staff@capinha.com')


class NavbarPermissoesTest(TestCase):
    """Valida visibilidade de links da navbar conforme perfil de usuário."""

    def setUp(self):
        self.client = Client()

        # Usuário comum (cliente)
        self.cliente = User.objects.create_user(
            email='cliente_test@capinha.com',
            password='testpass123',
            nome='Cliente Teste',
        )

        # Usuário staff
        self.staff = User.objects.create_user(
            email='staff_test@capinha.com',
            password='testpass123',
            nome='Staff Teste',
            is_staff=True,
        )

        # Usuário artista (com perfil aprovado)
        self.artista_user = User.objects.create_user(
            email='artista_test@capinha.com',
            password='testpass123',
            nome='Artista Teste',
        )
        from artists.models import Artista
        self.artista_perfil = Artista.objects.create(
            usuario=self.artista_user,
            nome_artistico='Artista de Teste',
            status_aprovacao='aprovado',
            ativo=True,
        )

    def test_navbar_anonimo_mostra_login(self):
        """Usuário não autenticado deve ver o botão de Login."""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Início')
        self.assertContains(response, 'Sobre')
        self.assertContains(response, 'Como Testar')

    def test_navbar_anonimo_nao_mostra_carrinho(self):
        """Usuário não autenticado não deve ver o link de Carrinho."""
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Carrinho')

    def test_navbar_cliente_mostra_carrinho_e_pedidos(self):
        """Usuário autenticado como cliente deve ver Carrinho e Pedidos."""
        self.client.login(email='cliente_test@capinha.com', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Carrinho')
        self.assertContains(response, 'Pedidos')
        self.assertContains(response, 'Sair')

    def test_navbar_cliente_nao_mostra_painel_artista(self):
        """Usuário cliente sem perfil de artista aprovado não deve ver o link do Painel."""
        self.client.login(email='cliente_test@capinha.com', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Painel do Artista')

    def test_navbar_artista_aprovado_mostra_painel(self):
        """Artista aprovado deve ver o link para o Painel do Artista na navbar."""
        self.client.login(email='artista_test@capinha.com', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Painel do Artista')

    def test_navbar_staff_mostra_producao(self):
        """Usuário staff deve ver o menu Produção na navbar."""
        self.client.login(email='staff_test@capinha.com', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Produção')

    def test_navbar_cliente_nao_mostra_producao(self):
        """Usuário comum não deve ver o menu Produção."""
        self.client.login(email='cliente_test@capinha.com', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Produção')


class SeedDemoTest(TestCase):
    """Testa que o comando seed_demo executa sem erros."""

    def test_seed_demo_executa_sem_erros(self):
        """O comando seed_demo deve finalizar com sucesso e criar os dados básicos."""
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        # Executa o seed sem quebrar
        call_command('seed_demo', stdout=out)
        output = out.getvalue()
        # Verifica que o seed rodou e criou os dados
        self.assertIn('Seed conclu', output)

    def test_seed_demo_idempotente(self):
        """Rodar seed_demo duas vezes não deve gerar duplicatas ou erros."""
        from django.core.management import call_command
        from io import StringIO
        call_command('seed_demo', stdout=StringIO())
        # Segunda execução não deve lançar exceção
        out = StringIO()
        call_command('seed_demo', stdout=out)
        self.assertIn('Seed conclu', out.getvalue())
