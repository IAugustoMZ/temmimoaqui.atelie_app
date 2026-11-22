"""Gera o HTML navegável e prepara o artefato estático do site."""
import argparse
import json
import re
import shutil
from decimal import Decimal, DecimalException
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    ("index.html", "Início"),
    ("catalogo.html", "Nossos Mimos"),
    ("sobre.html", "Sobre o Ateliê"),
    ("contato.html", "Contato"),
)
PUBLIC_DIRS = {
    "assets": {".svg", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".ico", ".pdf", ".woff2"},
    "imgs": {".svg", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".ico"},
    "css": {".css"},
    "js": {".js"},
}
PRODUCT_SIZES = "(min-width: 80rem) 380px, (min-width: 62rem) 30vw, (min-width: 42rem) 45vw, 90vw"


def asset(value):
    path = Path(value)
    if not path.parts or path.parts[0] not in ("assets", "imgs") or ".." in path.parts:
        raise ValueError(f"Caminho de mídia inválido: {value}")
    if not (ROOT / path).is_file() or not (ROOT / path).resolve().is_relative_to(ROOT):
        raise ValueError(f"Arquivo de mídia ausente: {value}")
    return quote(value, safe="/")


def icon(name, extra=""):
    return f'<svg class="icon {extra}" aria-hidden="true"><use href="assets/icons/mimos.svg#{name}"></use></svg>'


def image(photo, sizes, *, priority=False, logo=False):
    src = asset(photo["arquivo"])
    width, height = photo["largura"], photo["altura"]
    if not all(type(n) is int and n > 0 for n in (width, height)):
        raise ValueError(f"Dimensões inválidas: {src}")
    versions = photo.get("versoes", [])
    candidates = []
    for version in versions:
        variant_width = version["largura"]
        if type(variant_width) is not int or variant_width <= 0:
            raise ValueError(f"Largura de imagem inválida: {version}")
        candidates.append(f'{asset(version["arquivo"])} {variant_width}w')
    responsive = f' srcset="{", ".join(candidates)}" sizes="{sizes}"' if candidates else ""
    loading = ' fetchpriority="high"' if priority else ("" if logo else ' loading="lazy"')
    alt = "" if logo else escape(photo["alt"])
    return f'<img src="{src}"{responsive} width="{width}" height="{height}" alt="{alt}"{loading} decoding="async">'


def button(label, config, style="primary", with_icon=True, accessible_label=None):
    mark = icon("instagram") if with_icon else ""
    accessible = f' aria-label="{escape(accessible_label)}"' if accessible_label else ""
    return (f'<a class="button {style} instagram" href="{escape(config["instagram"])}" '
            f'target="_blank" rel="noopener noreferrer"{accessible}>{mark}{escape(label)}</a>')


def navigation(page):
    links = []
    for url, label in PAGES:
        current = ' aria-current="page"' if page == url else ""
        links.append(f'<li><a href="{url}"{current}>{label}</a></li>')
    return "".join(links)


def header(page, config):
    mark = image(config["logo"], "66px", logo=True) if config["logo"] else icon("heart")
    return f'''<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html"><span class="brand-mark">{mark}</span><span class="brand-name">Tem Mimo Aqui<span>Ateliê</span></span></a>
    <nav class="desktop-nav" aria-label="Navegação principal"><ul>{navigation(page)}</ul></nav>
    {button("Encomendar", config, "secondary desktop-order")}
    <details class="mobile-nav">
      <summary><span class="sr-only">Menu principal</span>{icon("menu", "open-icon")}{icon("close", "close-icon")}</summary>
      <nav class="mobile-panel" aria-label="Navegação principal">
        <ul>{navigation(page)}</ul>
        {button("Encomendar", config, "secondary")}
      </nav>
    </details>
  </div>
</header>'''


def footer(config):
    return f'''<footer class="site-footer">
  <div class="wrap footer-grid">
    <div><a class="footer-brand" href="index.html">Tem Mimo Aqui <em>Ateliê</em></a><p>Feito à mão, com carinho, para presentear com amor.</p></div>
    <nav aria-label="Navegação do rodapé"><ul>{navigation(None)}</ul></nav>
    <div class="footer-order"><a class="text-link instagram" href="{escape(config["instagram"])}" target="_blank" rel="noopener noreferrer">{icon("instagram")} Instagram</a><p>Encomendas e atendimento pelo Instagram.</p></div>
  </div>
</footer>'''


def placeholder(kind="gift"):
    return f'<div class="photo-placeholder">{icon(kind)}<span>Fotografia oficial em breve</span></div>'


def photo_or_placeholder(key, config, sizes, **kwargs):
    return image(config["fotos"][key], sizes, **kwargs) if key else placeholder()


def editorial_photo(key, config, hero=False):
    photo = photo_or_placeholder(key, config, "(min-width: 80rem) 620px, (min-width: 54rem) 51vw, 92vw", priority=True)
    return f'<div class="editorial-photo{" hero-photo" if hero else ""}"><div class="photo-mat">{photo}</div><span class="glimmer" aria-hidden="true"></span></div>'


def price_text(value):
    if value is None:
        return "Valor sob consulta"
    value = Decimal(str(value))
    if not value.is_finite() or value < 0 or value != value.quantize(Decimal("0.01")):
        raise ValueError(f"Preço inválido: {value}")
    return "R$ " + f"{value:,.2f}".translate(str.maketrans(",.", ".,"))


def card(product, config, chapter=False):
    category = product["categoria"]
    kind = {"velas": "candle", "aromatizadores": "diffuser", "lembrancinhas": "heart"}.get(category, "gift")
    sizes = "(min-width: 80rem) 650px, (min-width: 54rem) 51vw, 90vw" if chapter else PRODUCT_SIZES
    photo = image(config["fotos"][product["imagem"]], sizes) if product["imagem"] else placeholder(kind)
    return f'''<article class="product-card" data-category="{escape(category)}" data-reveal>
  <div class="product-media">{photo}</div>
  <div class="product-copy">
    <p class="eyebrow product-category">{icon(kind)}{escape(config["categorias"][category])}</p>
    <h3>{escape(product["nome"])}</h3>
    <p class="product-description">{escape(product["descricao"])}</p>
    <p class="price">{price_text(product["preco"])}</p>
    {button("Encomendar pelo Instagram", config, "secondary product-order", with_icon=False, accessible_label=f"Encomendar pelo Instagram · {product['nome']}")}
  </div>
</article>'''


def grid(products, config, *, chapter=False):
    return '<div class="product-grid">' + "\n".join(card(p, config, chapter) for p in products) + '</div>'


def catalog(config):
    sections = []
    for key, edition in config["edicoes"].items():
        products = [p for p in config["produtos"] if p["edicao"] == key]
        if not products:
            continue
        chapter = len(products) == 1
        sections.append(f'''<section class="catalog-edition{' single-edition' if chapter else ''}" data-edition aria-labelledby="{escape(key)}">
  <div class="edition-heading" data-reveal>
    <span class="edition-ornament" aria-hidden="true">{icon("sparkle")}</span>
    <h2 id="{escape(key)}">{escape(edition["titulo"])}</h2>
    <p>{escape(edition["texto"])}</p>
  </div>
  {grid(products, config, chapter=chapter)}
</section>''')
    return '<div id="catalog-results">' + "\n".join(sections) + '</div>'


def filters(config):
    choices = {"todos": "Todos os mimos", **config["categorias"]}
    markup = "".join(
        f'<button type="button" data-filter="{escape(key)}" aria-pressed="{str(key == "todos").lower()}">{escape(label)}</button>'
        for key, label in choices.items()
    )
    return (f'<div class="filters" hidden role="group" aria-label="Filtrar por categoria" '
            f'aria-controls="catalog-results">{markup}</div><p class="sr-only" id="catalog-status" role="status"></p>')


def replace_region(source, name, replacement):
    region = rf'<!-- inicio:{name} -->.*?<!-- fim:{name} -->'
    return re.sub(region, lambda _: f'<!-- inicio:{name} -->{replacement}<!-- fim:{name} -->', source, flags=re.S)


def validate_config(config):
    url = urlsplit(config["instagram"])
    if (url.scheme != "https" or url.netloc != "www.instagram.com"
            or not re.fullmatch(r"/[A-Za-z0-9._]+/", url.path) or url.query or url.fragment):
        raise ValueError("Informe o perfil do Instagram em https://www.instagram.com/NOME_DO_PERFIL/.")
    ids = set()
    for product in config["produtos"]:
        product_id = product["id"]
        if product_id in ids or not re.fullmatch(r"[a-z0-9-]+", product_id):
            raise ValueError(f"Identificador de produto inválido ou duplicado: {product_id}")
        ids.add(product_id)
        if product["categoria"] not in config["categorias"] or product["edicao"] not in config["edicoes"]:
            raise ValueError(f"Categoria ou edição desconhecida em {product_id}")
        if product["imagem"] and product["imagem"] not in config["fotos"]:
            raise ValueError(f"Fotografia desconhecida em {product_id}: {product['imagem']}")
    for key in config["edicoes"]:
        if not re.fullmatch(r"[a-z0-9-]+", key):
            raise ValueError(f"Identificador de edição inválido: {key}")
    if not ids:
        raise ValueError("O catálogo deve ter pelo menos um produto.")


def render(page, config):
    source = (ROOT / page).read_text(encoding="utf-8")
    regions = {
        "cabecalho": header(page, config),
        "rodape": footer(config),
        "pagamento": f'<p class="payment">{escape(config["pagamento"])}</p>',
        "usuario": f'@{escape(urlsplit(config["instagram"]).path.strip("/"))}',
    }
    if page == "index.html":
        by_id = {p["id"]: p for p in config["produtos"]}
        regions["hero"] = editorial_photo(config["fotoInicio"], config, hero=True)
        regions["vitrine"] = grid([by_id[key] for key in config["vitrine"]], config)
        photo = photo_or_placeholder(config.get("fotoInstagram"), config, "170px")
        regions["social"] = f'<div class="social-photo">{photo}</div>'
    elif page == "sobre.html":
        regions["sobre"] = editorial_photo(config["fotoSobre"], config)
        gallery = "".join(f'<figure>{image(config["fotos"][key], PRODUCT_SIZES)}</figure>' for key in config["galeria"])
        regions["galeria"] = f'<div class="gallery">{gallery}</div>'
    elif page == "catalogo.html":
        regions["catalogo"] = catalog(config)
        regions["filtros"] = filters(config)
        regions["pdf"] = (f'<a class="text-link pdf-link" href="{asset(config["pdf"])}" download>Baixar o catálogo em PDF</a>'
                          if config.get("pdf") else "")
    for name, content in regions.items():
        inline = name in {"usuario", "pagamento"}
        source = replace_region(source, name, content if inline else f"\n{content}\n")
    return re.sub(r'data-instagram href="[^"]*"', f'data-instagram href="{escape(config["instagram"])}"', source)


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id":
                if value in self.ids:
                    raise ValueError(f"Identificador HTML duplicado: {value}")
                self.ids.add(value)
            if key in ("href", "src"):
                self.references.append(value)
            if key == "srcset":
                self.references.extend(item.split()[0] for item in value.split(","))


def validate_pages(pages, directory):
    parsed = {}
    for name, source in pages.items():
        parser = PageLinks()
        parser.feed(source)
        parsed[name] = parser
    for name, parser in parsed.items():
        for rel in parser.references:
            url = urlsplit(rel)
            if url.scheme == "https" and url.netloc:
                continue
            if url.scheme or url.netloc or url.path.startswith("/") or not rel:
                raise ValueError(f"{name}: referência inválida ou incompatível com GitHub Pages: {rel}")
            pathname = unquote(url.path) or name
            target = directory / pathname
            if not target.is_file() or not target.resolve().is_relative_to(directory):
                raise ValueError(f"{name}: arquivo não encontrado: {rel}")
            if pathname in parsed and url.fragment and unquote(url.fragment) not in parsed[pathname].ids:
                raise ValueError(f"{name}: âncora não encontrada: {rel}")


def prepare_output(output, pages):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Use uma pasta de saída vazia para preparar o site.")
    for folder, extensions in PUBLIC_DIRS.items():
        source = ROOT / folder
        if source.is_symlink():
            raise ValueError(f"Diretório público é um link simbólico: {folder}")
        for original in sorted(source.rglob("*")):
            if original.is_symlink() or not original.resolve().is_relative_to(ROOT):
                raise ValueError(f"Link simbólico na mídia pública: {original.relative_to(ROOT)}")
            rel = original.relative_to(ROOT)
            if original.is_file() and original.suffix.lower() in extensions and not any(part.startswith(".") for part in rel.parts):
                target = output / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
    shutil.copy2(ROOT / ".nojekyll", output / ".nojekyll")
    for name, content in pages.items():
        (output / name).write_text(content, encoding="utf-8")
    validate_pages(pages, output)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    mode = cli.add_mutually_exclusive_group(required=True)
    mode.add_argument("--saida", type=Path, help="pasta vazia para o artefato público")
    mode.add_argument("--atualizar-html", action="store_true", help="atualiza as páginas para a prévia local")
    args = cli.parse_args()
    config = json.loads((ROOT / "catalogo.json").read_text(encoding="utf-8"))
    validate_config(config)
    pages = {name: render(name, config) for name, _ in PAGES}
    if args.saida:
        output = args.saida.resolve()
        if output.is_relative_to(ROOT):
            raise ValueError("Use uma pasta de saída fora de website/.")
        prepare_output(output, pages)
    else:
        validate_pages(pages, ROOT)
        for name, content in pages.items():
            (ROOT / name).write_text(content, encoding="utf-8")
    print(f"Site validado: {len(pages)} páginas, {len(config['produtos'])} produtos.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, DecimalException) as error:
        raise SystemExit(f"Falha ao preparar o site: {error}") from error
