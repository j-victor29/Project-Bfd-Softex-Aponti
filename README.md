# 🎨 Capinha — Plataforma de Personalização de Capinhas

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST%20Framework-red?style=flat&logo=django)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=flat&logo=sqlite)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat&logo=bootstrap&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-Automatizados-success?style=flat&logo=pytest)
![MVP](https://img.shields.io/badge/Status-MVP%20Portfolio-informational?style=flat)

> **Projeto de portfólio** demonstrando um sistema web completo com Django. O objetivo é mostrar domínio de arquitetura modular, fluxo de e-commerce completo, testes automatizados, segurança por permissões e organização de código profissional.

---

## 📋 Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Arquitetura por Apps](#arquitetura-por-apps)
- [Fluxo do Sistema](#fluxo-do-sistema)
- [Perfis de Usuário](#perfis-de-usuário)
- [Como Instalar](#como-instalar)
- [Como Rodar](#como-rodar)
- [Usuários de Demonstração](#usuários-de-demonstração)
- [Checklist de Teste Manual](#checklist-de-teste-manual)
- [Diferenciais Técnicos](#diferenciais-técnicos)
- [Roadmap Futuro](#roadmap-futuro)
- [Roteiro de Apresentação](#roteiro-de-apresentação)

---

## 📖 Sobre o Projeto

**Capinha** é um MVP de plataforma de personalização e venda de capinhas para celular, desenvolvido como projeto de portfólio para demonstrar habilidades full-stack em Django.

O sistema simula o ciclo completo de um e-commerce de produtos personalizados:

1. Artistas independentes cadastram suas artes e coleções no sistema
2. Clientes navegam pelo catálogo, escolhem produtos e personalizam via editor 2D
3. A equipe de produção (staff) gerencia a fila de impressão dos pedidos pagos

> ⚠️ O pagamento neste MVP é **simulado** (sem API real) para fins de portfólio. O foco é demonstrar a arquitetura do sistema, não integrar gateways de pagamento.

---

## ✅ Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 🛍️ Catálogo de Produtos | Listagem, busca e filtro por categoria |
| 🎨 Artes e Estampas | Biblioteca de designs criados por artistas parceiros |
| ✏️ Editor 2D | Personalização visual com texto, cor, fonte e posicionamento |
| 🛒 Carrinho de Compras | Carrinho persistente com personalização detalhada |
| 📦 Pedidos | Ciclo de vida completo: criado → pago → em produção → impresso |
| 💳 Pagamento Simulado | Confirmação de pagamento por método (Pix/Cartão) sem API real |
| 🖨️ Fila de Impressão | Painel de produção com controle de status e impressoras |
| 🎭 Painel do Artista | Dashboard exclusivo com métricas de vendas e CRUD de artes/coleções |
| 🏆 Gamificação | Sistema de pontos, badges e ranking para artistas |
| 👥 Autenticação | Controle de acesso por perfil de usuário |

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django 5.x, Django REST Framework, Python 3.11+
- **Banco de Dados:** SQLite (facilmente substituível por PostgreSQL)
- **Frontend:** Bootstrap 5, HTML/CSS customizado, JavaScript vanilla
- **Autenticação:** `django.contrib.auth` com modelo de usuário customizado
- **Gerenciamento de dependências:** pip / requirements.txt
- **Configuração:** python-decouple para variáveis de ambiente

---

## 📁 Arquitetura por Apps

O projeto segue o princípio de responsabilidade única, com cada app tendo escopo bem definido:

```
capinha/
├── core/           # Configurações, URLs raiz, views institucionais, seed_demo
├── users/          # Modelo de usuário customizado (AUTH_USER_MODEL)
├── products/       # Catálogo de produtos (Produto)
├── artists/        # Perfil de artista, painel e métricas (Artista)
├── creations/      # Artes, Coleções e Personalizações (Arte, Colecao, Personalizacao)
├── cart/           # Carrinho de compras (Carrinho, ItemCarrinho)
├── orders/         # Pedidos e itens (Pedido, ItemPedido, PedidoService)
├── payments/       # Pagamento simulado (Payment)
├── printing/       # Fila de impressão e impressoras (FilaImpressao, Impressora)
└── gamification/   # Pontos, badges e ranking (Ponto, Badge, Ranking)
```

---

## 🔄 Fluxo do Sistema

```
[Cliente] → Escolhe Produto
         → Seleciona Arte (do artista)
         → Editor 2D (texto, cor, fonte, posição)
         → Adiciona ao Carrinho
         → Checkout → Pagamento Simulado
         
[Staff]  → Vê pedido pago na Fila de Impressão
         → Gerencia impressora e status
         → Atualiza: aguardando → imprimindo → concluído
         
[Artista]→ Painel do Artista
         → Métricas de vendas / faturamento
         → CRUD de Artes e Coleções
```

---

## 👥 Perfis de Usuário

| Perfil | Acesso |
|--------|--------|
| **Cliente** | Produtos, Editor, Carrinho, Pedidos, Pagamento Simulado |
| **Artista** | Tudo do Cliente + Painel do Artista (CRUD de artes/coleções, métricas) |
| **Staff** | Tudo do Cliente + Produção (Fila de Impressão, Impressoras, Todos os Pedidos) |
| **Admin** | Acesso total ao Django Admin |

---

## ⚙️ Como Instalar

### Pré-requisitos
- Python 3.11+
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/capinha.git
cd capinha

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## 🔑 Como Configurar o `.env`

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

> Um `.env.example` já está incluído no repositório como referência.

---

## 🗄️ Como Rodar Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🌱 Como Popular Dados Demo

```bash
python manage.py seed_demo
```

Isso criará automaticamente (de forma idempotente):
- 3 usuários (cliente, artista aprovado, staff)
- Produtos, artes e coleções de exemplo
- Pedidos em diferentes estados (criado, pago, em produção)
- Fila de impressão e impressora
- Pagamento simulado

---

## 🧪 Como Rodar os Testes

```bash
# Todos os testes
python manage.py test --verbosity=2

# Apenas os testes do core (páginas e navbar)
python manage.py test core --verbosity=2

# Apenas os testes do carrinho
python manage.py test cart --verbosity=2

# Apenas os testes de criações
python manage.py test creations --verbosity=2
```

---

## 🚀 Como Iniciar o Servidor

```bash
python manage.py runserver
```

Acesse: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔑 Usuários de Demonstração

Após rodar `seed_demo`, os seguintes usuários estarão disponíveis:

| E-mail | Senha | Perfil |
|--------|-------|--------|
| `cliente@capinha.com` | `capinha123` | Cliente (usuário comum) |
| `artista@capinha.com` | `capinha123` | Artista aprovado |
| `staff@capinha.com` | `capinha123` | Staff / Produção |

---

## 📋 Checklist de Teste Manual

- [ ] Acessar `/` e ler a landing page do projeto
- [ ] Acessar `/sobre/` e `/como-testar/`
- [ ] Login como **cliente** → Produtos → Escolher produto → Editor 2D → Carrinho → Checkout → Pagamento Simulado
- [ ] Login como **staff** → Produção → Fila de Impressão → Avançar status do pedido
- [ ] Login como **artista** → Painel do Artista → Ver métricas → Cadastrar nova arte → Criar coleção
- [ ] Verificar que links de `Produção` não aparecem para cliente
- [ ] Verificar que `Painel do Artista` não aparece para cliente comum

---

## ⭐ Diferenciais Técnicos

| Diferencial | Descrição |
|-------------|-----------|
| 🏗️ **Arquitetura modular** | 9 apps Django com responsabilidade bem definida |
| 🧪 **Testes automatizados** | Cobertura de fluxos de carrinho, permissões de artista, páginas institucionais |
| 🔐 **Permissões por perfil** | Links e views protegidos por decorators e condicionais de template |
| 🛡️ **Transações atômicas** | Uso de `transaction.atomic` em operações críticas do carrinho e pedidos |
| 🌱 **Seed idempotente** | `seed_demo` pode ser executado múltiplas vezes sem criar duplicatas |
| 📊 **Painel do Artista** | Dashboard com métricas de faturamento e CRUD completo de artes |
| 🎨 **Editor 2D** | Personalização visual em tempo real com persistência no banco |
| 📋 **Fila de Produção** | Ciclo completo de pedido até impressão física com gestão de status |
| 🛒 **Carrinho persistente** | Carrinho salvo no banco com personalização detalhada vinculada |
| 🏆 **Gamificação** | Sistema de pontos, badges e ranking para engajamento de artistas |
| 📝 **Validações robustas** | Formulários validados no backend + proteção CSRF |
| 🎨 **UI Moderna** | Interface dark/glassmorphism com Bootstrap 5, responsiva e animada |

---

## 🗺️ Roadmap Futuro

As seguintes melhorias estão planejadas para versões futuras, mas **não foram implementadas neste MVP** para manter a simplicidade:

- [ ] Integração com **Mercado Pago / Stripe** para pagamento real
- [ ] Integração com API de **frete** (Correios / Melhor Envio)
- [ ] **Notificações por WhatsApp** (via Twilio ou Evolution API)
- [ ] **Editor 3D** com Three.js para preview mais realista
- [ ] **Deploy em produção** (Railway, Heroku ou VPS)
- [ ] Autenticação com **OAuth** (Google, GitHub)
- [ ] **API REST pública** com autenticação por Token para integrações

---

## 🎙️ Roteiro de Apresentação

Para apresentar o projeto em entrevistas técnicas, siga este roteiro sugerido:

### 1. Introdução (30s)
> "Construí o Capinha para simular o back-end de um e-commerce de personalização. A ideia é mostrar como organizar um sistema Django modular com fluxo de compra completo."

### 2. Mostrar a Home e as páginas institucionais
- Acesse `/` e explique os módulos
- Mostre `/sobre/` para explicar a arquitetura
- Mostre `/como-testar/` para orientar o avaliador

### 3. Demonstrar o fluxo de cliente
- Login como `cliente@capinha.com`
- Produtos → Escolher → Editor 2D → Carrinho → Checkout → Pagamento Simulado

### 4. Demonstrar o fluxo de staff
- Login como `staff@capinha.com`
- Menu Produção → Fila de Impressão → Avançar status

### 5. Demonstrar o painel do artista
- Login como `artista@capinha.com`
- Painel do Artista → Métricas → CRUD de artes

### 6. Mostrar os testes
```bash
python manage.py test --verbosity=2
```

### 7. Mostrar a organização do código
- Estrutura de apps, services.py, models.py, tests.py
- Destacar o uso de `transaction.atomic` no `PedidoService`
- Mostrar as permissões nos decorators das views

### 8. Fechar com o roadmap
> "Para produção, eu adicionaria Mercado Pago, notificações por WhatsApp e faria o deploy no Railway. O sistema já está estruturado para receber essas integrações sem refatoração maior."

---

*Desenvolvido por João Victor — 2026*
