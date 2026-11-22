# Tem Mimo Aqui Ateliê

Site público em português brasileiro, com quatro páginas estáticas e catálogo inspirado na edição **V8 – Apresentação** do PDF do ateliê. Atendimento e encomendas são feitos pelo Instagram **@temmimoaqui.atelie**. O pagamento é combinado durante o atendimento e feito via PIX.

## Estrutura no monorepo

- `website/` contém as páginas HTML, os estilos, o JavaScript, o catálogo e as mídias públicas.
- `website/catalogo.json` concentra produtos, categorias, coleções, fotos, logotipo, PDF, Instagram e texto de pagamento.
- `website/assets/images/` contém os arquivos oficiais. `website/imgs/` também aceita novas imagens.
- `website/scripts/publicar.py` gera as áreas compartilhadas, valida as referências do site e prepara o artefato público.
- `.github/workflows/deploy-website.yml`, na raiz do monorepo, publica apenas o site.

## Prévia local

Na raiz do repositório, use Python 3.11 ou superior, sem instalar bibliotecas adicionais.

```bash
python3 website/scripts/publicar.py --atualizar-html
python3 -m http.server 8000 --directory website
```

Abra [a página inicial](http://localhost:8000/). As páginas, os produtos e os links funcionam com JavaScript desativado. Os filtros, os efeitos de entrada e as transições complementam o HTML quando o navegador oferece suporte.

Para simular um site de projeto, gere o artefato dentro de uma subpasta de um diretório temporário e sirva o diretório pai.

```bash
previa=$(mktemp -d)
python3 website/scripts/publicar.py --saida "$previa/atelie"
python3 -m http.server 8001 --directory "$previa"
```

Abra [a prévia no caminho do projeto](http://localhost:8001/atelie/).

## Atualizar catálogo, imagens e contatos

1. Edite `catalogo.json`. Cada produto tem um `id` único, `nome`, `categoria`, `edicao`, `descricao`, `preco` em reais e uma referência `imagem`. A ordem de `edicoes` e dos produtos define a sequência das coleções e dos cards. `vitrine` lista os destaques da página inicial. Cadastre o preço com ponto decimal, como `46.50`. Use `null` para exibir “Valor sob consulta”.
2. Coloque as imagens em `assets/images/products/`, `assets/images/logo/` ou `imgs/`. Em `fotos`, cadastre cada caminho relativo ao site com texto alternativo e dimensões reais em pixels. Use a chave dessa foto em `imagem`. Use `null` enquanto aguarda uma foto confirmada. O logotipo segue o mesmo formato de uma entrada de `fotos`.
3. Mantenha o arquivo original ao adicionar versões responsivas. Em `versoes`, informe os caminhos e as larguras reais das cópias WebP ou AVIF. O navegador escolhe a largura de acordo com a tela. Preserve enquadramento, proporções, cores e rótulos.
4. Se houver nova edição, atualize os produtos e o arquivo público em `assets/catalogo/` na mesma mudança. O campo `pdf` controla o link para download. O valor `null` oculta esse link.
5. Atualize `instagram` se o perfil oficial mudar e `pagamento` para revisar o texto de PIX. O gerador atualiza todos os links de atendimento e o nome de usuário exibido. O site dispensa chaves, credenciais e serviços de contato.
6. Execute `python3 website/scripts/publicar.py --atualizar-html` e confira a prévia. Edite o conteúdo livre dos arquivos HTML fora dos trechos marcados por `inicio` e `fim`. O workflow sempre recria esses trechos a partir do JSON.

## Publicar no GitHub Pages

1. No repositório, abra **Settings → Pages → Build and deployment** e selecione **GitHub Actions** em **Source**. A disponibilidade do Pages depende da visibilidade do repositório e do plano da conta.
2. Faça merge na branch padrão `main`. Pushes em `main` que alterem `website/**` ou o próprio workflow disparam **Publicar site do ateliê**. Mudanças em outras aplicações ficam fora do gatilho. Para restringir o ambiente de produção, selecione `main` em **Settings → Environments → github-pages → Deployment branches and tags**.
3. Para executar manualmente, abra **Actions → Publicar site do ateliê → Run workflow**, selecione `main` e confirme. O workflow precisa estar presente na branch padrão para essa opção aparecer.
4. Acompanhe em **Actions** as etapas **Validar e preparar o site** e **Publicar no GitHub Pages**. Ao concluir, o ambiente `github-pages` informa a URL. Links e arquivos usam caminhos relativos e funcionam em um endereço de projeto no formato `https://USUARIO.github.io/REPOSITORIO/`.

A publicação inclui somente as páginas geradas e as mídias, folhas de estilo e scripts públicos. O artefato contém `index.html` na raiz. O JSON fonte, o gerador, o README e os arquivos das outras aplicações ficam fora dele. As ações oficiais usam o token automático do GitHub.

Se a validação falhar, confira no log o caminho do arquivo, incluindo espaços, acentos e maiúsculas. Se a configuração ou a publicação falhar, confira a fonte **GitHub Actions**, a disponibilidade do Pages e as regras do ambiente `github-pages`. Para uma execução manual ignorada em outra branch, repita a partir de `main`.

Para usar um domínio próprio, informe-o em **Settings → Pages → Custom domain**, configure o DNS com o provedor e ative **Enforce HTTPS** quando o GitHub concluir a verificação. Os caminhos relativos dispensam alterações nas páginas.

- [Publicação com workflows personalizados do GitHub Pages](https://docs.github.com/pt/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Configuração de domínio personalizado no GitHub Pages](https://docs.github.com/pt/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
