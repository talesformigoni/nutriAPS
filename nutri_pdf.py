import locale
import datetime
import re
import textwrap
import math
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle

# ── Paleta de cores (mesma do app) ─────────────────────────────────────────
AZUL_ESCURO  = colors.HexColor("#222222")
AZUL_MEDIO   = colors.HexColor("#555555")
AZUL_CLARO   = colors.HexColor("#F0F0F0")
CINZA_BORDA  = colors.HexColor("#CCCCCC")
CINZA_TEXTO  = colors.HexColor("#333333")
CINZA_ALT    = colors.HexColor("#EAEAEA")
BRANCO       = colors.white
VERDE        = colors.HexColor("#666666")
AMARELO      = colors.HexColor("#444444")
VERMELHO     = colors.HexColor("#222222")

W, H = A4   # 210 × 297 mm em pontos

# ── Helpers ─────────────────────────────────────────────────────────────────
def _limpar(texto):
    if not texto:
        return ""
    subs = {"—":"-","–":"-","\u201c":'"',"\u201d":'"',"'":"'","'":"'","…":"..."}
    for a, b in subs.items():
        texto = texto.replace(a, b)
    return str(texto)

def _limpar_md(texto):
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'\*(.*?)\*',     r'\1', texto)
    texto = re.sub(r'#{1,6}\s*',     '',    texto)
    texto = re.sub(r'[^\x00-\xFF]',  '',    texto)
    return texto.strip()

def _cor_risco(risco):
    return {"Baixo": VERDE, "Moderado": AMARELO, "Alto": VERMELHO}.get(risco, AZUL_MEDIO)

# ── Elementos visuais reutilizáveis ─────────────────────────────────────────
def _cabecalho_pagina(c, titulo_secao=""):
    """Faixa superior azul + linha decorativa."""
    c.setFillColor(AZUL_ESCURO)
    c.rect(0, H - 22*mm, W, 22*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(15*mm, H - 14*mm, "Mapa de Saúde Nutricional")
    if titulo_secao:
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#DDDDDD"))
        c.drawRightString(W - 15*mm, H - 14*mm, titulo_secao)
    # Faixa azul fina abaixo do cabeçalho
    c.setFillColor(AZUL_MEDIO)
    c.rect(0, H - 24*mm, W, 2*mm, fill=1, stroke=0)

def _rodape_pagina(c, nome_paciente, num_pagina):
    """Rodapé com nome do paciente e número de página."""
    c.setFillColor(CINZA_BORDA)
    c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(CINZA_TEXTO)
    c.setFont("Helvetica", 8)
    c.drawString(15*mm, 4*mm, f"Página {num_pagina}  |  Uso exclusivo de {_limpar(nome_paciente)}")
    c.drawRightString(W - 15*mm, 4*mm,
                      datetime.datetime.now().strftime("%d/%m/%Y"))

def _card(c, x, y, largura, altura, cor_fundo=None, cor_borda=None, raio=3*mm):
    """Retângulo arredondado simulado com rect simples."""
    if cor_fundo:
        c.setFillColor(cor_fundo)
        c.roundRect(x, y, largura, altura, raio, fill=1, stroke=0)
    if cor_borda:
        c.setStrokeColor(cor_borda)
        c.setLineWidth(0.5)
        c.roundRect(x, y, largura, altura, raio, fill=0, stroke=1)

def _tag_metrica(c, x, y, largura, label, valor, cor=AZUL_MEDIO):
    """Card de métrica com label embaixo e valor grande."""
    _card(c, x, y, largura, 18*mm, cor_fundo=AZUL_CLARO, cor_borda=CINZA_BORDA)
    c.setFillColor(cor)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(x + largura/2, y + 10*mm, str(valor))
    c.setFillColor(CINZA_TEXTO)
    c.setFont("Helvetica", 8)
    c.drawCentredString(x + largura/2, y + 4*mm, label)

def _titulo_secao(c, y, texto, cor=AZUL_MEDIO):
    """Faixa colorida com título branco."""
    c.setFillColor(cor)
    c.rect(15*mm, y - 2*mm, W - 30*mm, 8*mm, fill=1, stroke=0)
    # Acento lateral
    c.setFillColor(AZUL_ESCURO)
    c.rect(15*mm, y - 2*mm, 3*mm, 8*mm, fill=1, stroke=0)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(21*mm, y + 0.5*mm, texto.upper())
    return y - 12*mm   # retorna Y após o título

def _linha_info(c, y, label, valor, fundo=False):
    if fundo:
        c.setFillColor(CINZA_ALT)
        c.rect(15*mm, y - 1.5*mm, W - 30*mm, 7*mm, fill=1, stroke=0)
    c.setFillColor(AZUL_ESCURO)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(18*mm, y, _limpar(label))
    c.setFillColor(CINZA_TEXTO)
    c.setFont("Helvetica", 9)
    c.drawString(65*mm, y, _limpar(str(valor)))
    return y - 7*mm

# ═══════════════════════════════════════════════════════════════════════════
# PDF PRINCIPAL DO PACIENTE
# ═══════════════════════════════════════════════════════════════════════════
def gerar_pdf_paciente(nome, idade, sexo, peso, altura, imc, classif_imc,
                       tmb, get, formula_nome, risco, explicacao, respostas_hab):

    # Verifica de forma segura se é gestante acessando o session_state do app
    import streamlit as st
    is_gestante = False
    if "dados_paciente" in st.session_state and st.session_state["dados_paciente"].get("is_gestante"):
        is_gestante = True
        dados_g = st.session_state["dados_paciente"]

    meses = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", 
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = datetime.datetime.now()
    data_formatada = f"Gerado em {hoje.day:02d} de {meses[hoje.month]} de {hoje.year}"

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ─── PÁGINA 1 — Capa + Identificação ─────────────────────────────────
    c.setFillColor(AZUL_ESCURO)
    c.rect(0, H - 75*mm, W, 75*mm, fill=1, stroke=0)
    c.setFillColor(AZUL_MEDIO)
    c.rect(0, H - 78*mm, W, 4*mm, fill=1, stroke=0)

    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(15*mm, H - 30*mm, "Mapa de Saúde Nutricional")

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#DDDDDD"))
    c.drawString(15*mm, H - 40*mm, "Prefeitura de Buritis-RO | Secretaria Municipal de Saúde")
    if is_gestante:
        c.drawString(15*mm, H - 45*mm, "Atenção Primária à Saúde | Linha de Cuidado da Gestante")
    else:
        c.drawString(15*mm, H - 45*mm, "Atenção Primária à Saúde | Departamento de Nutrição")

    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(15*mm, H - 55*mm, _limpar(nome))
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#CCCCCC"))
    c.drawString(15*mm, H - 63*mm, data_formatada)

    larg_card = 50*mm
    if is_gestante:
        # Troca os cards do topo para dados obstétricos
        _tag_metrica(c, 15*mm,   H - 99*mm, larg_card, "Idade Gestacional", f"{dados_g['semana']} Semanas")
        _tag_metrica(c, 70*mm,   H - 99*mm, larg_card, "Ganho de Peso (GPG)", f"{dados_g['res_gest']['gpg']:.1f} kg")
        _tag_metrica(c, 125*mm,  H - 99*mm, larg_card, "IMC Pré-Gest.", f"{dados_g['res_gest']['imc_pre']:.1f}")
        
        _card(c, 125*mm, H - 108*mm, larg_card, 7*mm, cor_fundo=VERDE)
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(125*mm + larg_card/2, H - 105*mm, _limpar(dados_g['res_gest']['classificacao_pre']))
    else:
        # Mantém o fluxo normal para população geral
        _tag_metrica(c, 15*mm,   H - 99*mm, larg_card, "Metabolismo Basal", f"{tmb:.0f} kcal")
        _tag_metrica(c, 70*mm,   H - 99*mm, larg_card, "Gasto Diário Total", f"{get:.0f} kcal")
        _tag_metrica(c, 125*mm,  H - 99*mm, larg_card, "IMC", f"{imc:.1f}",
                     cor=_cor_risco("Baixo") if imc < 25 else _cor_risco("Moderado") if imc < 30 else _cor_risco("Alto"))
        cor_imc = (_cor_risco("Baixo") if imc < 25 else _cor_risco("Moderado") if imc < 30 else _cor_risco("Alto"))
        _card(c, 125*mm, H - 108*mm, larg_card, 7*mm, cor_fundo=cor_imc)
        c.setFillColor(BRANCO)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(125*mm + larg_card/2, H - 105*mm, _limpar(classif_imc))

    # ── Seção Identificação ──
    y = H - 118*mm
    y = _titulo_secao(c, y, "1. IDENTIFICAÇÃO do Paciente")
    y = _linha_info(c, y, "Nome:", nome, fundo=True)
    y = _linha_info(c, y, "Data:", datetime.datetime.now().strftime("%d/%m/%Y"), fundo=False)
    y = _linha_info(c, y, "Idade:", f"{idade} anos", fundo=True)
    
    if is_gestante:
            y = _linha_info(c, y, "Idade Gestacional:", f"{dados_g['semana']} semanas", fundo=False)
            y = _linha_info(c, y, "Peso Atual:", f"{dados_g['peso']:.1f} kg", fundo=True)
            y = _linha_info(c, y, "IMC Atual:", f"{dados_g['res_gest']['imc_atual']:.1f} kg/m2", fundo=False)
            y = _linha_info(c, y, "Classificação (Atalah):", f"{dados_g['res_gest']['classificacao_atual']}", fundo=True)
            y -= 8*mm
            
            y = _titulo_secao(c, y, "2. Diretrizes do Pré-Natal", cor=AZUL_MEDIO)
            y -= 2*mm
            c.setFont("Helvetica", 9)
            c.setFillColor(CINZA_TEXTO)
            linhas_g = [
                f"Diagnóstico de Atalah (1997): {dados_g['res_gest']['classificacao_atual']}",
                f"Ganho de peso total recomendado: {dados_g['res_gest']['ganho_min']} a {dados_g['res_gest']['ganho_max']} kg",
                "",
                "O acompanhamento do IMC semana a semana visa prevenir intercorrências",
                "garantindo o crescimento intrauterino ideal do feto e a saúde materna."
            ]
            for linha in linhas_g:
                c.drawString(18*mm, y, linha)
                y -= 6*mm
    else:
        y = _linha_info(c, y, "Sexo:", sexo, fundo=False)
        y = _linha_info(c, y, "Peso:", f"{peso} kg", fundo=True)
        y = _linha_info(c, y, "Altura:", f"{altura} cm", fundo=False)
        y = _linha_info(c, y, "IMC:", f"{imc:.1f} kg/m2  —  {_limpar(classif_imc)}", fundo=True)
        y -= 8*mm

        y = _titulo_secao(c, y, "2. Seus Gastos de Energia", cor=AZUL_MEDIO)
        y -= 2*mm
        c.setFont("Helvetica", 9)
        c.setFillColor(CINZA_TEXTO)
        linhas_energia = [
            f"Fórmula utilizada: {_limpar(formula_nome)}",
            f"Metabolismo basal (repouso total): {tmb:.0f} kcal/dia",
            f"Gasto energético total (com sua rotina): {get:.0f} kcal/dia",
            "",
            "Este é o valor que seu corpo precisa para manter o peso atual.",
            "Comer acima desse valor tende ao ganho de peso; abaixo, à perda gradual.",
        ]
        for linha in linhas_energia:
            c.drawString(18*mm, y, linha)
            y -= 6*mm
    hoje = datetime.datetime.now()
    data_formatada = f"Gerado em {hoje.day:02d} de {meses[hoje.month]} de {hoje.year}"

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # ─── PÁGINA 1 — Capa + Identificação ─────────────────────────────────
    # Hero azul escuro no topo
    c.setFillColor(AZUL_ESCURO)
    c.rect(0, H - 75*mm, W, 75*mm, fill=1, stroke=0)

    # Faixa azul médio como detalhe
    c.setFillColor(AZUL_MEDIO)
    c.rect(0, H - 78*mm, W, 4*mm, fill=1, stroke=0)

    # Título principal
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(15*mm, H - 30*mm, "Mapa de Saúde Nutricional")

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#DDDDDD"))
    c.drawString(15*mm, H - 40*mm, "Prefeitura de Buritis-RO | Secretaria Municipal de Saúde")
    c.drawString(15*mm, H - 45*mm, "Atenção Primária à Saúde | Departamento de Nutrição")

    # Nome do paciente em destaque
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(15*mm, H - 55*mm, _limpar(nome))
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#CCCCCC"))
    c.drawString(15*mm, H - 63*mm, data_formatada)

    # Cards de métricas no hero
    larg_card = 50*mm
    _tag_metrica(c, 15*mm,   H - 99*mm, larg_card, "Metabolismo Basal", f"{tmb:.0f} kcal")
    _tag_metrica(c, 70*mm,   H - 99*mm, larg_card, "Gasto Diário Total", f"{get:.0f} kcal")
    _tag_metrica(c, 125*mm,  H - 99*mm, larg_card, "IMC",
                 f"{imc:.1f}",
                 cor=_cor_risco("Baixo") if imc < 25 else
                     _cor_risco("Moderado") if imc < 30 else _cor_risco("Alto"))

    # Classificação IMC badge
    cor_imc = (_cor_risco("Baixo") if imc < 25 else
               _cor_risco("Moderado") if imc < 30 else _cor_risco("Alto"))
    _card(c, 125*mm, H - 108*mm, larg_card, 7*mm, cor_fundo=cor_imc)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(125*mm + larg_card/2, H - 105*mm, _limpar(classif_imc))

    # ── Seção Identificação ──
    y = H - 118*mm
    y = _titulo_secao(c, y, "1. IDENTIFICAÇÃO do Paciente")
    y = _linha_info(c, y, "Nome:", nome, fundo=True)
    y = _linha_info(c, y, "Data:", datetime.datetime.now().strftime("%d/%m/%Y"), fundo=False)
    y = _linha_info(c, y, "Idade:", f"{idade} anos", fundo=True)
    y = _linha_info(c, y, "Sexo:", sexo, fundo=False)
    y = _linha_info(c, y, "Peso:", f"{peso} kg", fundo=True)
    y = _linha_info(c, y, "Altura:", f"{altura} cm", fundo=False)
    y = _linha_info(c, y, "IMC:", f"{imc:.1f} kg/m2  —  {_limpar(classif_imc)}", fundo=True)
    y -= 8*mm

    # ── Seção Energia ──
    y = _titulo_secao(c, y, "2. Seus Gastos de Energia", cor=AZUL_MEDIO)
    y -= 2*mm
    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_TEXTO)
    linhas_energia = [
        f"Fórmula utilizada: {_limpar(formula_nome)}",
        f"Metabolismo basal (repouso total): {tmb:.0f} kcal/dia",
        f"Gasto energético total (com sua rotina): {get:.0f} kcal/dia",
        "",
        "Este é o valor que seu corpo precisa para manter o peso atual.",
        "Comer acima desse valor tende ao ganho de peso; abaixo, à perda gradual.",
    ]
    for linha in linhas_energia:
        c.drawString(18*mm, y, linha)
        y -= 6*mm

    _rodape_pagina(c, nome, 1)
    c.showPage()

    # ─── PÁGINA 2 — Avaliação de Hábitos ────────────────────────────────
    _cabecalho_pagina(c, "Avaliação de Hábitos")
    cor_r = _cor_risco(risco)

    y = H - 32*mm
    y = _titulo_secao(c, y, "3. Avaliação dos Seus Hábitos", cor=cor_r)

    # Badge de risco
    y -= 2*mm
    _card(c, 15*mm, y - 4*mm, W - 30*mm, 12*mm, cor_fundo=cor_r)
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W/2, y + 2*mm, f"Risco de Qualidade Alimentar: {risco}")
    y -= 18*mm

    # Texto de explicação
    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_TEXTO)
    linhas_exp = textwrap.wrap(_limpar(explicacao), width=95)
    for l in linhas_exp:
        c.drawString(18*mm, y, l)
        y -= 5.5*mm
    y -= 5*mm

    # Tabela de respostas
    y = _titulo_secao(c, y, "Resumo das Respostas (Protocolo PRAR)", cor=AZUL_ESCURO)
    y -= 2*mm

    for i, (pergunta, resposta) in enumerate(respostas_hab):
        if resposta is None:
            continue
        resp_limpa = str(resposta).split(" (")[0]
        fundo = CINZA_ALT if i % 2 == 0 else BRANCO
        _card(c, 15*mm, y - 2*mm, W - 30*mm, 7.5*mm, cor_fundo=fundo, cor_borda=CINZA_BORDA)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(AZUL_ESCURO)
        perg_curta = _limpar(pergunta)[:60]
        c.drawString(18*mm, y + 1*mm, perg_curta)

        c.setFont("Helvetica", 8)
        c.setFillColor(CINZA_TEXTO)
        c.drawRightString(W - 18*mm, y + 1*mm, _limpar(resp_limpa))
        y -= 8*mm

        if y < 20*mm:
            _rodape_pagina(c, nome, 2)
            c.showPage()
            _cabecalho_pagina(c, "Avaliação de Hábitos (cont.)")
            y = H - 35*mm

    _rodape_pagina(c, nome, 2)
    c.showPage()

    # ─── PÁGINA 3 — Tabela de Alimentos ─────────────────────────────────
    _cabecalho_pagina(c, "Exemplos de Alimentos")
    y = H - 32*mm
    y = _titulo_secao(c, y, "4. Exemplos de Alimentos e Porções", cor=AZUL_MEDIO)

    y -= 2*mm
    c.setFont("Helvetica", 8)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(15*mm, y,
        "Valores médios baseados na TACO. Servem para educação nutricional, "
        "não substituem orientação individual.")
    y -= 8*mm

    alimentos = [
        ["Alimento", "Medida caseira", "kcal", "Grupo"],
        ["Arroz branco cozido",          "1 concha média (100 g)",    "130", "Base"],
        ["Feijão carioca cozido",        "1 concha média (100 g)",    "80",  "Base"],
        ["Macarrão cozido",              "1 escumadeira (100 g)",     "140", "Base"],
        ["Pão francês",                  "1 unidade média (50 g)",    "135", "Base"],
        ["Batata doce cozida",           "1 pedaço médio (60 g)",     "50",  "Base"],
        ["Frango cozido/assado s/ pele", "1 filé pequeno (60 g)",     "100", "Proteína"],
        ["Ovo de galinha inteiro",       "1 unidade média (50 g)",    "75",  "Proteína"],
        ["Carne bovina magra cozida",    "1 bife pequeno (60 g)",     "130", "Proteína"],
        ["Leite integral",               "1 copo (200 ml)",           "120", "Lácteo"],
        ["Iogurte natural integral",     "1 pote (170 g)",            "110", "Lácteo"],
        ["Queijo muçarela",              "1 fatia média (30 g)",      "90",  "Lácteo"],
        ["Banana prata",                 "1 unidade média (80 g)",    "70",  "Fruta"],
        ["Maçã",                         "1 unidade média (90 g)",    "50",  "Fruta"],
        ["Laranja-pera",                 "1 unidade média (130 g)",   "60",  "Fruta"],
        ["Óleo vegetal (soja)",          "1 col. sopa (8 g)",         "70",  "Gordura"],
        ["Refrigerante comum",           "1 copo (200 ml)",           "80",  "Açúcar"],
        ["Biscoito recheado",            "3 unidades (30 g)",         "145", "Açúcar"],
        ["Bolo simples caseiro",         "1 fatia média (60 g)",      "180", "Açúcar"],
        ["Achocolatado com leite",       "1 copo (200 ml)",           "160", "Açúcar"],
    ]

    col_w = [65*mm, 65*mm, 20*mm, 25*mm]
    style = TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  AZUL_ESCURO),
        ("TEXTCOLOR",    (0,0), (-1,0),  colors.white),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  8),
        ("ALIGN",        (2,0), (2,-1),  "CENTER"),
        ("ALIGN",        (3,0), (3,-1),  "CENTER"),
        ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",     (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [BRANCO, CINZA_ALT]),
        ("GRID",         (0,0), (-1,-1), 0.3, CINZA_BORDA),
        ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ])
    t = Table(alimentos, colWidths=col_w)
    t.setStyle(style)
    tw, th = t.wrapOn(c, W - 30*mm, H)
    t.drawOn(c, 15*mm, y - th)

    _rodape_pagina(c, nome, 3)
    c.showPage()

    # ─── PÁGINA 4 — Metas ────────────────────────────────────────────────
    _cabecalho_pagina(c, "Metas da Consulta")
    y = H - 32*mm
    y = _titulo_secao(c, y, "5. Metas Combinadas na Consulta", cor=VERDE)

    y -= 3*mm
    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(15*mm, y, "Preencha junto com o nutricionista durante a consulta:")
    y -= 10*mm

    metas_dados = [
        ["Semana", "O que vamos mudar?", "Como fazer na prática", "Prazo"],
        ["1", "", "", ""],
        ["2", "", "", ""],
        ["3", "", "", ""],
        ["4", "", "", ""],
    ]
    metas_cols = [18*mm, 65*mm, 65*mm, 27*mm]
    metas_style = TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  VERDE),
        ("TEXTCOLOR",    (0,0), (-1,0),  BRANCO),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  9),
        ("ALIGN",        (0,0), (0,-1),  "CENTER"),
        ("FONTNAME",     (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",     (0,1), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [BRANCO, CINZA_ALT]),
        ("GRID",         (0,0), (-1,-1), 0.4, CINZA_BORDA),
        ("MINROWHEIGHT", (0,1), (-1,-1), 18*mm),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("LEFTPADDING",  (0,0), (-1,-1), 5),
    ])
    tm = Table(metas_dados, colWidths=metas_cols)
    tm.setStyle(metas_style)
    tmw, tmh = tm.wrapOn(c, W - 30*mm, H)
    tm.drawOn(c, 15*mm, y - tmh)

    # Mensagem final
    y_msg = y - tmh - 15*mm
    _card(c, 15*mm, y_msg - 8*mm, W - 30*mm, 14*mm,
          cor_fundo=AZUL_CLARO, cor_borda=CINZA_BORDA)
    c.setFillColor(AZUL_MEDIO)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W/2, y_msg - 2*mm,
                        "Pequenos passos geram grandes resultados. Confie em você!")

    _rodape_pagina(c, nome, 4)
    c.save()

    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# PDF DO CARDÁPIO GERADO PELA IA
# ═══════════════════════════════════════════════════════════════════════════
# ── PÁGINA 2: GRÁFICO OFICIAL MS 2026 (GRAYSCALE PARA PDF) ──
    _cabecalho_pagina_mono(c, "Acompanhamento do Ganho de Peso")
    dados_ms = res['dados_ms']
    perc = dados_ms['percentis']
    
    y_graf = H - 35*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRETO_TITULO)
    c.drawCentredString(W/2, y_graf, "GRÁFICO DE ACOMPANHAMENTO DO GANHO DE PESO")
    y_graf -= 6*mm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CINZA_ESCURO)
    c.drawCentredString(W/2, y_graf, f"{res['classificacao_pre'].upper()} ({dados_ms['limite_imc']})")
    y_graf -= 5*mm
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W/2, y_graf, f"GANHO DE PESO RECOMENDADO ATÉ 40 SEMANAS DE GESTAÇÃO: {dados_ms['rec_ganho']}")
    y_graf -= 8*mm
    
    graf_x, graf_y = 20*mm, y_graf - 110*mm
    graf_w, graf_h = 165*mm, 105*mm
    
    SEM_MIN, SEM_MAX = 10, 40
    Y_MIN, Y_MAX = -10, 25 

    def coord(sem, ganho):
        x = graf_x + ((sem - SEM_MIN) / (SEM_MAX - SEM_MIN)) * graf_w
        g_clamped = max(Y_MIN, min(ganho, Y_MAX))
        y = graf_y + ((g_clamped - Y_MIN) / (Y_MAX - Y_MIN)) * graf_h
        return x, y

    # Fundo Branco e Grade Fina (1 em 1 kg)
    c.setFillColor(BRANCO)
    c.rect(graf_x, graf_y, graf_w, graf_h, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#EAEAEA"))
    c.setLineWidth(0.3)
    
    c.setFont("Helvetica", 6)
    c.setFillColor(CINZA_ESCURO)
    for sem in range(SEM_MIN, SEM_MAX + 1):
        x, _ = coord(sem, Y_MIN)
        c.line(x, graf_y, x, graf_y + graf_h)
        c.drawCentredString(x, graf_y - 3*mm, str(sem))
        
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(graf_x + graf_w/2, graf_y - 10*mm, "← SEMANA DE GESTAÇÃO →")

    c.setFont("Helvetica", 6)
    for val_y in range(Y_MIN, Y_MAX + 1):
        _, y = coord(SEM_MIN, val_y)
        c.line(graf_x, y, graf_x + graf_w, y)
        c.drawRightString(graf_x - 1.5*mm, y - 1*mm, str(val_y))
    
    c.saveState()
    c.rotate(90)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(graf_y + graf_h/2, -(graf_x - 6*mm), "← GANHO DE PESO GESTACIONAL (kg) →")
    c.restoreState()

    # Marcações e Textos dos 3 Trimestres
    c.setStrokeColor(CINZA_MEDIO); c.setLineWidth(1.5)
    c.line(coord(13, Y_MIN)[0], graf_y, coord(13, Y_MIN)[0], graf_y + graf_h)
    c.line(coord(27, Y_MIN)[0], graf_y, coord(27, Y_MIN)[0], graf_y + graf_h)
    
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(coord(11.5, Y_MIN)[0], graf_y - 6*mm, "1º Trimestre")
    c.drawCentredString(coord(20, Y_MIN)[0], graf_y - 6*mm, "2º Trimestre")
    c.drawCentredString(coord(33.5, Y_MIN)[0], graf_y - 6*mm, "3º Trimestre")

    # === DESENHO DAS ZONAS EM ESCALA DE CINZA ===
    C_FILL = colors.HexColor("#F0F0F0") # Sombreamento da zona recomendada
    C_SAFE = colors.HexColor("#444444") # Linhas da zona de adequação (Sólidas)
    C_OUT = colors.HexColor("#888888")  # Linhas fora da zona (Tracejadas)
    
    x_vals = list(range(10, 41))
    keys_sorted = sorted(perc.keys(), key=lambda k: float(k.replace('P','')))
    
    # 1. Desenhar Área Sombreada (Fill)
    y_bottom = perc[dados_ms["safe_min_key"]]
    y_top = perc[dados_ms["safe_max_key"]]
    c.setFillColor(C_FILL)
    p = c.beginPath()
    p.moveTo(*coord(x_vals[0], y_bottom[0]))
    for i in range(1, len(x_vals)): p.lineTo(*coord(x_vals[i], y_bottom[i]))
    for i in range(len(x_vals)-1, -1, -1): p.lineTo(*coord(x_vals[i], y_top[i]))
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # 2. Desenhar as Linhas (Tracejadas vs Sólidas)
    for k in keys_sorted:
        is_safe = (k == dados_ms["safe_min_key"] or k == dados_ms["safe_max_key"])
        c.setStrokeColor(C_SAFE if is_safe else C_OUT)
        c.setLineWidth(1.5 if is_safe else 1.0)
        
        if not is_safe: c.setDash(3, 2)
        else: c.setDash()
        
        y_vals = perc[k]
        for i in range(len(x_vals)-1):
            c.line(*coord(x_vals[i], y_vals[i]), *coord(x_vals[i+1], y_vals[i+1]))
        
        # Bolinhas brancas e Rótulos dos Percentis
        c.setFillColor(BRANCO)
        c.circle(coord(40, y_vals[-1])[0] + 3*mm, coord(40, y_vals[-1])[1], 2.5*mm, fill=1, stroke=1)
        c.setFillColor(C_SAFE if is_safe else C_OUT)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(coord(40, y_vals[-1])[0] + 3*mm, coord(40, y_vals[-1])[1] - 1*mm, k)

    # 3. Ponto da Paciente
    x_pac, y_pac = coord(dados['semana'], res['ganho_atual'])
    c.setStrokeColor(PRETO_TITULO)
    c.setLineWidth(0.5); c.setDash(2,2)
    c.line(graf_x, y_pac, x_pac, y_pac); c.line(x_pac, graf_y, x_pac, y_pac) 
    c.setDash(); c.setFillColor(PRETO_TITULO)
    c.circle(x_pac, y_pac, 2*mm, fill=1, stroke=1)
    
    # 4. Fonte
    c.setFillColor(CINZA_ESCURO)
    c.setFont("Helvetica", 5.5)
    c.drawString(graf_x, graf_y - 15*mm, "Fonte: KAC, G. et al. Gestational weight gain charts: results from the Brazilian Maternal and Child Nutrition Consortium. Am. J. Clin. Nutr., v. 113, n. 5, p. 1351-1360, 2021. DOI: https://doi.org/10.1093/ajcn/nqaa402")

    # ── TABELA DINÂMICA COM ANTI-OVERLAP ──
    y_tab = graf_y - 20*mm
    tab_data = [
        ["Marcos Gestacionais", "Meta Mínima", "Meta Máxima"],
        [f"Até 13 semanas (1º Trimestre)", f"{perc[dados_ms['safe_min_key']][3]:+.1f} kg", f"{perc[dados_ms['safe_max_key']][3]:+.1f} kg"],
        [f"Até 27 semanas (2º Trimestre)", f"{perc[dados_ms['safe_min_key']][17]:+.1f} kg", f"{perc[dados_ms['safe_max_key']][17]:+.1f} kg"],
        [f"Até 40 semanas (3º Trimestre)", f"{perc[dados_ms['safe_min_key']][-1]:+.1f} kg", f"{perc[dados_ms['safe_max_key']][-1]:+.1f} kg"]
    ]
    tab = Table(tab_data, colWidths=[75*mm, 45*mm, 45*mm])
    tab.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), CINZA_ESCURO), ("TEXTCOLOR", (0,0), (-1,0), BRANCO),
        ("ALIGN", (0,0), (-1,-1), "CENTER"), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), 
        ("FONTSIZE", (0,0), (-1,-1), 8), ("GRID", (0,0), (-1,-1), 0.5, CINZA_CLARO),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [BRANCO, CINZA_FUNDO]),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)
    ]))
    
    # O ReportLab avalia a altura da tabela e joga os Desafios exatamente pra baixo dela
    w_tab, h_tab = tab.wrapOn(c, W, H)
    tab.drawOn(c, 22.5*mm, y_tab - h_tab)

    # ── ESPAÇO DE DESAFIOS ──
    y_desafios = y_tab - h_tab - 10*mm
    y_desafios = _titulo_secao_mono(c, y_desafios, "5. MEUS DESAFIOS E DIFICULDADES (Espaço da Paciente)")
    y_desafios -= 4*mm
    
    c.setFont("Helvetica-BoldOblique", 9); c.setFillColor(PRETO_TEXTO)
    c.drawString(15*mm, y_desafios, "O que foi mais difícil de seguir na dieta ou nos conselhos que combinamos?")
    
    y_desafios -= 5*mm
    c.setFont("Helvetica", 8.5); c.setFillColor(CINZA_ESCURO)
    c.drawString(15*mm, y_desafios, "Anote abaixo suas dúvidas e barreiras. Leve este papel na próxima consulta.")

    y_linhas = y_desafios - 12*mm
    c.setStrokeColor(CINZA_MEDIO); c.setLineWidth(0.5); c.setDash(1, 2)
    for _ in range(5): 
        c.line(15*mm, y_linhas, 195*mm, y_linhas)
        y_linhas -= 9*mm
    c.setDash()

    _rodape_pagina_mono(c, dados_g['nome'], 2)
    c.showPage()
    c.save()
    return buf.getvalue()

# ─── FUNÇÕES AUXILIARES MONOCROMÁTICAS (PRINT-FRIENDLY) ───

def _tag_metrica_mono(c, x, y, larg, label, valor):
    """Desenha um card de métrica profissional em tons de cinza."""
    # Cores
    PRETO_TITULO = colors.HexColor("#000000")
    CINZA_ESCURO = colors.HexColor("#555555")
    CINZA_BORDA = colors.HexColor("#DDDDDD")
    BRANCO = colors.white
    
    # Fundo e Borda
    c.setFillColor(BRANCO)
    c.setStrokeColor(CINZA_BORDA)
    c.setLineWidth(0.5)
    c.roundRect(x, y, larg, 18*mm, 2*mm, fill=1, stroke=1)
    
    # Label (Título do Card)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(CINZA_ESCURO)
    c.drawString(x + 3*mm, y + 13*mm, label.upper())
    
    # Valor Principal
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(PRETO_TITULO)
    c.drawCentredString(x + larg/2, y + 5*mm, valor)

def _titulo_secao_mono(c, y, titulo):
    """Desenha um título de seção padronizado em preto."""
    PRETO_TITULO = colors.HexColor("#000000")
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(PRETO_TITULO)
    c.drawString(15*mm, y, titulo.upper())
    
    # Linha divisória fina
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.3)
    c.line(15*mm, y - 2*mm, 195*mm, y - 2*mm)
    return y - 7*mm

def _linha_info_mono(c, y, label, valor, fundo=False, cor_valor=None):
    """Desenha uma linha de informação alternando fundo cinza claro."""
    # Cores
    PRETO_TEXTO = colors.HexColor("#222222")
    CINZA_FUNDO = colors.HexColor("#EEEEEE")
    CINZA_TEXTO = colors.HexColor("#555555")
    BRANCO = colors.white
    
    alt_linha = 6*mm
    if fundo:
        c.setFillColor(CINZA_FUNDO)
        c.rect(15*mm, y - 1*mm, 180*mm, alt_linha, fill=1, stroke=0)
    
    # Label
    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_TEXTO)
    c.drawString(18*mm, y + 1*mm, label)
    
    # Valor
    c.setFont("Helvetica-Bold", 9)
    # Se uma cor específica de valor for passada (ex: Preto Titulo para Obesidade), usa ela.
    if cor_valor:
        c.setFillColor(cor_valor)
    else:
        c.setFillColor(PRETO_TEXTO)
    c.drawRightString(192*mm, y + 1*mm, str(valor))
    return y - alt_linha

def _card_mono(c, x, y, larg, alt, cor_fundo=colors.white, cor_borda=colors.HexColor("#DDDDDD")):
    """Desenha um card arredondado genérico em tons de cinza."""
    c.setFillColor(cor_fundo)
    c.setStrokeColor(cor_borda)
    c.setLineWidth(0.5)
    c.roundRect(x, y, larg, alt, 1*mm, fill=1, stroke=1)

def _cabecalho_pagina_mono(c, titulo_pagina):
    """Desenha o cabeçalho padronizado nas páginas subsequentes (Preto)."""
    W, H = A4
    PRETO_TITULO = colors.HexColor("#000000")
    CINZA_ESCURO = colors.HexColor("#555555")
    CINZA_FUNDO = colors.HexColor("#EEEEEE")
    
    # Faixa superior
    c.setFillColor(CINZA_FUNDO)
    c.rect(0, H - 20*mm, W, 20*mm, fill=1, stroke=0)
    
    # Logo / Identificação (Texto simulando logo para print-friendly)
    c.setFillColor(PRETO_TITULO)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(15*mm, H - 10*mm, "Buritis-RO | Saúde Nutricional")
    
    # Título da Página
    c.setFillColor(CINZA_ESCURO)
    c.setFont("Helvetica", 10)
    c.drawRightString(195*mm, H - 10*mm, titulo_pagina)

def _rodape_pagina_mono(c, nome_paciente, num_pagina):
    """Desenha o rodapé monocromático padronizado."""
    W, _ = A4
    CINZA_ESCURO = colors.HexColor("#AAAAAA")
    CINZA_CLARO = colors.HexColor("#DDDDDD")
    
    # Linha divisória
    c.setStrokeColor(CINZA_CLARO)
    c.setLineWidth(0.3)
    c.line(15*mm, 15*mm, 195*mm, 15*mm)
    
    # Textos do rodapé
    c.setFont("Helvetica", 7)
    c.setFillColor(CINZA_ESCURO)
    c.drawString(15*mm, 11*mm, f"Paciente: {_limpar(nome_paciente)}")
    c.drawCentredString(W/2, 11*mm, "Gerado pelo Sistema NutriAPS | Buritis-RO")
    c.drawRightString(195*mm, 11*mm, f"Página {num_pagina}")

def _limpar(texto):
    """Remove caracteres especiais que quebram o ReportLab."""
    if not texto: return ""
    import unicodedata
    # Normaliza e remove acentos
    texto_limpo = unicodedata.normalize('NFKD', str(texto)).encode('ASCII', 'ignore').decode('ASCII')
    # Mantém apenas caracteres básicos e pontuação simples
    caracteres_validos = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,()-_:\"'%/*+=_-"
    return "".join(c for c in texto_limpo if c in caracteres_validos)

def gerar_pdf_cardapio_ia(dados_paciente, texto_cardapio):
    """
    Gera o PDF do Cardápio no estilo "Cards de Refeição" (Padrão Dietbox),
    otimizado para impressão em Preto e Branco / Tons de Cinza.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from io import BytesIO
    import datetime
    import re

    buf = BytesIO()
    
    # Configuração do documento (Margens confortáveis)
    doc = SimpleDocTemplate(
        buf, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, 
        topMargin=15*mm, bottomMargin=15*mm
    )

    elementos = []
    
    # --- ESTILOS DE TEXTO ---
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'Titulo', fontName='Helvetica-Bold', fontSize=14, 
        textColor=colors.HexColor("#000000"), alignment=1, spaceAfter=4
    )
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo', fontName='Helvetica', fontSize=10, 
        textColor=colors.HexColor("#555555"), alignment=1, spaceAfter=2
    )
    estilo_data = ParagraphStyle(
        'Data', fontName='Helvetica', fontSize=9, 
        textColor=colors.HexColor("#777777"), alignment=1, spaceAfter=10
    )
    
    # Estilos de dentro do Card
    estilo_card_header = ParagraphStyle(
        'CardHeader', fontName='Helvetica-Bold', fontSize=11, 
        textColor=colors.white, textTransform='uppercase'
    )
    estilo_card_body = ParagraphStyle(
        'CardBody', fontName='Helvetica', fontSize=10, 
        textColor=colors.HexColor("#222222"), leading=16 # leading = espaçamento entre linhas
    )

    # --- 1. CABEÇALHO GERAL DO DOCUMENTO ---
    nome_paciente = dados_paciente.get('nome', 'Paciente não informado')
    hoje = datetime.datetime.now().strftime("%d/%m/%Y")

    elementos.append(Paragraph("Plano Alimentar", estilo_titulo))
    elementos.append(Paragraph(nome_paciente, estilo_subtitulo))
    elementos.append(Paragraph(hoje, estilo_data))
    
    # Linha divisória fina
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceBefore=5, spaceAfter=10))
    
    elementos.append(Paragraph("Todos os dias", estilo_subtitulo))
    elementos.append(Paragraph(f"Plano alimentar para {nome_paciente}", estilo_subtitulo))
    elementos.append(Spacer(1, 15*mm))

    # --- 2. PROCESSAMENTO E CRIAÇÃO DOS CARDS DE REFEIÇÃO ---
    # O regex divide o texto usando os **asteriscos** das refeições
    refeicoes = re.split(r'\*\*(.*?)\*\*', texto_cardapio)
    
    # A lista 'refeicoes' fica assim: ['', 'Café da manhã', 'texto do café...', 'Almoço', 'texto...']
    for i in range(1, len(refeicoes), 2):
        nome_refeicao = refeicoes[i].strip()
        conteudo_refeicao = refeicoes[i+1].strip()
        
        # Ignora blocos vazios
        if not conteudo_refeicao:
            continue
            
        # Converte as quebras de linha em <br/> para o Paragraph entender
        conteudo_html = conteudo_refeicao.replace('\n', '<br/>')
        
        # Monta os dados da tabela (Card)
        # Linha 0: Cabeçalho (Ex: Café da Manhã)
        # Linha 1: Conteúdo (Alimentos)
        dados_card = [
            [Paragraph(nome_refeicao, estilo_card_header)],
            [Paragraph(conteudo_html, estilo_card_body)]
        ]
        
        # Cria a tabela simulando um Card
        card = Table(dados_card, colWidths=[180*mm])
        
        # PALETA MONOCROMÁTICA PRINT-FRIENDLY
        COR_FUNDO_HEADER = colors.HexColor("#4F4F4F") # Cinza Chumbo
        COR_FUNDO_BODY = colors.HexColor("#F7F7F7")   # Cinza Gelo (gasta pouquíssima tinta)
        COR_BORDA = colors.HexColor("#E0E0E0")        # Cinza claro para borda
        
        card.setStyle(TableStyle([
            # Estilo do Cabeçalho da Refeição
            ('BACKGROUND', (0,0), (0,0), COR_FUNDO_HEADER),
            ('TEXTCOLOR', (0,0), (0,0), colors.white),
            ('TOPPADDING', (0,0), (0,0), 6),
            ('BOTTOMPADDING', (0,0), (0,0), 6),
            ('LEFTPADDING', (0,0), (0,0), 12),
            ('RIGHTPADDING', (0,0), (0,0), 12),
            ('VALIGN', (0,0), (0,0), 'MIDDLE'),
            
            # Estilo do Corpo da Refeição (Alimentos)
            ('BACKGROUND', (0,1), (0,1), COR_FUNDO_BODY),
            ('TOPPADDING', (0,1), (0,1), 12),
            ('BOTTOMPADDING', (0,1), (0,1), 12),
            ('LEFTPADDING', (0,1), (0,1), 12),
            ('RIGHTPADDING', (0,1), (0,1), 12),
            
            # Borda ao redor do card inteiro
            ('BOX', (0,0), (-1,-1), 1, COR_BORDA),
        ]))
        
        elementos.append(card)
        elementos.append(Spacer(1, 8*mm)) # Espaço entre um card e outro

    # 3. RODAPÉ FIXO (Numerador de página)
    def desenhar_rodape(canvas, doc):
        canvas.saveState()
        W, H = A4
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#AAAAAA"))
        canvas.drawString(15*mm, 10*mm, "Gerado pelo Sistema NutriAPS | Buritis-RO")
        canvas.drawRightString(W - 15*mm, 10*mm, f"Página {doc.page}")
        canvas.restoreState()

    # Gera o PDF final
    doc.build(elementos, onFirstPage=desenhar_rodape, onLaterPages=desenhar_rodape)
    
    return buf.getvalue()

# ═══════════════════════════════════════════════════════════════════════════
# PDF DA GESTANTE — Padrão MS 2026 — Impressão em Preto e Branco
# ═══════════════════════════════════════════════════════════════════════════

def gerar_pdf_gestante(dados_g):
    """
    PDF Obstétrico Diamante atualizado para as Diretrizes MS (2026) e SBD.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_JUSTIFY
    from io import BytesIO
    import datetime

    W, H = A4
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    # PALETA MONOCROMÁTICA IMPRESSÃO-FRIENDLY
    PRETO_TITULO = colors.HexColor("#000000")
    PRETO_TEXTO = colors.HexColor("#222222")
    CINZA_ESCURO = colors.HexColor("#555555")
    CINZA_MEDIO = colors.HexColor("#AAAAAA")
    CINZA_CLARO = colors.HexColor("#DDDDDD")
    CINZA_FUNDO = colors.HexColor("#EEEEEE")
    BRANCO = colors.white

    res = dados_g['res_gest']
    hoje = datetime.datetime.now().strftime("%d/%m/%Y")

    peso_base_str = f"{res['peso_base']:.1f} kg"
    if res['is_peso_estimado']:
        peso_base_str += " (Estimado na Consulta)"

    # ── PÁGINA 1: CAPA, BIOMETRIA E LAUDOS CLÍNICOS ──
    c.setFillColor(CINZA_FUNDO)
    c.rect(0, H - 65*mm, W, 65*mm, fill=1, stroke=0)
    
    c.setFillColor(PRETO_TITULO)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(15*mm, H - 25*mm, "Mapa de Saúde Gestacional")

    c.setFont("Helvetica", 11)
    c.setFillColor(CINZA_ESCURO)
    c.drawString(15*mm, H - 32*mm, "Atenção Primária à Saúde | Linha de Cuidado da Gestante")
    c.setFont("Helvetica", 9)
    c.drawString(15*mm, H - 37*mm, "Diretrizes Ministério da Saúde (2026) / SBD")

    c.setFillColor(PRETO_TITULO)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(15*mm, H - 48*mm, str(dados_g['nome']).upper())
    
    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_ESCURO)
    c.drawString(15*mm, H - 54*mm, f"Gerado em {hoje}")

    # CARDS DE MÉTRICAS RÁPIDAS
    larg_card = 52*mm
    y_cards = H - 85*mm
    _tag_metrica_mono(c, 15*mm, y_cards, larg_card, "IDADE GESTACIONAL", f"{dados_g['semana']} sem")
    _tag_metrica_mono(c, 71*mm, y_cards, larg_card, "GANHO ATUAL", f"{res['ganho_atual']:.1f} kg")
    _tag_metrica_mono(c, 127*mm, y_cards, larg_card, "IMC PRÉ-GESTACIONAL", f"{res['imc_pre']:.1f}")
    
    _card_mono(c, 127*mm, y_cards - 12*mm, larg_card, 7*mm, cor_fundo=CINZA_CLARO)
    c.setFillColor(PRETO_TEXTO)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(127*mm + larg_card/2, y_cards - 9*mm, res['classificacao_pre'].upper())

    # SEÇÃO 1: BIOMETRIA
    y = y_cards - 25*mm
    y = _titulo_secao_mono(c, y, "1. DADOS OBSTÉTRICOS E BIOMETRIA")
    y -= 5*mm
    y = _linha_info_mono(c, y, "Peso Inicial de Referência (Base):", peso_base_str, fundo=True)
    y = _linha_info_mono(c, y, "Peso Atual na Consulta:", f"{dados_g['peso']:.1f} kg", fundo=False)
    y = _linha_info_mono(c, y, f"Meta para a Semana Atual ({dados_g['semana']} sem):", f"{res['meta_semana_min']:.1f} a {res['meta_semana_max']:.1f} kg", fundo=True)
    y = _linha_info_mono(c, y, "Meta de Ganho Total até o Parto:", f"{res['meta_total_min']:.1f} a {res['meta_total_max']:.1f} kg", fundo=False)
    
    # SEÇÃO 2: DIAGNÓSTICO DO GANHO DE PESO
    y -= 8*mm
    y = _titulo_secao_mono(c, y, "2. AVALIAÇÃO DO GANHO DE PESO ACUMULADO")
    y -= 4*mm
    texto_laudo = f"\"{res['diagnostico']}\" — {res['conselho']}"
    estilo_justificado = ParagraphStyle('Just', fontName='Helvetica-Oblique', fontSize=9, textColor=CINZA_ESCURO, alignment=TA_JUSTIFY, leading=13)
    p = Paragraph(texto_laudo, estilo_justificado)
    w_p, h_p = p.wrap(175*mm, 50*mm)
    y -= h_p
    p.drawOn(c, 18*mm, y)

    # SEÇÃO 3: CUIDADOS ESPECIAIS
    is_dmg = dados_g.get('is_dmg', False)
    is_has = dados_g.get('is_has', False)

    if is_dmg or is_has:
        y -= 8*mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(PRETO_TITULO)
        c.drawString(15*mm, y, "CUIDADOS ESPECIAIS")
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.3)
        c.line(15*mm, y - 2*mm, 195*mm, y - 2*mm)
        y -= 6*mm

        if is_dmg and is_has:
            texto_especial = "Neste momento, seu corpo está passando por grandes adaptações com a glicose e a pressão. Isso exige carinho e cuidado em dobro com as suas escolhas. O alimento será o seu principal remédio para que você e o bebê cheguem ao final da gestação com muita saúde. Vamos unir forças: comida de verdade, feita em casa. Descasque mais e desembale menos. Evite industrializados, doces e temperos prontos. Foque no arroz com feijão, carnes magras, ovos, saladas variadas e muita hidratação. Estamos juntos com você nessa jornada!"
        elif is_dmg:
            texto_especial = "Notamos que a sua glicose está precisando de uma atenção especial. Fique tranquila! Nossa missão não é fazer você passar fome ou cortar todo o carboidrato, mas sim ensinar o seu corpo a absorver o açúcar bem devagar para proteger o crescimento do bebê. Sempre combine um carboidrato com uma fibra ou proteína. Vai comer uma fruta? Adicione aveia ou linhaça. Vai comer um pão? Coloque um ovo ou queijo. Evite sucos coados (mesmo os naturais) e doces isolados, priorizando refeições completas. Fracionar a alimentação ajuda a evitar picos de glicose!"
        elif is_has:
            texto_especial = "Sua pressão arterial está exigindo um cuidado extra para garantir que os nutrientes e o oxigênio cheguem perfeitamente até o seu bebê. Vamos fazer adjustments simples na cozinha que farão toda a diferença. Esconda o saleiro da mesa e abuse de temperos naturais: alho, cebola, limão, orégano e cheiro-verde. É fundamental retirar da rotina os temperos em cubo, macarrão instantâneo, embutidos (salsicha, calabresa) e salgadinhos. Aumente o consumo de água, frutas e vegetais, pois eles contêm nutrientes que ajudam a relaxar os vasos sanguíneos!"

        p_esp = Paragraph(texto_especial, estilo_justificado)
        w_esp, h_esp = p_esp.wrap(175*mm, 60*mm)
        y -= h_esp
        p_esp.drawOn(c, 18*mm, y)

    # SEÇÃO 4: MONITORAMENTO DE GLICEMIA (SBD)
    diag_dmg = dados_g.get('diagnostico_dmg', 'Sem rastreio')
    alerta_dmg = dados_g.get('alerta_dmg', '')
    
    y -= 10*mm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(PRETO_TITULO)
    c.drawString(15*mm, y, "3. RASTREIO GLICÊMICO E RISCO METABÓLICO")
    c.setStrokeColor(colors.black)
    c.setLineWidth(0.3)
    c.line(15*mm, y - 2*mm, 195*mm, y - 2*mm)
    y -= 7*mm
    
    if diag_dmg != "Sem rastreio":
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(PRETO_TEXTO)
        c.drawString(15*mm, y, f"Status Glicêmico: {diag_dmg}")
        y -= 4*mm
        c.setFont("Helvetica", 9)
        c.setFillColor(CINZA_ESCURO)
        c.drawString(15*mm, y, f"Conduta SBD: {alerta_dmg}" if alerta_dmg else "Exames laboratoriais normais. Manter conduta preventiva da APS.")
    else:
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(CINZA_MEDIO)
        c.drawString(15*mm, y, "Dados de rastreio glicêmico (Jejum/TOTG) não informados nesta consulta.")

    _rodape_pagina_mono(c, dados_g['nome'], 1)
    c.showPage()

    # ── PÁGINA 2: GRÁFICO OFICIAL MS 2026 (GRAYSCALE PARA PDF) ──
    _cabecalho_pagina_mono(c, "Acompanhamento do Ganho de Peso")
    dados_ms = res['dados_ms']
    perc = dados_ms['percentis']
    
    y_graf = H - 35*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(PRETO_TITULO)
    c.drawCentredString(W/2, y_graf, "GRÁFICO DE ACOMPANHAMENTO DO GANHO DE PESO")
    y_graf -= 6*mm
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CINZA_ESCURO)
    c.drawCentredString(W/2, y_graf, f"{res['classificacao_pre'].upper()} ({dados_ms['limite_imc']})")
    y_graf -= 5*mm
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(W/2, y_graf, f"GANHO DE PESO RECOMENDADO ATÉ 40 SEMANAS DE GESTAÇÃO: {dados_ms['rec_ganho']}")
    y_graf -= 8*mm
    
    graf_x, graf_y = 20*mm, y_graf - 110*mm
    graf_w, graf_h = 165*mm, 105*mm
    
    SEM_MIN, SEM_MAX = 10, 40
    Y_MIN, Y_MAX = -10, 25 

    def coord(sem, ganho):
        x = graf_x + ((sem - SEM_MIN) / (SEM_MAX - SEM_MIN)) * graf_w
        g_clamped = max(Y_MIN, min(ganho, Y_MAX))
        y = graf_y + ((g_clamped - Y_MIN) / (Y_MAX - Y_MIN)) * graf_h
        return x, y

    # Fundo Branco e Grade Fina (1 em 1 kg)
    c.setFillColor(BRANCO)
    c.rect(graf_x, graf_y, graf_w, graf_h, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#EAEAEA"))
    c.setLineWidth(0.3)
    
    c.setFont("Helvetica", 6)
    c.setFillColor(CINZA_ESCURO)
    for sem in range(SEM_MIN, SEM_MAX + 1):
        x, _ = coord(sem, Y_MIN)
        c.line(x, graf_y, x, graf_y + graf_h)
        c.drawCentredString(x, graf_y - 3*mm, str(sem))
        
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(graf_x + graf_w/2, graf_y - 10*mm, "← SEMANA DE GESTAÇÃO →")

    c.setFont("Helvetica", 6)
    for val_y in range(Y_MIN, Y_MAX + 1):
        _, y = coord(SEM_MIN, val_y)
        c.line(graf_x, y, graf_x + graf_w, y)
        c.drawRightString(graf_x - 1.5*mm, y - 1*mm, str(val_y))
    
    c.saveState()
    c.rotate(90)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(graf_y + graf_h/2, -(graf_x - 6*mm), "← GANHO DE PESO GESTACIONAL (kg) →")
    c.restoreState()

    # Marcações e Textos dos 3 Trimestres
    c.setStrokeColor(CINZA_MEDIO); c.setLineWidth(1.5)
    c.line(coord(13, Y_MIN)[0], graf_y, coord(13, Y_MIN)[0], graf_y + graf_h)
    c.line(coord(27, Y_MIN)[0], graf_y, coord(27, Y_MIN)[0], graf_y + graf_h)
    
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(coord(11.5, Y_MIN)[0], graf_y - 6*mm, "1º Trimestre")
    c.drawCentredString(coord(20, Y_MIN)[0], graf_y - 6*mm, "2º Trimestre")
    c.drawCentredString(coord(33.5, Y_MIN)[0], graf_y - 6*mm, "3º Trimestre")

    # === DESENHO DAS ZONAS EM ESCALA DE CINZA ===
    C_FILL = colors.HexColor("#F0F0F0") # Sombreamento da zona recomendada
    C_SAFE = colors.HexColor("#444444") # Linhas da zona de adequação (Sólidas)
    C_OUT = colors.HexColor("#888888")  # Linhas fora da zona (Tracejadas)
    
    x_vals = list(range(10, 41))
    keys_sorted = sorted(perc.keys(), key=lambda k: float(k.replace('P','')))
    
    # 1. Desenhar Área Sombreada (Fill)
    y_bottom = perc[dados_ms["safe_min_key"]]
    y_top = perc[dados_ms["safe_max_key"]]
    c.setFillColor(C_FILL)
    p = c.beginPath()
    p.moveTo(*coord(x_vals[0], y_bottom[0]))
    for i in range(1, len(x_vals)): p.lineTo(*coord(x_vals[i], y_bottom[i]))
    for i in range(len(x_vals)-1, -1, -1): p.lineTo(*coord(x_vals[i], y_top[i]))
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # 2. Desenhar as Linhas (Tracejadas vs Sólidas)
    for k in keys_sorted:
        is_safe = (k == dados_ms["safe_min_key"] or k == dados_ms["safe_max_key"])
        c.setStrokeColor(C_SAFE if is_safe else C_OUT)
        c.setLineWidth(1.5 if is_safe else 1.0)
        
        if not is_safe: c.setDash(3, 2)
        else: c.setDash()
        
        y_vals = perc[k]
        for i in range(len(x_vals)-1):
            c.line(*coord(x_vals[i], y_vals[i]), *coord(x_vals[i+1], y_vals[i+1]))
        
        # Bolinhas brancas e Rótulos dos Percentis
        c.setFillColor(BRANCO)
        c.circle(coord(40, y_vals[-1])[0] + 3*mm, coord(40, y_vals[-1])[1], 2.5*mm, fill=1, stroke=1)
        c.setFillColor(C_SAFE if is_safe else C_OUT)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(coord(40, y_vals[-1])[0] + 3*mm, coord(40, y_vals[-1])[1] - 1*mm, k)

    # 3. Ponto da Paciente
    x_pac, y_pac = coord(dados_g['semana'], res['ganho_atual'])
    c.setStrokeColor(PRETO_TITULO)
    c.setLineWidth(0.5); c.setDash(2,2)
    c.line(graf_x, y_pac, x_pac, y_pac); c.line(x_pac, graf_y, x_pac, y_pac) 
    c.setDash(); c.setFillColor(PRETO_TITULO)
    c.circle(x_pac, y_pac, 2*mm, fill=1, stroke=1)
    
    # 4. Fonte
    c.setFillColor(CINZA_ESCURO)
    c.setFont("Helvetica", 5.5)
    c.drawString(graf_x, graf_y - 15*mm, "Fonte: KAC, G. et al. Gestational weight gain charts: results from the Brazilian Maternal and Child Nutrition Consortium. Am. J. Clin. Nutr., v. 113, n. 5, p. 1351-1360, 2021. DOI: https://doi.org/10.1093/ajcn/nqaa402")

    # ── TABELA DINÂMICA COM ANTI-OVERLAP ──
    y_tab = graf_y - 20*mm
    tab_data = [
        ["Marcos Gestacionais", "Meta Mínima", "Meta Máxima"],
        [f"Até 13 semanas (1º Trimestre)", f"{perc[dados_ms['safe_min_key']][3]:+.1f} kg", f"{perc[dados_ms['safe_max_key']][3]:+.1f} kg"],
        [f"Até 27 semanas (2º Trimestre)", f"{perc[dados_ms['safe_min_key']][17]:+.1f} kg", f"{perc[dados_ms['safe_max_key']][17]:+.1f} kg"],
        [f"Até 40 semanas (3º Trimestre)", f"{perc[dados_ms['safe_min_key']][-1]:+.1f} kg", f"{perc[dados_ms['safe_max_key']][-1]:+.1f} kg"]
    ]
    tab = Table(tab_data, colWidths=[75*mm, 45*mm, 45*mm])
    tab.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), CINZA_ESCURO), ("TEXTCOLOR", (0,0), (-1,0), BRANCO),
        ("ALIGN", (0,0), (-1,-1), "CENTER"), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), 
        ("FONTSIZE", (0,0), (-1,-1), 8), ("GRID", (0,0), (-1,-1), 0.5, CINZA_CLARO),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [BRANCO, CINZA_FUNDO]),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)
    ]))
    
    # O ReportLab avalia a altura da tabela e joga os Desafios exatamente pra baixo dela
    w_tab, h_tab = tab.wrapOn(c, W, H)
    tab.drawOn(c, 22.5*mm, y_tab - h_tab)

    # ── ESPAÇO DE DESAFIOS ──
    y_desafios = y_tab - h_tab - 10*mm
    y_desafios = _titulo_secao_mono(c, y_desafios, "5. MEUS DESAFIOS E DIFICULDADES (Espaço da Paciente)")
    y_desafios -= 4*mm
    
    c.setFont("Helvetica-BoldOblique", 9); c.setFillColor(PRETO_TEXTO)
    c.drawString(15*mm, y_desafios, "O que foi mais difícil de seguir na dieta ou nos conselhos que combinamos?")
    
    y_desafios -= 5*mm
    c.setFont("Helvetica", 8.5); c.setFillColor(CINZA_ESCURO)
    c.drawString(15*mm, y_desafios, "Anote abaixo suas dúvidas e barreiras. Leve este papel na próxima consulta.")

    y_linhas = y_desafios - 12*mm
    c.setStrokeColor(CINZA_MEDIO); c.setLineWidth(0.5); c.setDash(1, 2)
    for _ in range(4): 
        c.line(15*mm, y_linhas, 195*mm, y_linhas)
        y_linhas -= 9*mm
    c.setDash()

    _rodape_pagina_mono(c, dados_g['nome'], 2)
    c.showPage()
    c.save()

    # ESSA É A LINHA MÁGICA QUE FALTAVA (Ela devolve o PDF gerado)
    return buf.getvalue()

# ═══════════════════════════════════════════════════════════════════════════
# PDF ESPECÍFICO DO IDOSO (Focado em clareza, mastigação e longevidade)
# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
# PDF ESPECÍFICO DO IDOSO (Padrão MS Grayscale Print-Friendly + 10 Passos)
# ═══════════════════════════════════════════════════════════════════════════
def gerar_pdf_idoso(nome, idade, sexo, peso, altura, imc, classif_imc,
                    tmb, get, formula_nome, risco, explicacao, respostas_hab):
    import datetime
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_JUSTIFY
    from io import BytesIO

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    # PALETA MONOCROMÁTICA IMPRESSÃO-FRIENDLY
    PRETO_TITULO = colors.HexColor("#000000")
    PRETO_TEXTO = colors.HexColor("#222222")
    CINZA_ESCURO = colors.HexColor("#555555")
    CINZA_CLARO = colors.HexColor("#DDDDDD")
    CINZA_FUNDO = colors.HexColor("#EEEEEE")
    BRANCO = colors.white

    meses = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", 
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = datetime.datetime.now()
    data_formatada = f"Gerado em {hoje.day:02d} de {meses[hoje.month]} de {hoje.year}"

    # Estilos seguros de parágrafo para não vazar texto
    estilo_texto = ParagraphStyle('Texto', fontName='Helvetica', fontSize=9, textColor=CINZA_ESCURO, alignment=TA_JUSTIFY, leading=13)
    
    classif_curta = _limpar(classif_imc).upper()
    if classif_curta == "ADEQUADO OU EUTRÓFICO": classif_curta = "EUTRÓFICO"

    # --- PÁGINA 1: Capa e Biometria ---
    c.setFillColor(CINZA_FUNDO)
    c.rect(0, H - 65*mm, W, 65*mm, fill=1, stroke=0)
    
    c.setFillColor(PRETO_TITULO)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(15*mm, H - 25*mm, "Mapa de Saúde Nutricional")

    c.setFont("Helvetica", 11)
    c.setFillColor(CINZA_ESCURO)
    c.drawString(15*mm, H - 32*mm, "Atenção Primária à Saúde | Saúde da Pessoa Idosa")
    c.setFont("Helvetica", 9)
    c.drawString(15*mm, H - 37*mm, "Avaliação Geriátrica e Orientações (VAN/MS)")

    c.setFillColor(PRETO_TITULO)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(15*mm, H - 48*mm, _limpar(nome).upper())
    
    c.setFont("Helvetica", 9)
    c.setFillColor(CINZA_ESCURO)
    c.drawString(15*mm, H - 54*mm, data_formatada)

    # Cards de Métricas Rápidas
    larg_card = 52*mm
    y_cards = H - 85*mm
    _tag_metrica_mono(c, 15*mm, y_cards, larg_card, "GASTO ENERGIA", f"{get:.0f} kcal")
    _tag_metrica_mono(c, 71*mm, y_cards, larg_card, "PESO ATUAL", f"{peso:.1f} kg")
    _tag_metrica_mono(c, 127*mm, y_cards, larg_card, "IMC GERIÁTRICO", f"{imc:.1f}")
    
    _card_mono(c, 127*mm, y_cards - 12*mm, larg_card, 7*mm, cor_fundo=CINZA_CLARO)
    c.setFillColor(PRETO_TEXTO)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(127*mm + larg_card/2, y_cards - 9*mm, classif_curta)

    # SEÇÃO 1: Identificação (Rótulos curtos para não bugar)
    y = y_cards - 25*mm
    y = _titulo_secao_mono(c, y, "1. IDENTIFICAÇÃO E BIOMETRIA")
    y -= 5*mm
    y = _linha_info_mono(c, y, "Nome Completo:", nome, fundo=True)
    y = _linha_info_mono(c, y, "Idade:", f"{idade} anos", fundo=False)
    y = _linha_info_mono(c, y, "Estatura (Altura):", f"{altura} cm", fundo=True)
    y = _linha_info_mono(c, y, "Classificação (VAN/MS):", classif_curta, fundo=False)
    y -= 8*mm

    # SEÇÃO 2: Cuidados Essenciais
    y = _titulo_secao_mono(c, y, "2. CUIDADOS ESSENCIAIS NO DIA A DIA")
    y -= 4*mm
    
    texto_cuidados = (
        "<b>• Hidratação é Remédio:</b> Beba água mesmo sem estar com sede. Com o passar dos anos, "
        "o corpo não avisa sobre a sede corretamente. A falta de água causa confusão mental, intestino preso e tonturas.<br/><br/>"
        "<b>• Atenção à Mastigação:</b> Se estiver difícil mastigar ou engolir, não deixe de comer carnes e frutas. "
        "Amasse bem, faça na forma de purês, desfie as carnes ou faça carne moída. Sopas com pedaços macios são excelentes.<br/><br/>"
        "<b>• Menos Sal, Mais Sabor:</b> A capacidade de sentir o gosto do sal diminui na terceira idade, o que faz a "
        "gente querer colocar mais. Evite o saleiro na mesa. Capriche no alho, cebola, limão, orégano e ervas.<br/><br/>"
        "<b>• Força e Ossos:</b> Não deixe de consumir proteínas (ovos, queijos, carnes) para evitar fraqueza nas pernas. "
        "E lembre-se: tomar 15 minutos de sol pela manhã ajuda a fixar o cálcio nos ossos."
    )
    p = Paragraph(texto_cuidados, estilo_texto)
    w_p, h_p = p.wrap(175*mm, 80*mm)
    y -= h_p
    p.drawOn(c, 18*mm, y)

    _rodape_pagina_mono(c, nome, c.getPageNumber())
    c.showPage()

    # --- PÁGINA 2: Hábitos e PRAR ---
    _cabecalho_pagina_mono(c, "Avaliação de Hábitos Alimentares")
    
    y = H - 35*mm
    y = _titulo_secao_mono(c, y, "3. DIAGNÓSTICO DO RISCO ALIMENTAR")

    y -= 4*mm
    _card_mono(c, 15*mm, y - 10*mm, W - 30*mm, 10*mm, cor_fundo=CINZA_FUNDO)
    c.setFillColor(PRETO_TITULO)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W/2, y - 6.5*mm, f"NÍVEL DE RISCO IDENTIFICADO: {risco.upper()}")
    y -= 16*mm

    p_exp = Paragraph(_limpar(explicacao), estilo_texto)
    w_e, h_e = p_exp.wrap(175*mm, 40*mm)
    y -= h_e
    p_exp.drawOn(c, 18*mm, y)
    y -= 10*mm

    y = _titulo_secao_mono(c, y, "RESUMO DO INQUÉRITO CLÍNICO")
    y -= 2*mm

    for i, (pergunta, resposta) in enumerate(respostas_hab):
        if resposta is None: continue
        resp_limpa = str(resposta).split(" (")[0]
        fundo = CINZA_FUNDO if i % 2 == 0 else BRANCO
        
        c.setFillColor(fundo)
        c.setStrokeColor(CINZA_CLARO)
        c.setLineWidth(0.3)
        c.rect(15*mm, y - 6*mm, W - 30*mm, 8*mm, fill=1, stroke=1)

        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(PRETO_TEXTO)
        c.drawString(18*mm, y - 2*mm, _limpar(pergunta)[:70])

        c.setFont("Helvetica", 7.5)
        c.setFillColor(CINZA_ESCURO)
        c.drawRightString(W - 18*mm, y - 2*mm, _limpar(resp_limpa))
        y -= 8*mm

    _rodape_pagina_mono(c, nome, c.getPageNumber())
    c.showPage()

    # --- PÁGINA 3: Os 10 Passos do Ministério da Saúde ---
    _cabecalho_pagina_mono(c, "Dez Passos para a Alimentação Saudável")
    
    y = H - 35*mm
    c.setFillColor(PRETO_TITULO)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W/2, y, "10 PASSOS PARA UMA ALIMENTAÇÃO SAUDÁVEL PARA PESSOAS IDOSAS")
    y -= 5*mm
    c.setFont("Helvetica", 8)
    c.setFillColor(CINZA_ESCURO)
    c.drawCentredString(W/2, y, "Baseado no Manual do Ministério da Saúde (Edição 2010)")
    y -= 12*mm

    passos = [
        "<b>1º PASSO:</b> Faça pelo menos três refeições (café da manhã, almoço e jantar) e dois lanches saudáveis por dia. Não pule as refeições e mastigue bem os alimentos.",
        "<b>2º PASSO:</b> Inclua diariamente seis porções do grupo dos cereais (arroz, milho, trigo, pães e massas), tubérculos como a batata e raízes nas refeições. Dê preferência aos grãos integrais.",
        "<b>3º PASSO:</b> Coma diariamente pelo menos três porções de legumes e verduras como parte das refeições e três porções ou mais de frutas nas sobremesas e lanches.",
        "<b>4º PASSO:</b> Coma feijão com arroz todos os dias ou, pelo menos, cinco vezes por semana. Esse prato brasileiro é uma combinação completa de proteínas e bom para a saúde.",
        "<b>5º PASSO:</b> Consuma diariamente três porções de leite e derivados e uma porção de carnes, aves, peixes ou ovos. Retire a gordura aparente das carnes.",
        "<b>6º PASSO:</b> Consuma, no máximo, uma porção por dia de óleos vegetais, azeite, manteiga ou margarina. Evite frituras e salgadinhos.",
        "<b>7º PASSO:</b> Evite refrigerantes e sucos industrializados, bolos, biscoitos doces e recheados, sobremesas e outras guloseimas. Coma-os, no máximo, duas vezes por semana.",
        "<b>8º PASSO:</b> Diminua a quantidade de sal na comida e retire o saleiro da mesa. Use temperos como cheiro verde, alho, cebola e ervas frescas e secas.",
        "<b>9º PASSO:</b> Beba pelo menos dois litros (seis a oito copos) de água por dia. Dê preferência ao consumo de água nos intervalos das refeições.",
        "<b>10º PASSO:</b> Torne sua vida mais saudável. Pratique pelo menos 30 minutos de atividade física todos os dias, evite bebidas alcoólicas e o fumo."
    ]

    for passo in passos:
        p_passo = Paragraph(passo, estilo_texto)
        w_p, h_p = p_passo.wrap(175*mm, 30*mm)
        
        # Garante que não corte o texto no final da página
        if (y - h_p) < 20*mm:
            _rodape_pagina_mono(c, nome, c.getPageNumber())
            c.showPage()
            _cabecalho_pagina_mono(c, "Dez Passos para a Alimentação Saudável (Cont.)")
            y = H - 35*mm
        
        p_passo.drawOn(c, 18*mm, y - h_p)
        y -= (h_p + 6*mm) # Espaçamento confortável entre cada passo

    _rodape_pagina_mono(c, nome, c.getPageNumber())
    
    c.save()
    return buf.getvalue()