"""Gera docs/yksim-manual.pdf a partir de docs/MANUAL.md, com a identidade visual da NoctaSecurity.

    python3 docs/gerar_pdf.py            # precisa de: pip install markdown weasyprint
    python3 docs/gerar_pdf.py saida.pdf
"""
import datetime
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode
from weasyprint import HTML

docs = Path(__file__).resolve().parent
out = str(docs / "yksim-manual.pdf") if len(sys.argv) < 2 else sys.argv[1]
md = (docs / "MANUAL.md").read_text(encoding="utf-8")

# A capa já tem o logotipo e o título: tira os do topo do Markdown
md = re.sub(r"\A<p align=\"center\">.*?</p>\s*# [^\n]*\n", "", md, flags=re.S)
# <details> do GitHub: no papel, mostra o conteúdo aberto
md = md.replace("<details>\n<summary>", '<div class="details" markdown="1">\n<p class="summary">').replace(
    "</summary>", "</p>\n").replace("</details>", "</div>")
# fenced_code não funciona dentro de listas: vira bloco recuado (8 espaços = código dentro do item)
md = re.sub(r"^    ```[a-z]*\n(.*?)^    ```$",
            lambda m: "\n".join("        " + l[4:] for l in m.group(1).rstrip("\n").split("\n")),
            md, flags=re.M | re.S)
body = markdown.markdown(md, extensions=["tables", "fenced_code", "toc", "md_in_html", "sane_lists"],
                         extension_configs={"toc": {"slugify": slugify_unicode}}, output_format="html5")

# Paleta da NoctaSecurity (a mesma de yksim/brand.py). No papel o fundo é claro, para imprimir;
# o preto e o amarelo ficam na capa, nos títulos e nos destaques.
NIGHT, GRAPHITE, YELLOW, YELLOW_DARK, RIM, MUTED = "#0B0B0F", "#15151C", "#FFC300", "#D99E00", "#7A5A00", "#6B6B76"

CSS = f"""
@page {{ size: A4; margin: 18mm 16mm 20mm;
  @bottom-left {{ content: "yksim · manual de instalação e uso"; font: 8pt 'DejaVu Sans'; color: {MUTED}; }}
  @bottom-right {{ content: counter(page) " / " counter(pages); font: 8pt 'DejaVu Sans'; color: {MUTED}; }}
  @top-right {{ content: "noctasecurity"; font: bold 8pt 'DejaVu Sans'; color: {RIM}; }} }}
@page :first {{ margin: 0; background: {NIGHT};
  @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} @top-right {{ content: none; }} }}
.cover {{ break-after: page; height: 297mm; box-sizing: border-box; padding: 62mm 22mm 0; color: #F2F2F2;
          text-align: center; position: relative; }}
.cover .logo {{ width: 150mm; border: 0; margin: 0 auto; }}
.cover .rule {{ width: 40mm; height: 3pt; background: {YELLOW}; margin: 14mm auto 10mm; }}
.cover .ctitle {{ font-size: 26pt; font-weight: bold; margin: 0 0 6pt; color: #F2F2F2; border: 0; padding: 0; }}
.cover .csub {{ color: #9A9AA5; font-size: 11pt; margin: 0 10mm; line-height: 1.5; }}
.cover .foot {{ position: absolute; bottom: 22mm; left: 0; right: 0; }}
.cover .company {{ width: 62mm; border: 0; margin: 0 auto 4mm; }}
.cover .cdate {{ color: #9A9AA5; font-size: 9pt; }}
html {{ font: 10pt/1.55 'DejaVu Sans', sans-serif; color: #1f1f24; }}
h1 {{ font-size: 21pt; margin: 0 0 6pt; color: {NIGHT}; }}
h2 {{ font-size: 14.5pt; margin: 22pt 0 8pt; color: {NIGHT}; padding: 4pt 0 4pt 9pt;
      border-left: 4pt solid {YELLOW}; background: #FFF8DC; break-after: avoid; }}
h2 + * {{ break-before: avoid; }}
h3, p.summary {{ font-size: 11pt; font-weight: bold; break-after: avoid; color: {NIGHT}; }}
a {{ color: {RIM}; text-decoration: none; border-bottom: 1px solid {YELLOW}; }}
strong {{ color: {NIGHT}; }}
code {{ font: 8.6pt 'DejaVu Sans Mono', monospace; background: #F4F2EA; padding: 0 2pt; border-radius: 2pt; }}
pre {{ background: {GRAPHITE}; color: #E8E8EE; border-left: 3pt solid {YELLOW}; border-radius: 4pt;
       padding: 7pt 9pt; white-space: pre-wrap; word-break: break-all; break-inside: avoid; }}
pre code {{ background: none; padding: 0; font-size: 8.2pt; color: inherit; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.6pt; margin: 6pt 0; break-inside: auto; }}
th, td {{ border: 1px solid #DCDCE2; padding: 3.5pt 5pt; vertical-align: top; text-align: left; }}
th {{ background: {NIGHT}; color: {YELLOW}; border-color: {NIGHT}; }}
tr:nth-child(even) td {{ background: #FAFAF7; }}
tr {{ break-inside: avoid; }}
td code {{ font-size: 7.8pt; word-break: break-all; }}
img {{ max-width: 100%; display: block; margin: 8pt auto; border: 1px solid #DCDCE2; border-radius: 4pt;
       break-inside: avoid; }}
p:has(> img) {{ break-inside: avoid; }}
blockquote {{ margin: 8pt 0; padding: 5pt 10pt; border-left: 3pt solid {YELLOW}; background: #FFF8DC;
              color: #4A3A08; }}
hr {{ display: none; }}
.details {{ border: 1px dashed #CFCFD6; border-radius: 4pt; padding: 4pt 8pt; }}
ul, ol {{ padding-left: 16pt; }}
li::marker {{ color: {YELLOW_DARK}; }}
"""

cover = f"""<section class="cover">
<img class="logo" src="img/logo.png" alt="yksim por noctasecurity">
<div class="rule"></div>
<p class="ctitle">Manual de instalação e uso</p>
<p class="csub">YubiKey 5 NFC virtual com PIV<br>Debian 13 e Ubuntu 24.04 no WSL2 · dependências, instalação,
primeiro uso, tutoriais e solução de problemas</p>
<div class="foot">
<img class="company" src="../yksim/assets/logo-noctasecurity.png" alt="noctasecurity">
<p class="cdate">{datetime.date.today():%d/%m/%Y}</p>
</div>
</section>"""
html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>yksim — manual de instalação e uso</title>
<meta name="author" content="NoctaSecurity"><style>{CSS}</style></head><body>{cover}{body}</body></html>"""
HTML(string=html, base_url=str(docs) + "/").write_pdf(out)
print("ok", out)
