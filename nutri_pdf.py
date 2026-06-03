import locale
import datetime
import re
import textwrap
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

    meses = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", 
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
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
def gerar_pdf_cardapio_ia(dados_paciente: dict, texto_cardapio: str) -> bytes:

    nome = dados_paciente.get("nome", "Paciente")
    buf  = BytesIO()
    c    = canvas.Canvas(buf, pagesize=A4)

    # ─── PÁGINA 1 — Capa do Cardápio ─────────────────────────────────────
    c.setFillColor(AZUL_ESCURO)
    c.rect(0, H - 70*mm, W, 70*mm, fill=1, stroke=0)
    c.setFillColor(AZUL_MEDIO)
    c.rect(0, H - 73*mm, W, 4*mm, fill=1, stroke=0)

    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(15*mm, H - 28*mm, "Cardápio Personalizado")
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#DDDDDD"))
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(15*mm, H - 50*mm, _limpar(nome))
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#CCCCCC"))
    c.drawString(15*mm, H - 58*mm,
                 datetime.datetime.now().strftime("Gerado em %d/%m/%Y"))

    # Métricas
    larg = 55*mm
    _tag_metrica(c, 15*mm,  H - 93*mm, larg,
                 "Gasto Energético Total", f"{dados_paciente.get('get',0):.0f} kcal")
    _tag_metrica(c, 75*mm,  H - 93*mm, larg,
                 "Peso", f"{dados_paciente.get('peso',0):.1f} kg")
    _tag_metrica(c, 135*mm, H - 93*mm, larg,
                 "IMC",
                 f"{dados_paciente.get('imc',0):.1f}",
                 cor=VERDE if dados_paciente.get('imc',30) < 25 else
                     AMARELO if dados_paciente.get('imc',30) < 30 else VERMELHO)

    # ─── Corpo do cardápio ────────────────────────────────────────────────
    y = H - 105*mm
    y = _titulo_secao(c, y, "Plano Alimentar do Dia", cor=AZUL_MEDIO)
    y -= 3*mm

    SUBTITULOS = ["café", "lanche", "almoço", "jantar", "ceia", "total", "dica"]
    num_pag = 1
    table_data = []

    def desenhar_tabela_acumulada(c, dados_tabela, y_atual, pag_atual):
        if not dados_tabela:
            return y_atual, pag_atual
            
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        
        # Estilos do Paragraph para permitir a quebra de texto (wrap) automática
        style_header = ParagraphStyle(
            name='Header', fontName='Helvetica-Bold', fontSize=8, 
            textColor=BRANCO, alignment=TA_CENTER
        )
        style_body = ParagraphStyle(
            name='Body', fontName='Helvetica', fontSize=8, 
            textColor=CINZA_TEXTO, alignment=TA_CENTER
        )

        # Converte as strings brutas em Paragraphs do ReportLab
        dados_formatados = []
        for row_idx, row in enumerate(dados_tabela):
            nova_linha = []
            for col in row:
                texto = str(col).strip()
                if row_idx == 0:
                    nova_linha.append(Paragraph(texto, style_header))
                else:
                    nova_linha.append(Paragraph(texto, style_body))
            dados_formatados.append(nova_linha)
        
        num_cols = len(dados_tabela[0])
        largura_disp = W - 30*mm
        
        # Ajuste inteligente de largura das colunas
        if num_cols == 8:
            # Dá mais espaço para Alimento e Medidas, menos para os Macros
            col_w = [
                largura_disp * 0.22, # Alimento
                largura_disp * 0.14, # Quantidade
                largura_disp * 0.18, # Medida caseira
                largura_disp * 0.09, # kcal
                largura_disp * 0.09, # Proteína
                largura_disp * 0.10, # Carboidrato
                largura_disp * 0.09, # Gordura
                largura_disp * 0.09  # Fibra
            ]
        else:
            col_w = [largura_disp / num_cols] * num_cols

        t_style = TableStyle([
            ("BACKGROUND",   (0,0), (-1,0),  AZUL_ESCURO),
            ("ALIGN",        (0,0), (-1,-1), "CENTER"),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [BRANCO, CINZA_ALT]),
            ("GRID",         (0,0), (-1,-1), 0.3, CINZA_BORDA),
            ("TOPPADDING",   (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LEFTPADDING",  (0,0), (-1,-1), 2),
            ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ])
        
        t = Table(dados_formatados, colWidths=col_w)
        t.setStyle(t_style)
        tw, th = t.wrapOn(c, W - 30*mm, H)
        
        # Se a tabela não couber inteira na página, quebra a página antes de desenhá-la
        if y_atual - th < 20*mm:
            _rodape_pagina(c, nome, pag_atual)
            c.showPage()
            pag_atual += 1
            _cabecalho_pagina(c, "Cardápio (continuação)")
            y_atual = H - 35*mm
            
        t.drawOn(c, 15*mm, y_atual - th)
        return y_atual - th - 6*mm, pag_atual

    for linha in texto_cardapio.splitlines():
        linha_b = _limpar_md(_limpar(linha)).strip()
        
        # 1. Verifica se a linha atual é de uma Tabela Markdown (inicia e termina com |)
        if linha_b.startswith('|') and linha_b.endswith('|'):
            # Ignora a linha divisória do Markdown (ex: |---|---|)
            if '---' in linha_b:
                continue
            
            # Limpa e extrai as colunas
            colunas = [col.strip() for col in linha_b.strip('|').split('|')]
            table_data.append(colunas)
            continue
            
        else:
            # 2. Se a linha não é tabela, mas a tabela estava sendo construída, DESENHA a tabela agora.
            if table_data:
                y, num_pag = desenhar_tabela_acumulada(c, table_data, y, num_pag)
                table_data = [] # Zera a tabela para a próxima
                
            # 3. Fluxo normal: Texto, Pulos de linha e Subtítulos
            if not linha_b:
                y -= 3*mm
                continue

            eh_sub = any(linha_b.lower().startswith(s) for s in SUBTITULOS)
            pedacos = textwrap.wrap(linha_b, width=90) or [linha_b]

            for i, pedaco in enumerate(pedacos):
                if y < 20*mm:
                    _rodape_pagina(c, nome, num_pag)
                    c.showPage()
                    num_pag += 1
                    _cabecalho_pagina(c, "Cardápio (continuação)")
                    y = H - 35*mm

                if eh_sub and i == 0:
                    y -= 2*mm
                    c.setFillColor(AZUL_CLARO)
                    c.rect(15*mm, y - 1.5*mm, W - 30*mm, 7*mm, fill=1, stroke=0)
                    c.setFillColor(AZUL_MEDIO)
                    c.rect(15*mm, y - 1.5*mm, 3*mm, 7*mm, fill=1, stroke=0)
                    c.setFillColor(AZUL_ESCURO)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(21*mm, y + 0.5*mm, pedaco)
                    y -= 9*mm
                else:
                    c.setFillColor(CINZA_TEXTO)
                    c.setFont("Helvetica", 9)
                    c.drawString(18*mm, y, pedaco)
                    y -= 6*mm

    # 4. Caso o texto acabe mas ainda haja uma tabela pendente, desenha ela.
    if table_data:
        y, num_pag = desenhar_tabela_acumulada(c, table_data, y, num_pag)

    # Nota de rodapé de conteúdo
    y -= 5*mm
    if y < 35*mm:
        _rodape_pagina(c, nome, num_pag)
        c.showPage()
        num_pag += 1
        _cabecalho_pagina(c, "Observações")
        y = H - 35*mm

    nota = ("Este cardápio foi gerado pela ferramenta Mapa Nutricional desenvolvida pelo Nutricionista Residente Tales Formigoni. "
            "Ferramenta preparada exclusivamente para uso na APS por profissionais da Nutrição. "
            "Este cardápio é individual e instransferível.")
    
    # Quebra o texto para não vazar as margens (aprox. 110 caracteres por linha)
    linhas_nota = textwrap.wrap(nota, width=110)
    altura_caixa = (len(linhas_nota) * 4 * mm) + 6 * mm
    
    c.setFillColor(CINZA_ALT)
    # Desenha a caixa cinza com altura dinâmica
    c.rect(15*mm, y - altura_caixa, W - 30*mm, altura_caixa, fill=1, stroke=0)
    
    c.setFillColor(CINZA_TEXTO)
    c.setFont("Helvetica", 7.5)
    
    # Escreve cada linha centralizada
    y_atual = y - 6 * mm
    for linha in linhas_nota:
        c.drawCentredString(W/2, y_atual, linha)
        y_atual -= 4 * mm

    _rodape_pagina(c, nome, num_pag)
    c.save()
    return buf.getvalue()