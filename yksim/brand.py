"""Identidade visual da NoctaSecurity usada pelas interfaces do yksim (Qt e web).

Uma fonte só para a paleta, os arquivos da marca e o texto do "Sobre": a janela Qt importa daqui e a interface
web recebe os mesmos textos e imagens na hora de servir a página (web.py).

As cores vêm das chaves de segurança físicas: o corpo preto e o disco dourado onde se encosta o dedo.
"""

from __future__ import annotations

from pathlib import Path

ASSETS = Path(__file__).with_name("assets")
ICON_PNG = ASSETS / "icone.png"                      # yksim: anéis de toque no disco dourado (1024 -> 256 px)
SYMBOL_PNG = ASSETS / "simbolo.png"                  # o mesmo símbolo, sem fundo
SYMBOL_SVG = ASSETS / "simbolo.svg"
COMPANY_LOGO_PNG = ASSETS / "logo-noctasecurity.png"  # escudo com N + "noctasecurity"
COMPANY_LOGO_SVG = ASSETS / "logo-noctasecurity.svg"

# Paleta da marca
NIGHT = "#0B0B0F"       # fundo principal
GRAPHITE = "#15151C"    # painéis
SURFACE = "#1D1D25"     # campos, botões secundários
LINE = "#2A2A35"        # bordas
TEXT = "#F2F2F2"
MUTED = "#9A9AA5"
YELLOW = "#FFC300"      # destaque (amarelo Nocta)
YELLOW_HOVER = "#FFD13D"
YELLOW_DARK = "#D99E00"
RIM = "#7A5A00"         # aro do disco
DANGER = "#C62828"
DANGER_HOVER = "#D84040"

REPO_URL = "https://github.com/noctasecurity/yubikey"
COMPANY_URL = "https://github.com/noctasecurity"

ABOUT_TITLE = "Sobre o yksim e a NoctaSecurity"

ABOUT_YKSIM = (
    "O <b>yksim</b> é um simulador de YubiKey 5 NFC com o applet PIV, para desenvolver e testar sistemas que "
    "dependem de chave física sem precisar de uma chave para cada pessoa ou máquina. É código aberto e faz parte "
    "das ferramentas da NoctaSecurity."
)

ABOUT_COMPANY = [
    "A <b>NoctaSecurity</b> é uma empresa brasileira de segurança da informação. Começa atendendo clientes no "
    "Brasil e se prepara para atuar também fora dele.",
    "Acreditamos que nenhuma ação crítica deve acontecer sem uma pessoa presente para aprová-la. É a mesma ideia "
    "de uma chave de segurança física: ela só assina quando alguém encosta o dedo.",
    "Por isso as nossas cores são o preto e o amarelo dessas chaves, o corpo escuro e o disco dourado de toque. "
    "O símbolo de cada produto nosso é um desenho gravado nesse disco; o do yksim são os anéis do toque.",
]

ABOUT_NOTICE = (
    "YubiKey é marca registrada da Yubico AB. O yksim é um projeto independente, sem vínculo com a Yubico e sem "
    "endosso dela. Use só para desenvolvimento e testes: as chaves simuladas ficam em arquivos comuns no disco."
)


def about_html(link_color: str = YELLOW) -> str:
    """O texto do "Sobre" em HTML simples (serve para o QLabel do Qt e para a página web)."""
    a = f'style="color:{link_color}"'
    paras = [ABOUT_YKSIM, *ABOUT_COMPANY]
    body = "".join(f"<p>{p}</p>" for p in paras)
    links = (f'<p><a {a} href="{REPO_URL}">Código do yksim</a> · '
             f'<a {a} href="{COMPANY_URL}">NoctaSecurity no GitHub</a></p>')
    return body + links
