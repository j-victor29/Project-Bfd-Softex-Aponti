# 🎨 Capinha – Plataforma de Capinhas Personalizadas

> Plataforma MVP para personalização e venda de capinhas de celular com artes de artistas independentes.

---

## 📌 Descrição

**Capinha** é uma plataforma web desenvolvida em Django que conecta artistas independentes a clientes que desejam capinhas de celular personalizadas. O fluxo completo do MVP vai desde a escolha do produto até a impressão e entrega.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Papel |
|---|---|---|
| Python | 3.10+ | Linguagem principal |
| Django | 5.2.7 | Framework web |
| Django REST Framework | 3.15.2 | API REST |
| django-filter | 24.3 | Filtros de API |
| python-decouple | 3.8 | Variáveis de ambiente |
| Pillow | 10.4.0 | Processamento de imagens |
| SQLite | built-in | Banco de dados (desenvolvimento) |

---

## 📁 Apps do Sistema

| App | Responsabilidade |
|---|---|
| `core` | Configurações globais, URLs raiz, settings |
| `users` | Autenticação e gestão de usuários personalizados |
| `artists` | Perfil de artistas e aprovação |
| `products` | Catálogo de produtos (capinhas, cases, acessórios) |
| `creations` | Artes, coleções e personalizações |
| `orders` | Pedidos e itens do pedido |
| `payments` | Simulação de pagamentos |
| `printing` | Fila de impressão e produção |
| `gamification` | Módulo de recompensas e badges (em desenvolvimento) |

---

## 🔄 Fluxo Principal do MVP

```
Produto → Arte → Personalização → Carrinho → Pedido → Pagamento Simulado → Fila de Impressão → Produção → Impresso
```

1. **Produto** – Cliente escolhe o modelo de capinha em `/products/`
2. **Arte** – Cliente escolhe uma arte de um artista em `/creations/artes/`
3. **Personalização** – Cliente adiciona texto, fonte e cor em `/creations/personalizar/`
4. **Carrinho** – A personalização é adicionada ao carrinho de compras em `/carrinho/`
5. **Pedido** – Ao finalizar o carrinho, o sistema cria o pedido correspondente
6. **Pagamento** – Cliente simula o pagamento em `/payments/pagar/<id>/`
7. **Fila de Impressão** – Pedido pago é enviado para `/printing/fila/`
8. **Produção** – Staff inicia e conclui a impressão
9. **Impresso** – Pedido muda para status `impresso`


---

## 🚀 Como Instalar e Executar

### 1. Clonar o Repositório

```bash
git clone https://github.com/j-victor29/capinha.git
cd capinha
```

### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS
```

Edite o `.env` e configure:

```env
SECRET_KEY=uma-chave-secreta-muito-segura-aqui
DEBUG=True
ALLOWED_HOSTS=*,localhost,127.0.0.1
```

### 5. Aplicar Migrations

```bash
python manage.py migrate
```

### 6. Criar Superusuário (Opcional)

```bash
python manage.py createsuperuser
```

### 7. Popular com Dados de Demonstração

```bash
python manage.py seed_demo
```

Saída esperada:
```
=== 🌱 Seed Demo: Capinha MVP ===

👤 Criando usuários...
  [CRIADO] Usuário comum: cliente@capinha.com / capinha123
  [CRIADO] Usuário staff: staff@capinha.com / capinha123
  [CRIADO] Usuário artista: artista@capinha.com / capinha123
...
=== ✅ Seed concluído! ===
```

### 8. Rodar o Servidor

```bash
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000/**

---

## 🧪 Rodando os Testes

```bash
# Todos os testes
python manage.py test

# Testes por app específico
python manage.py test products
python manage.py test creations
python manage.py test cart
python manage.py test orders
python manage.py test payments
python manage.py test printing

# Com verbosidade
python manage.py test --verbosity=2
```

### Verificação do Sistema

```bash
python manage.py check
python manage.py makemigrations --check
```

---

## 🗺️ Rotas Principais

### Rotas HTML (Templates)

| Rota | Descrição | Autenticação |
|---|---|---|
| `/` | Página inicial | Não |
| `/login/` | Login | Não |
| `/logout/` | Logout | Sim |
| `/products/` | Lista de produtos | Não |
| `/products/<id>/` | Detalhe do produto | Não |
| `/creations/` | Dashboard de criações | Não |
| `/creations/artes/` | Galeria de artes | Não |
| `/creations/artes/<id>/` | Detalhe da arte | Não |
| `/creations/colecoes/` | Lista de coleções | Não |
| `/creations/personalizar/` | Criar personalização | **Sim** |
| `/creations/personalizar/salvar/` | Salvar personalização (POST) | **Sim** |
| `/carrinho/` | Visualizar carrinho | **Sim** |
| `/carrinho/adicionar/<personalizacao_id>/` | Adicionar personalização ao carrinho | **Sim** |
| `/carrinho/atualizar/<item_id>/` | Atualizar quantidade (POST) | **Sim** |
| `/carrinho/remover/<item_id>/` | Remover item | **Sim** |
| `/carrinho/finalizar/` | Finalizar carrinho e criar pedido | **Sim** |
| `/orders/` | Lista de pedidos do usuário | **Sim** |
| `/orders/<id>/` | Detalhe do pedido | **Sim** |
| `/orders/criar-do-item/` | Criar pedido da personalização | **Sim** |
| `/orders/<id>/enviar-impressao/` | Enviar pedido para fila | **Sim** |
| `/payments/pagar/<pedido_id>/` | Simular pagamento | **Sim** |
| `/printing/` | Lista de impressoras | **Staff** |
| `/printing/<id>/` | Detalhe da impressora | **Staff** |
| `/printing/fila/` | Fila de impressão | **Staff** |
| `/printing/fila/<id>/status/` | Atualizar status da fila | **Staff** |
| `/admin/` | Painel administrativo | **Superuser** |

### Rotas API REST

| Rota | Descrição |
|---|---|
| `/carrinho/api/carrinho/` | Ver/finalizar carrinho atual |
| `/carrinho/api/itens/` | CRUD dos itens do carrinho |
| `/products/api/produtos/` | CRUD de produtos |
| `/creations/api/artes/` | CRUD de artes |
| `/creations/api/colecoes/` | CRUD de coleções |
| `/creations/api/personalizacoes/` | CRUD de personalizações |
| `/orders/api/orders/` | CRUD de pedidos |
| `/payments/api/payments/` | CRUD de pagamentos |
| `/printing/api/impressoras/` | CRUD de impressoras |

---

## 👥 Usuários de Demonstração

Criados pelo comando `python manage.py seed_demo`:

| Email | Senha | Tipo | Acesso |
|---|---|---|---|
| `cliente@capinha.com` | `capinha123` | Usuário comum | Personalizar, pedir, pagar |
| `staff@capinha.com` | `capinha123` | Staff/Produção | Fila de impressão |
| `artista@capinha.com` | `capinha123` | Artista aprovado | Dashboard de criações |

---

## ✅ Checklist de Teste Manual

Siga este roteiro para validar o fluxo completo do MVP:

### Pré-requisito
- Servidor rodando: `python manage.py runserver`
- Dados populados: `python manage.py seed_demo`

### Fluxo do Cliente

**1.** Acesse `http://127.0.0.1:8000/products/`
- Deve ver a lista de produtos ativos

**2.** Clique em **"Personalizar"** em um produto
- Deve ver a galeria de artes disponíveis

**3.** Escolha uma arte e clique **"Personalizar com esta Arte"**
- Deve abrir o formulário de personalização

**4.** Preencha texto, fonte e cor e clique **"Salvar e Criar Pedido"** (ou Adicionar ao Carrinho)
- Deve criar a personalização, adicioná-la ao carrinho de compras e redirecionar para a tela do carrinho (`/carrinho/`)
- Deve exibir a mensagem de sucesso: *"Personalização adicionada ao carrinho com sucesso."*

**5.** Na tela do carrinho (`/carrinho/`):
- Altere a quantidade de um item e clique no botão de atualizar (ícone de recarregar). Verifique se o subtotal e o total foram recalculados
- Se quiser, adicione outra personalização para ver ambos os itens juntos no carrinho
- Clique em **"Finalizar Pedido"**
- Deve criar o pedido correspondente e redirecionar para o detalhe do pedido (`/orders/<id>/`)

**6.** Verifique o **detalhe do pedido** (`/orders/<id>/`)
- Status deve ser `Criado`
- Itens do pedido devem exibir os produtos e artes corretos

**7.** Clique em **"Pagar"** e vá para a tela de pagamento (`/payments/pagar/<id>/`)
- Deve exibir o valor total do pedido e opções de método

**8.** Selecione **PIX** e clique **"Confirmar Pagamento"**
- Deve redirecionar para o detalhe do pedido com status `Pago`

**9.** Clique em **"Enviar para Impressão"**
- Deve criar uma entrada na fila de impressão
- Status do pedido muda para `Em Produção`

### Fluxo do Staff

**10.** Faça logout e login com `staff@capinha.com` / `capinha123`

**11.** Acesse `http://127.0.0.1:8000/printing/fila/`
- Deve ver o pedido na fila com status `Aguardando`

**12.** Clique em **"Iniciar Produção"** (status → `imprimindo`)
- O campo `iniciado_em` deve ser preenchido

**13.** Clique em **"Concluir Impressão"** (status → `concluído`)
- O campo `concluido_em` deve ser preenchido

**14.** Volte ao detalhe do pedido (`/orders/<id>/`)
- Status do pedido deve ser `Impresso` ✅

### Validações de Segurança

**15.** Tente acessar `/printing/fila/` com usuário comum
- Deve receber **403 Forbidden**

**16.** Tente acessar `/orders/<id>/` de outro usuário
- Deve receber **404 Not Found**

**17.** Tente acessar `/creations/personalizar/` sem login
- Deve ser redirecionado para `/login/`

**18.** Tente acessar `/carrinho/` sem login
- Deve ser redirecionado para `/login/`

---

## 📊 Status Atual do Projeto

| Funcionalidade | Status |
|---|---|
| Autenticação de usuários | ✅ Completo |
| Catálogo de produtos | ✅ Completo |
| Galeria de artes e coleções | ✅ Completo |
| Sistema de personalização | ✅ Completo |
| Carrinho de compras | ✅ Completo |
| Criação e gestão de pedidos | ✅ Completo |
| Simulação de pagamentos | ✅ Completo |
| Fila de impressão | ✅ Completo |
| Proteção de rotas e permissões | ✅ Completo |
| Prevenção de pedidos duplicados | ✅ Completo |
| Testes automatizados (45+) | ✅ Completo |
| Seed de dados de demonstração | ✅ Completo |
| Painel administrativo (admin) | ✅ Completo |
| Sistema de gamificação | 🔄 Em desenvolvimento |
| Painel do artista | 🔜 Futuro |

---

## 🔮 Funcionalidades Futuras

1. **Carrinho de Compras** – Múltiplos itens antes de gerar pedido
2. **Painel do Artista** – Dashboard de vendas e comissões
3. **Editor Visual 3D** – Preview da capinha em tempo real
4. **PIX Real** – Integração com API de pagamentos reais
5. **Notificações por E-mail** – Status do pedido por e-mail
6. **Rastreamento de Entrega** – Integração com transportadoras
7. **Avaliações** – Sistema de review de produtos e artistas
8. **App Mobile** – Versão React Native

---

## 👨‍💻 Desenvolvimento

```bash
# Verificar saúde do projeto
python manage.py check

# Criar migrações pendentes
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Rodar todos os testes
python manage.py test

# Rodar testes do Painel do Artista
python manage.py test artists --verbosity=2

# Popular dados de demonstração
python manage.py seed_demo

# Rodar servidor de desenvolvimento
python manage.py runserver
```

---

## 🎨 Painel do Artista

O **Painel do Artista** é uma área restrita que permite ao artista acompanhar suas criações, métricas de vendas e comissões estimadas.

### Rotas

| Rota | Descrição |
|---|---|
| `/artists/painel/` | Painel principal com métricas e últimos pedidos |
| `/artists/painel/artes/` | Gerenciamento de artes cadastradas |
| `/artists/painel/colecoes/` | Gerenciamento de coleções |

### Permissões

| Perfil | Acesso |
|---|---|
| Usuário anônimo | Redirecionado para `/login/` |
| Usuário comum (cliente) | `403 Forbidden` |
| Artista pendente ou bloqueado | `403 Forbidden` |
| Artista aprovado | ✅ Acessa apenas seus próprios dados |
| Superuser | ✅ Acessa (painel vazio se não tiver perfil de artista) |

### Métricas exibidas

- Total de artes cadastradas
- Total de coleções
- Total de itens vendidos (que usaram suas artes)
- **Comissão estimada** = 10% do subtotal de todos os itens de pedido que usam suas artes
- Últimos 5 pedidos com suas artes
- Top 5 artes mais utilizadas

### Como testar manualmente

```bash
# 1. Popular dados de demonstração
python manage.py seed_demo

# 2. Iniciar o servidor
python manage.py runserver

# 3. Fazer login com o artista aprovado
#    Email: artista@capinha.com | Senha: capinha123

# 4. Clicar em "Painel do Artista" na barra de navegação
#    ou acessar diretamente: http://127.0.0.1:8000/artists/painel/
```

### Como rodar os testes do painel

```bash
# Testes específicos do Painel do Artista
python manage.py test artists --verbosity=2

# Todos os testes do projeto
python manage.py test --verbosity=2
```

---

*Projeto desenvolvido como MVP da plataforma Capinha. Todos os pagamentos são simulados e não há integração real com meios de pagamento.*
