#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera assets/avatar-ascii.svg -> sua foto renderizando em ASCII, linha por linha.

Uso:
    python tools/gerar_avatar_svg.py                 # baixa a foto do GitHub
    python tools/gerar_avatar_svg.py minha_foto.jpg  # usa uma foto local

Requer: Pillow  ->  pip install pillow
"""

import io
import os
import sys
import urllib.request

from PIL import Image, ImageOps

USUARIO = "c-Murilo"
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SAIDA = os.path.join(RAIZ, "assets", "ascii-render.svg")

# ---- ajustes ---------------------------------------------------------------
COLS = 80                        # colunas de caractere
CROP = (0.10, 0.02, 0.86, 0.88)  # recorte da foto (esq, topo, dir, base) 0..1
RAMPA = " .:-=+*ox#%@"           # escuro -> claro
CICLO = 8.0                      # segundos do loop
DIGITACAO = 3.0                  # segundos ate terminar de "digitar"
FONTE = 11.0
RAZAO = 0.6                      # largura/altura do caractere monoespacado
BG = "#05070f"


def carregar(caminho=None):
    if caminho:
        return Image.open(caminho)
    url = f"https://avatars.githubusercontent.com/{USUARIO}?size=600"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return Image.open(io.BytesIO(r.read()))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def gerar(img):
    rows = max(1, round(COLS * RAZAO * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0])))
    im = ImageOps.exif_transpose(img).convert("L")
    w, h = im.size
    im = im.crop((round(CROP[0] * w), round(CROP[1] * h),
                  round(CROP[2] * w), round(CROP[3] * h)))
    im = ImageOps.autocontrast(im, cutoff=(0, 2))
    im = im.resize((COLS, rows), Image.LANCZOS)
    px = im.load()

    cw, lh = FONTE * RAZAO, FONTE
    mx, my = 24, 46
    W = round(COLS * cw + mx * 2)
    H = round(rows * lh + my + 42)

    # Nada de <mask>/<clipPath>: o proxy de imagens do GitHub remove esses
    # elementos e o conteudo some. A revelacao e feita por opacidade, em
    # blocos de BLOCO caracteres, com atraso crescente (efeito de digitacao).
    def cor_linha(k):
        pares = [(0.0,(0xa7,0x8b,0xfa)),(0.45,(0x22,0xd3,0xee)),(1.0,(0x7c,0x3a,0xed))]
        for i in range(len(pares)-1):
            a,ca = pares[i]; b,cb = pares[i+1]
            if a <= k <= b:
                f = 0 if b==a else (k-a)/(b-a)
                return "#%02x%02x%02x" % tuple(round(ca[j]+(cb[j]-ca[j])*f) for j in range(3))
        return "#22d3ee"

    BLOCO = 8
    LINHA_DUR = 0.5                          # tempo pra "digitar" uma linha
    n = len(RAMPA) - 1
    linhas = []
    for y in range(rows):
        txt = "".join(RAMPA[min(n, int(px[x, y] / 255 * n + 0.5))] for x in range(COLS))
        if not txt.strip():
            continue
        base = y / rows * DIGITACAO
        for c in range(0, COLS, BLOCO):
            pedaco = txt[c:c + BLOCO].rstrip()
            if not pedaco:
                continue
            atraso = round(base + (c / COLS) * LINHA_DUR, 2)
            linhas.append(
                f'<text x="{mx + c * cw:.1f}" y="{my + y * lh:.0f}" fill="{cor_linha(y/max(1,rows-1))}">{esc(pedaco)}'
                f'<animate attributeName="opacity" values="0;1;1;0" '
                f'keyTimes="0;0.035;0.93;1" dur="{CICLO}s" begin="{atraso}s" '
                f'repeatCount="indefinite"/></text>'
            )

    fim = DIGITACAO + LINHA_DUR

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" role="img" aria-label="Foto de {USUARIO} renderizada em ASCII">
<defs>
  <linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#7c3aed"/><stop offset="55%" stop-color="#22d3ee"/>
    <stop offset="100%" stop-color="#f472b6"/>
  </linearGradient>
  <linearGradient id="t" x1="0" y1="0" x2=".3" y2="1">
    <stop offset="0%" stop-color="#a78bfa"/><stop offset="45%" stop-color="#22d3ee"/>
    <stop offset="100%" stop-color="#7c3aed"/>
  </linearGradient>
  <linearGradient id="s" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#22d3ee" stop-opacity="0"/>
    <stop offset="80%" stop-color="#22d3ee" stop-opacity=".18"/>
    <stop offset="100%" stop-color="#e0fbff" stop-opacity=".55"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
<rect x=".8" y=".8" width="{W-1.6}" height="{H-1.6}" rx="13.5" fill="none" stroke="url(#b)" stroke-width="1.5" opacity=".8"/>
<circle cx="22" cy="22" r="4.5" fill="#f472b6"/><circle cx="38" cy="22" r="4.5" fill="#facc15"/><circle cx="54" cy="22" r="4.5" fill="#22d3ee"/>
<text x="72" y="26" fill="#64748b" font-family="monospace" font-size="11">murilo@github:~$ render --ascii avatar.png<tspan fill="#22d3ee">_<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.49;0.5;1" dur="1s" repeatCount="indefinite"/></tspan></text>
<line x1="8" y1="34" x2="{W-8}" y2="34" stroke="#1e293b"/>
<g font-family="monospace" font-size="{FONTE}">
{chr(10).join(linhas)}
</g>
<rect x="8" y="{my-16}" width="{W-16}" height="64" fill="url(#s)" opacity="0">
  <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.02;{fim/CICLO:.3f};{min(fim/CICLO+0.03,0.99):.3f};1" dur="{CICLO}s" repeatCount="indefinite"/>
  <animateTransform attributeName="transform" type="translate" values="0,-70;0,{H};0,{H}" keyTimes="0;{fim/CICLO:.3f};1" dur="{CICLO}s" repeatCount="indefinite"/>
</rect>
<text x="24" y="{H-30}" fill="#22d3ee" font-family="monospace" font-size="10" opacity=".8">{COLS} x {rows} chars</text>
<rect x="24" y="{H-22}" width="{W-48}" height="4" rx="2" fill="#111827"/>
<rect x="24" y="{H-22}" width="0" height="4" rx="2" fill="url(#b)">
  <animate attributeName="width" values="0;{W-48};{W-48}" keyTimes="0;{fim/CICLO:.3f};1" dur="{CICLO}s" repeatCount="indefinite"/>
</rect>
</svg>
'''


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else None
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(gerar(carregar(caminho)))
    print(f"OK -> {os.path.normpath(SAIDA)}  ({os.path.getsize(SAIDA)/1024:.1f} KB)")
