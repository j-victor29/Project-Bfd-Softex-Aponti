# 💼 Sugestão de Post para o LinkedIn

*Aqui está um roteiro/texto profissional pronto para postar no seu perfil do LinkedIn. Ajuste os detalhes conforme necessário.*

---

🚀 **Novo Projeto no Portfólio: GreenCase — MVP de E-commerce & Personalização**

Desenvolvi recentemente o **GreenCase**, um sistema web completo que simula uma plataforma de e-commerce e personalização de GreenCases de celular. 

O foco deste projeto foi ir além de uma interface simples ou um CRUD básico: criei uma arquitetura modular real com fluxos operacionais completos, cobrindo o ciclo de ponta a ponta desde a criação artística até a fila de produção final.

### 🛠️ Tecnologias Utilizadas:
- **Backend:** Django & Django REST Framework (Python)
- **Frontend:** Bootstrap 5, Javascript Vanilla, HTML/CSS customizado
- **Banco de Dados:** SQLite (com transações seguras via Django ORM)
- **Testes:** Django Test Suite (mais de 130 testes automatizados cobrindo carrinho, checkout, fluxos e permissões)

### 🎨 Principais Funcionalidades:
1. **Editor de Personalização 2D:** Permite customizar cores de fundo, textos, fontes e posicionamento no produto.
2. **Carrinho Persistente:** Armazena e detalha múltiplos itens personalizados vinculados a artes de criadores.
3. **Checkout e Pagamento Simulado:** Sistema que processa transações de forma atômica (`transaction.atomic`) e simula aprovação de pagamentos.
4. **Fila de Impressão (Produção):** Painel para equipe administrativa (Staff) gerenciar impressoras e avançar o status dos pedidos.
5. **Painel do Artista (Dashboard):** Um portal para artistas parceiros gerenciarem suas estampas/coleções e acompanharem faturamento e métricas de vendas.
6. **Gamificação:** Sistema simples de pontuação, rankings e conquista de badges para engajar os artistas.

### 🧠 Principais Aprendizados e Diferenciais Técnicos:
- **Arquitetura Modular:** Separação lógica em 9 apps Django independentes com responsabilidades bem definidas.
- **Segurança por Perfis:** Proteção de views e menus na navbar dependendo do tipo de usuário (Cliente, Artista ou Staff).
- **Dados Idempotentes:** Criação de um comando personalizado `seed_demo` para popular o sistema com dados de teste realistas sem duplicidade.
- **Robustez com Testes:** Criação de testes unitários e de integração para mitigar regressões críticas de lógica e fluxo de compra.

O código está aberto para quem quiser analisar, rodar localmente (há credenciais demo prontas no repositório) ou contribuir!

🔗 **Link do repositório no GitHub:** https://github.com/j-victor29/Project-Bfd-Softex-Aponti

#django #python #backend #webdevelopment #portfolio #softwareengineering #github #programacao
