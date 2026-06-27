# 🚀 Checklist Final de Publicação - GreenCase MVP

Este documento serve como guia de verificação final para a publicação do projeto **GreenCase** no GitHub, LinkedIn e preparação para entrevistas.

## 📁 1. Preparação de Arquivos e Git
- [ ] **Testes Passando:** Garantir que todos os 130+ testes automatizados rodem sem erros (`python manage.py test`).
- [ ] **Ambiente Limpo:** Certificar que o arquivo `.env` com chaves reais e senhas locais **não** foi adicionado ao Git (verificar `.gitignore`).
- [ ] **Exemplo do Env:** Garantir que o `.env.example` está atualizado com as chaves necessárias (mas sem os valores reais).
- [ ] **Seed Demo Funcional:** Executar `python manage.py seed_demo` em um banco limpo para garantir que a carga de demonstração funciona de ponta a ponta sem erros.
- [ ] **Tags de Versão:** Criar a tag Git para a versão inicial:
  ```bash
  git tag -a v1.0.0 -m "Release v1.0.0: MVP funcional de portfólio"
  ```

## 📸 2. Mídia e Documentação Visual
- [ ] **Capturar Screenshots:** Obter capturas das seguintes telas (salvar em `docs/screenshots/`):
  1. Home (Landing Page)
  2. Sobre o Projeto
  3. Como Testar (Timeline e credenciais)
  4. Catálogo de Produtos
  5. Galeria de Artes
  6. Editor de Personalização
  7. Carrinho de Compras
  8. Detalhe do Pedido
  9. Pagamento Simulado
  10. Fila de Impressão
  11. Painel do Artista
  12. Gerenciamento de Artes (CRUD)
  13. Gerenciamento de Coleções (CRUD)
- [ ] **Gravar Vídeo de Demonstração:** Gravar um vídeo curto (30 a 60 segundos) sem áudio ou com narração rápida, percorrendo o fluxo:
  - *Produto → Arte → Personalização → Carrinho → Pedido → Pagamento → Impressão → Painel do Artista*.
  - Salvar ou linkar em `docs/demo/` ou hospedar no YouTube/Vimeo.

## 🌐 3. Presença Online e Portfólio
- [ ] **Repositório Público:** Garantir que o repositório no GitHub está configurado como **Público**.
- [ ] **Descrição do Repositório (About):** Atualizar a descrição curta do repositório no GitHub para:
  > *MVP Django/DRF de uma plataforma de personalização e venda de GreenCases, com carrinho, editor visual, painel do artista, pagamento simulado, fila de produção, seed demo e testes automatizados.*
- [ ] **Fixar Projeto:** Adicionar o repositório à seção de **Pinned Projects (Fixados)** no perfil do GitHub.
- [ ] **Publicar no LinkedIn:** Fazer o post de apresentação com o texto sugerido e anexar o vídeo ou screenshots.
