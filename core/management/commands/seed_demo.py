"""
Comando de seed para popular o banco com dados de demonstração.

Uso:
    python manage.py seed_demo

O comando é idempotente: cria dados apenas se ainda não existirem.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com dados de demonstração do MVP Capinha."

    def _log(self, msg, created=True):
        if created:
            self.stdout.write(self.style.SUCCESS(f"  [CRIADO] {msg}"))
        else:
            self.stdout.write(self.style.WARNING(f"  [JÁ EXISTE] {msg}"))

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("\n=== 🌱 Seed Demo: Capinha MVP ===\n"))

        # ─── 1. Usuários ───────────────────────────────────────────────────────
        self.stdout.write("👤 Criando usuários...")

        usuario_comum, created = User.objects.get_or_create(
            email="cliente@capinha.com",
            defaults={"nome": "Cliente Demo", "is_staff": False, "is_active": True},
        )
        if created:
            usuario_comum.set_password("capinha123")
            usuario_comum.save()
        self._log("Usuário comum: cliente@capinha.com / capinha123", created)

        usuario_staff, created = User.objects.get_or_create(
            email="staff@capinha.com",
            defaults={"nome": "Staff Demo", "is_staff": True, "is_active": True},
        )
        if created:
            usuario_staff.set_password("capinha123")
            usuario_staff.save()
        self._log("Usuário staff: staff@capinha.com / capinha123", created)

        artista_user, created = User.objects.get_or_create(
            email="artista@capinha.com",
            defaults={"nome": "Artista Demo", "is_staff": False, "is_active": True},
        )
        if created:
            artista_user.set_password("capinha123")
            artista_user.save()
        self._log("Usuário artista: artista@capinha.com / capinha123", created)

        # ─── 2. Artista ────────────────────────────────────────────────────────
        self.stdout.write("\n🎨 Criando artista...")
        from artists.models import Artista

        artista, created = Artista.objects.get_or_create(
            usuario=artista_user,
            defaults={
                "nome_artistico": "Studio Capinha",
                "biografia": "Estúdio de arte personalizada para capinhas.",
                "status_aprovacao": "aprovado",
                "ativo": True,
            },
        )
        self._log("Artista: Studio Capinha (aprovado)", created)

        # ─── 3. Produtos ───────────────────────────────────────────────────────
        self.stdout.write("\n📦 Criando produtos...")
        from products.models import Produto

        produtos_data = [
            {
                "nome": "Capinha iPhone 15 Pro",
                "descricao": "Capinha de silicone premium para iPhone 15 Pro.",
                "categoria": "capinha",
                "preco_base": Decimal("49.90"),
                "estoque": 50,
                "ativo": True,
            },
            {
                "nome": "Capinha Samsung Galaxy S24",
                "descricao": "Capinha resistente para Samsung Galaxy S24.",
                "categoria": "capinha",
                "preco_base": Decimal("44.90"),
                "estoque": 30,
                "ativo": True,
            },
            {
                "nome": "Case Xiaomi 14",
                "descricao": "Case transparente com suporte para Xiaomi 14.",
                "categoria": "case",
                "preco_base": Decimal("39.90"),
                "estoque": 20,
                "ativo": True,
            },
        ]
        produtos = []
        for data in produtos_data:
            produto, created = Produto.objects.get_or_create(
                nome=data["nome"], defaults=data
            )
            produtos.append(produto)
            self._log(f"Produto: {produto.nome}", created)

        # ─── 4. Coleção e Artes ────────────────────────────────────────────────
        self.stdout.write("\n🖼️  Criando coleção e artes...")
        from creations.models import Colecao, Arte

        colecao, created = Colecao.objects.get_or_create(
            artista=artista,
            nome="Natureza Viva",
            defaults={"descricao": "Arte inspirada na natureza.", "ativa": True},
        )
        self._log("Coleção: Natureza Viva", created)

        colecao2, created2 = Colecao.objects.get_or_create(
            artista=artista,
            nome="Urbano & Moderno",
            defaults={"descricao": "Arte com estética urbana e minimalista.", "ativa": True},
        )
        self._log("Coleção: Urbano & Moderno", created2)

        artes_data = [
            {"nome": "Flores do Campo",     "arquivo": "artes/flores_campo.jpg",     "ativa": True, "colecao": colecao},
            {"nome": "Oceano Azul",         "arquivo": "artes/oceano_azul.jpg",      "ativa": True, "colecao": colecao},
            {"nome": "Floresta Tropical",   "arquivo": "artes/floresta_tropical.jpg","ativa": True, "colecao": colecao},
            {"nome": "Cidade Neon",         "arquivo": "artes/cidade_neon.jpg",      "ativa": True, "colecao": colecao2},
            {"nome": "Linhas Geométricas",  "arquivo": "artes/linhas_geometricas.jpg","ativa": True, "colecao": colecao2},
            {"nome": "Esboço Rústico",      "arquivo": "artes/esboco_rustico.jpg",    "ativa": False, "colecao": colecao},
        ]
        artes = []
        for data in artes_data:
            arte, created = Arte.objects.get_or_create(
                artista=artista,
                colecao=data["colecao"],
                nome=data["nome"],
                defaults={"arquivo": data["arquivo"], "ativa": data["ativa"]},
            )
            artes.append(arte)
            self._log(f"Arte: {arte.nome}", created)


        # ─── 5. Personalização de exemplo ──────────────────────────────────────
        self.stdout.write("\n✏️  Criando personalização de exemplo...")
        from creations.models import Personalizacao

        personalizacao, created = Personalizacao.objects.get_or_create(
            produto=produtos[0],
            arte=artes[0],
            texto="João Silva",
            defaults={"fonte": "Arial", "cor": "#1a73e8", "preco_extra": Decimal("5.00")},
        )
        self._log("Personalização: iPhone 15 + Flores do Campo + 'João Silva'", created)

        # ─── 5b. Carrinho de Compras ───────────────────────────────────────────
        self.stdout.write("\n🛒 Criando carrinhos de compras...")
        from cart.models import Carrinho, ItemCarrinho

        # Carrinho aberto para o cliente comum
        carrinho_aberto, created = Carrinho.objects.get_or_create(
            usuario=usuario_comum,
            status="aberto",
        )
        if created:
            # Criar uma personalização extra para o carrinho
            pers_cart = Personalizacao.objects.create(
                produto=produtos[1],
                arte=artes[1],
                texto="Meu Carrinho",
                fonte="Courier New",
                cor="#ff00ff",
                preco_extra=Decimal("10.00")
            )
            # Adicionar item ao carrinho
            ItemCarrinho.objects.create(
                carrinho=carrinho_aberto,
                personalizacao=pers_cart,
                quantidade=2,
                preco_unitario=produtos[1].preco_base + pers_cart.preco_extra
            )
        self._log(f"Carrinho aberto para cliente@capinha.com (Total: R$ {carrinho_aberto.total:.2f})", created)

        # Carrinho finalizado para o staff
        carrinho_finalizado, created = Carrinho.objects.get_or_create(
            usuario=usuario_staff,
            status="finalizado",
        )
        if created:
            pers_cart_finalizado = Personalizacao.objects.create(
                produto=produtos[2],
                arte=artes[2],
                texto="Finalizado",
                fonte="Arial",
                cor="#000000"
            )
            ItemCarrinho.objects.create(
                carrinho=carrinho_finalizado,
                personalizacao=pers_cart_finalizado,
                quantidade=1,
                preco_unitario=produtos[2].preco_base + pers_cart_finalizado.preco_extra
            )
        self._log(f"Carrinho finalizado para staff@capinha.com", created)


        # ─── 6. Impressora ─────────────────────────────────────────────────────
        self.stdout.write("\n🖨️  Criando impressora...")
        from printing.models import Impressora

        impressora, created = Impressora.objects.get_or_create(
            nome="UV-Pro-01",
            defaults={
                "tipo": "uv",
                "status": "ativo",
                "localizacao": "Galpão A - Setor 1",
                "fabricante": "EpsonPro",
                "modelo": "UV-Pro 3000",
            },
        )
        self._log("Impressora: UV-Pro-01 (ativa)", created)

        # ─── 7. Pedidos ────────────────────────────────────────────────────────
        self.stdout.write("\n🛒 Criando pedidos...")
        from orders.models import Pedido, ItemPedido
        from orders.services import PedidoService

        # Pedido criado (sem pagamento)
        pedido_criado = Pedido.objects.filter(
            usuario=usuario_comum,
            status_pedido="criado",
        ).first()
        if not pedido_criado:
            pedido_criado = PedidoService.criar_pedido(usuario_comum, artista)
            PedidoService.adicionar_item(
                pedido=pedido_criado,
                produto=produtos[1],
                personalizacao=Personalizacao.objects.create(
                    produto=produtos[1],
                    arte=artes[1],
                    texto="Maria Demo",
                    fonte="Georgia",
                    cor="#34a853",
                ),
                quantidade=1,
                preco_unitario=Decimal("44.90"),
            )
            created = True
        else:
            created = False
        self._log(f"Pedido criado #{pedido_criado.pk}", created)

        # Pedido pago
        pedido_pago = Pedido.objects.filter(
            usuario=usuario_staff,
            status_pedido="pago",
        ).first()
        if not pedido_pago:
            pedido_pago = PedidoService.criar_pedido(usuario_staff, artista)
            PedidoService.adicionar_item(
                pedido=pedido_pago,
                produto=produtos[2],
                personalizacao=Personalizacao.objects.create(
                    produto=produtos[2],
                    arte=artes[2],
                    texto="Staff Capinha",
                    fonte="Roboto",
                    cor="#ea4335",
                ),
                quantidade=1,
                preco_unitario=Decimal("39.90"),
            )
            PedidoService.confirmar_pagamento(pedido_pago, "pix", "confirmado")
            created = True
        else:
            created = False
        self._log(f"Pedido pago #{pedido_pago.pk}", created)

        # ─── 8. Payment simulado ───────────────────────────────────────────────
        self.stdout.write("\n💳 Criando pagamento simulado...")
        from payments.models import Payment

        payment, created = Payment.objects.get_or_create(
            pedido=pedido_pago,
            defaults={
                "usuario": usuario_staff,
                "amount": pedido_pago.valor_total,
                "method": "pix",
                "status": "paid",
                "paid_at": timezone.now(),
            },
        )
        self._log(f"Payment #{payment.pk} (pix, paid)", created)

        # ─── 9. Fila de impressão ──────────────────────────────────────────────
        self.stdout.write("\n📋 Criando item na fila de impressão...")
        from printing.models import FilaImpressao

        # Mover pedido pago para produção (necessário para fila)
        if pedido_pago.status_pedido == "pago":
            try:
                PedidoService.enviar_para_producao(pedido_pago)
            except ValueError:
                pass  # Já está em produção

        fila, created = FilaImpressao.objects.get_or_create(
            pedido=pedido_pago,
            defaults={
                "impressora": impressora,
                "status": "aguardando",
                "prioridade": 1,
                "observacoes": "Pedido de demonstração.",
            },
        )
        self._log(f"Fila de impressão #{fila.pk} (aguardando)", created)

        # ─── Resumo ────────────────────────────────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("\n=== ✅ Seed concluído! ===\n"))
        self.stdout.write("📊 Resumo dos dados de demonstração:")
        self.stdout.write(f"  - Usuários criados/verificados: 3")
        self.stdout.write(f"  - Artistas: 1")
        self.stdout.write(f"  - Produtos: {len(produtos)}")
        self.stdout.write(f"  - Coleções: 2")
        self.stdout.write(f"  - Artes: {len(artes)}")
        self.stdout.write(f"  - Pedidos: 2 (1 criado + 1 pago)")
        self.stdout.write(f"  - Impressoras: 1")
        self.stdout.write(f"  - Itens na fila: 1")
        self.stdout.write("\n🔑 Credenciais de acesso:")
        self.stdout.write("  cliente@capinha.com  /  capinha123  (usuário comum)")
        self.stdout.write("  staff@capinha.com    /  capinha123  (staff/produção)")
        self.stdout.write("  artista@capinha.com  /  capinha123  (artista aprovado)")
        self.stdout.write(self.style.SUCCESS("\n🚀 Acesse http://127.0.0.1:8000/ e faça login!\n"))
