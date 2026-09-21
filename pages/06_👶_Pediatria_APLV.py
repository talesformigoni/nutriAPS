import streamlit as st
import datetime
import math
from nutri_calc import calcular_escore_z_oms

st.set_page_config(page_title="Pediatria e APLV | NutriAPS", layout="wide")

if "current_module" not in st.session_state or st.session_state["current_module"] != "pediatria":
    st.session_state.clear()
    st.session_state["current_module"] = "pediatria"

# ==========================================
# INJEÇÃO DE CSS COMPLETA (SIDEBAR DA OBESIDADE + TABELA + CARDS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1D361F !important; }
    h1, h2, h3, h4, h5, .titulo-secao { font-family: 'Poppins', sans-serif !important; font-weight: 700 !important; }
    
    .material-icons, .material-symbols-rounded, [data-testid*="Icon"], [data-testid*="Icon"] *, [data-testid="stSidebarCollapseButton"] *, [data-testid="collapsedControl"] *, [class*="icon"] {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
    }
    
    .main { background-color: #ECE5DF !important; padding: 2rem !important; }
    [data-testid="stAppViewContainer"] { background-color: #ECE5DF !important; }

    /* ===================== SIDEBAR (Copiado da Obesidade) ===================== */
    [data-testid="stSidebar"] {
        background-color: #F7F9F7 !important; border-right: 1px solid #E2EBE3 !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }
    [data-testid="stSidebarNav"] { display: none !important; }
    .sidebar-logo { padding: 0rem 1.4rem 1.4rem 1.4rem; border-bottom: 1px solid #E2EBE3; margin-bottom: 1.4rem; }
    .sidebar-logo .logo-title { font-size: 1.3rem; font-weight: 700; color: #1D361F; letter-spacing: -0.02em; font-family: 'Poppins', sans-serif; }
    .sidebar-logo .logo-sub { font-size: 0.75rem; color: #5A7260; margin-top: 0.2rem; }
    .nav-group-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.10em; text-transform: uppercase; color: #859B48; padding: 0 1.4rem; margin-bottom: 0.4rem; font-family: 'Poppins', sans-serif;}
    
    [data-testid="stSidebar"] [data-testid="stPageLink"] { margin: 0 0.7rem 0.15rem 0.7rem !important; }
    [data-testid="stSidebar"] [data-testid="stPageLink"] a {
        display: flex !important; align-items: center !important; gap: 0.55rem !important;
        padding: 0.6rem 0.85rem !important; border-radius: 9px !important;
        font-size: 0.88rem !important; font-weight: 600 !important; color: #2D5A34 !important; text-decoration: none !important;
        font-family: 'Poppins', sans-serif !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background: #E8F0E9 !important; color: #1D361F !important; }

    [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; display: flex !important; flex-direction: column !important; min-height: 92vh !important; }
    .sidebar-footer { margin-top: auto !important; text-align: center !important; font-size: 0.68rem !important; color: #8A9A8E !important; line-height: 1.6 !important; padding-bottom: 1rem !important; }

    /* ===================== ELEMENTOS DA PÁGINA ===================== */
    h1 { font-size: 2.2rem !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.4rem !important; margin-top: 1.8rem !important; margin-bottom: 1rem !important; border-bottom: 2px solid #C4C7B6; padding-bottom: 8px; }
    
    .card-estudo { background: #FFFFFF; border-radius: 12px; padding: 22px; margin-bottom: 15px; border: 1px solid #C4C7B6; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    .card-estudo h4 { margin-top: 0; color: #2D5A34; font-size: 1.15rem; font-weight: 700; margin-bottom: 15px; }
    
    .linha-info { font-family: monospace; font-size: 1.05rem; color: #1D361F; margin: 6px 0; }
    .passo-ag { font-size: 0.95rem; color: #5A7260; margin: 4px 0;}
    .aviso-vazio { color: #8A9A8E; font-style: italic; text-align: center; padding: 30px 0; font-size: 1.1rem; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"], .stDateInput input { 
        background-color: #F7F3F0 !important; border: 1px solid #C4C7B6 !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important;
    }

    /* Layout da Tabela Oficial SESAU */
    .tabela-container { background-color: #FFFFFF; padding: 25px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.04); border: 1px solid #C4C7B6; margin-top: 15px; }
    .tabela-laudo { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 13.5px; color: #111111; }
    .tabela-laudo td, .tabela-laudo th { border: 1px solid #222222; padding: 10px 14px; vertical-align: middle; line-height: 1.5; }
    .bg-gray { background-color: #F4F4F4; font-weight: 600; text-align: center; }

    /* ===================== MEMÓRIA DE CÁLCULO ===================== */
    .memoria-resumo {
        background: linear-gradient(135deg, #F7FAF7 0%, #EEF4EF 100%);
        border: 1px solid #D7E3D8;
        border-radius: 14px;
        padding: 18px 20px;
        margin: 4px 0 16px 0;
    }
    .memoria-resumo-titulo {
        font-family: 'Poppins', sans-serif;
        font-size: 0.80rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #5A7260;
        margin-bottom: 10px;
    }
    .memoria-resumo-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
    }
    .memoria-kpi {
        background: #FFFFFF;
        border: 1px solid #DFE8E0;
        border-radius: 10px;
        padding: 12px 13px;
        min-height: 70px;
    }
    .memoria-kpi span {
        display: block;
        color: #718078;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .memoria-kpi strong {
        display: block;
        color: #1D361F;
        font-family: 'Poppins', sans-serif;
        font-size: 1.02rem;
        line-height: 1.2;
    }
    .memoria-etapa {
        position: relative;
        background: #FFFFFF;
        border: 1px solid #E1E8E2;
        border-radius: 12px;
        padding: 15px 16px 15px 52px;
        margin: 10px 0;
        box-shadow: 0 2px 7px rgba(25, 54, 31, 0.035);
    }
    .memoria-numero {
        position: absolute;
        left: 14px;
        top: 14px;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #2D5A34;
        color: #FFFFFF;
        font-family: 'Poppins', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .memoria-etapa h5 {
        margin: 0 0 7px 0 !important;
        color: #2D5A34;
        font-size: 0.96rem !important;
    }
    .memoria-etapa p {
        margin: 4px 0;
        color: #4E6253;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .memoria-equacao {
        background: #F5F7F5;
        border: 1px solid #E1E6E1;
        border-radius: 8px;
        padding: 10px 12px;
        margin-top: 8px;
        color: #203D25;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.83rem;
        line-height: 1.55;
        white-space: normal;
    }
    .memoria-destaque {
        background: #F1F6E8;
        border: 1px solid #D8E5C2;
        border-left: 4px solid #859B48;
        border-radius: 9px;
        padding: 11px 13px;
        margin-top: 9px;
        color: #344B27;
        font-size: 0.86rem;
        line-height: 1.5;
    }
    .memoria-alerta {
        background: #FFF8E8;
        border: 1px solid #EAD7A6;
        border-left: 4px solid #C69B38;
        border-radius: 9px;
        padding: 11px 13px;
        margin-top: 9px;
        color: #5F4A1B;
        font-size: 0.86rem;
        line-height: 1.5;
    }
    @media (max-width: 900px) {
        .memoria-resumo-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
        <div class="sidebar-logo">
            <div class="logo-title">🍏 NutriAPS</div>
            <div class="logo-sub">Atenção Primária à Saúde</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-group-label">Menu</div>', unsafe_allow_html=True)
    st.page_link("app.py",                         label="🏠  Início")
    st.page_link("pages/01_👥_Populacao_Geral.py", label="👥  População Geral")
    st.page_link("pages/02_🤰_Gestantes.py",       label="🤰  Gestantes")
    st.page_link("pages/03_👴_Idosos.py",          label="👴  Idosos")
    st.page_link("pages/05_⚖️_Obesidade.py",          label="⚖️  Linha de Obesidade")
    st.page_link("pages/06_👶_Pediatria_APLV.py", label="👶  Pediatria / APLV")

    st.markdown("""
        <style>
        a[href$="Protocolo_PRAR"] { background-color: #F0F6F1 !important; border: 1px solid #C4C7B6 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important; }
        a[href$="Protocolo_PRAR"]:hover { background-color: #E8F0E9 !important; border-color: #859B48 !important; }
        </style>
        <div class="nav-group-label" style="margin-top: 1.8rem;">Apoio Clínico</div>
    """, unsafe_allow_html=True)

    st.page_link("pages/04_📚_Protocolo_PRAR.py",  label="📚  Protocolo PRAR")

    st.markdown("""
        <div class="sidebar-footer">
            NutriAPS · v2.0<br>
            Residência Multiprofissional<br>
            Atenção Básica - 2026
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# DICIONÁRIO TRADUTOR OFICIAL SESAU
# ==========================================
tradutor_sesau = {
    "Pregomin Pepti": {
        "codigo": "261",
        "desc": "Fórmula infantil com proteína láctea extensamente hidrolisada sem lactose (FEH)",
        "peso_medida": 4.3,
        "vol_agua": 30.0,
        "classe": "FEH",
        "kcal_100g": 512.0,
        "kcal_100ml": 66.0,
    },
    "Aptamil SL (Sem Lactose)": {
        "codigo": "264",
        "desc": "Fórmula infantil sem lactose (FSL)",
        "peso_medida": 4.3,
        "vol_agua": 30.0,
        "classe": "FSL",
        "kcal_100g": 517.0,
        "kcal_100ml": 67.0,
    },
    "Neocate LCP (Até 3 anos)": {
        "codigo": "274",
        "desc": "Fórmula infantil à base de aminoácidos livres (FAA)",
        "peso_medida": 4.6,
        "vol_agua": 30.0,
        "classe": "FAA",
        "kcal_100g": 496.0,
        "kcal_100ml": 68.0,
    },
    "Aptamil Soja 1 (0 a 6 meses)": {
        "codigo": "272",
        "desc": "Fórmula infantil à base de proteína isolada de soja (FS)",
        "peso_medida": 4.6,
        "vol_agua": 30.0,
        "classe": "FS",
        "kcal_100g": 496.0,
        "kcal_100ml": 69.0,
    },
    "Aptamil Soja 2 (A partir 6 meses)": {
        "codigo": "272",
        "desc": "Fórmula infantil à base de proteína isolada de soja (FS)",
        "peso_medida": 4.6,
        "vol_agua": 30.0,
        "classe": "FS",
        "kcal_100g": 496.0,
        "kcal_100ml": 69.0,
    },
    "Neocate Advance (Acima 1 ano)": {
        "codigo": "258",
        "desc": "Dieta pediátrica para nutrição enteral à base de aminoácidos livres com restrição de lactose",
        "peso_medida": 7.3,
        "vol_agua": 30.0,
        "classe": "FAA",
        "kcal_100g": 475.0,
        "kcal_100ml": 100.0,
    }
}

# ==========================================
# CLASSIFICAÇÃO Z-SCORE EXATA DA SESAU
# ==========================================
def classificar_imc_sesau(z):
    if z is None: return "Sem dados"
    if z < -3: return "Magreza acentuada (< Escore-z -3)"
    elif z < -2: return "Magreza Baixa (≥ Escore-z -3 e < Escore-z -2)"
    elif z <= 1: return "Eutrofia (≥ Escore-z -2 e ≤ Escore-z +1)"
    elif z <= 2: return "Risco de Sobrepeso (> Escore-z +1 e ≤ Escore-z +2)"
    elif z <= 3: return "Sobrepeso (> Escore-z +2 e ≤ Escore-z +3)"
    else: return "Obesidade (> Escore-z +3)"

def classificar_peso_sesau(z):
    if z is None: return "Sem dados"
    if z < -3: return "Muito baixo peso a idade (< Escore-z -3)"
    elif z < -2: return "Baixo peso para idade (≥ Escore-z -3 e < Escore-z -2)"
    elif z <= 2: return "Peso adequado para idade (≥ Escore-z -2 e ≤ Escore-z +2)"
    elif z <= 3: return "Peso elevado para a idade (> Escore-z +2 e ≤ Escore-z +3)"
    else: return "Peso elevado para a idade (> Escore-z +3)"

def classificar_altura_sesau(z):
    if z is None: return "Sem dados"
    if z < -3: return "Muito baixa estatura para a idade (< Escore-z -3)"
    elif z < -2: return "Baixa estatura para idade (≥ Escore-z -3 e < Escore-z -2)"
    else: return "Estatura adequada para criança (≥ Escore-z -2)"

# ==========================================
# REFERÊNCIAS ENERGÉTICAS E TETO PAPLVRO
# ==========================================
def obter_fator_energia_paplvro(idade_meses, sexo):
    """Quadro 3 do Anexo II do PAPLVRO (FAO/WHO, 2004)."""
    masculino = (sexo == "Masculino")
    if idade_meses < 3:
        return 105.0 if masculino else 100.0
    elif idade_meses < 6:
        return 81.0 if masculino else 83.0
    elif idade_meses < 9:
        return 79.0 if masculino else 78.0
    elif idade_meses < 12:
        return 80.0 if masculino else 79.0
    return 83.0 if masculino else 80.0


def obter_desconto_alimentacao_complementar(idade_meses):
    """Quadro 7 do PAPLVRO/CONITEC: energia prevista da alimentação complementar."""
    if idade_meses < 6:
        return 0.0
    elif idade_meses < 8:
        return 200.0
    elif idade_meses < 12:
        return 300.0
    return 550.0


def obter_teto_latas(idade_meses, tipo_formula):
    """
    Teto mensal em equivalentes de latas de 400 g usado pelo motor matemático.

    IMPORTANTE:
    A matemática quantitativa é mantida separada da indicação clínica.
    Portanto, os dois produtos de soja cadastrados (Aptamil Soja 1 e 2)
    continuam gerando cálculo de quantidade, como no código original.
    A adequação da fórmula à idade/mecanismo da APLV é tratada no
    Assistente Clínico, sem zerar a memória matemática.
    """
    classe = tradutor_sesau[tipo_formula].get("classe", "FEH")

    if idade_meses < 3:
        return 9
    elif idade_meses < 6:
        return 10
    elif idade_meses < 9:
        return 8
    elif idade_meses < 12:
        return 7

    # 12-24m: FAA = 7; demais classes = 6.
    return 7 if classe == "FAA" else 6


def adicionar_anos(data, anos):
    """Adiciona anos tratando nascimento em 29/02."""
    try:
        return data.replace(year=data.year + anos)
    except ValueError:
        return data.replace(month=2, day=28, year=data.year + anos)


def calcular_dri_2023(idade_meses, idade_anos_decimal, sexo, peso, altura):
    """DRI/NASEM 2023 para 0-2 anos: GET/TEE + custo energético do crescimento = EER."""
    if sexo == "Masculino":
        get_dri = -716.45 - (1.00 * idade_anos_decimal) + (17.82 * altura) + (15.06 * peso)
        if idade_meses < 3:
            crescimento = 200.0
        elif idade_meses < 6:
            crescimento = 50.0
        else:
            crescimento = 20.0
    else:
        get_dri = -69.15 + (80.00 * idade_anos_decimal) + (2.65 * altura) + (54.15 * peso)
        if idade_meses < 3:
            crescimento = 180.0
        elif idade_meses < 6:
            crescimento = 60.0
        elif idade_meses < 12:
            crescimento = 20.0
        else:
            crescimento = 15.0

    eer_dri = get_dri + crescimento
    return {
        "get": get_dri,
        "crescimento": crescimento,
        "eer": eer_dri,
        "eer_kg": eer_dri / peso if peso > 0 else 0.0
    }


# ==========================================
# LÓGICA MATEMÁTICA SILENCIOSA DO TETO (A -> G)
# ==========================================
def calcular_aplv_matematica(idade_meses, tipo_formula, freq_usuario):
    """
    Engenharia reversa do teto PAPLVRO.

    O teto é definido em gramas de pó. A energia máxima é calculada diretamente
    pela densidade energética do PÓ (kcal/100 g). O volume exibido é o volume
    FINAL da preparação pronta, calculado pela densidade da preparação
    reconstituída (kcal/100 mL).

    A água necessária à reconstituição é calculada separadamente e fica disponível
    apenas para a memória de cálculo.
    """
    dados = tradutor_sesau[tipo_formula]

    A = obter_teto_latas(idade_meses, tipo_formula)
    B = 400.0
    C = A * B
    D = C / 30.0
    X = freq_usuario

    # Quantidade de pó no teto
    E = D / X if X > 0 else 0.0

    # Energia do teto: calculada diretamente pelas kcal/100 g do pó
    G = (D * dados["kcal_100g"]) / 100.0

    # Volume FINAL da preparação pronta
    F_total = (
        (G * 100.0) / dados["kcal_100ml"]
        if dados["kcal_100ml"] > 0 else 0.0
    )
    F = F_total / X if X > 0 else 0.0

    # Água de reconstituição: somente para memória de cálculo
    agua_dia = (
        (D / dados["peso_medida"]) * dados["vol_agua"]
        if dados["peso_medida"] > 0 else 0.0
    )
    agua_porcao = agua_dia / X if X > 0 else 0.0

    return {
        "latas": A,
        "g_mes": C,
        "g_dia": D,
        "freq": X,
        "g_porcao": E,
        "ml_porcao": F,
        "ml_dia": F_total,
        "kcal_formula": G,
        "agua_dia": agua_dia,
        "agua_porcao": agua_porcao,
        "kcal_100g": dados["kcal_100g"],
        "kcal_100ml": dados["kcal_100ml"],
    }


def calcular_prescricao_por_vet(vet_kcal, idade_meses, tipo_formula, freq_usuario):
    """
    Converte o VET adotado em quantidade de fórmula e aplica o teto PAPLVRO
    como limite absoluto.

    REGRA MATEMÁTICA:
      1) kcal da fórmula = VET - alimentação complementar de referência;
      2) gramas de pó = kcal da fórmula / (kcal por grama de pó);
      3) aplica-se o teto mensal em gramas;
      4) após eventual limitação, recalculam-se as kcal efetivas da fórmula;
      5) volume em mL = volume FINAL da preparação pronta, usando kcal/100 mL;
      6) água necessária à reconstituição é calculada separadamente e usada
         somente na memória de cálculo.
    """
    dados = tradutor_sesau[tipo_formula]
    teto_latas = obter_teto_latas(idade_meses, tipo_formula)
    teto_g_mes = teto_latas * 400.0
    comp = obter_desconto_alimentacao_complementar(idade_meses)

    kcal_formula_teorica = max(vet_kcal - comp, 0.0)

    # Quantidade de pó necessária pelas kcal/100 g do produto
    g_dia = (
        (kcal_formula_teorica * 100.0) / dados["kcal_100g"]
        if dados["kcal_100g"] > 0 else 0.0
    )
    g_mes = g_dia * 30.0

    limitado_teto = g_mes > teto_g_mes

    if limitado_teto:
        g_mes = teto_g_mes
        g_dia = g_mes / 30.0

    # Energia REAL fornecida pela quantidade de pó efetivamente calculada
    kcal_formula = (g_dia * dados["kcal_100g"]) / 100.0

    # Volume FINAL da fórmula preparada
    ml_dia = (
        (kcal_formula * 100.0) / dados["kcal_100ml"]
        if dados["kcal_100ml"] > 0 else 0.0
    )

    # Água para reconstituição — somente para memória
    agua_dia = (
        (g_dia / dados["peso_medida"]) * dados["vol_agua"]
        if dados["peso_medida"] > 0 else 0.0
    )

    X = freq_usuario
    g_porcao = g_dia / X if X > 0 else 0.0
    ml_porcao = ml_dia / X if X > 0 else 0.0
    agua_porcao = agua_dia / X if X > 0 else 0.0

    equiv_latas = g_mes / 400.0 if g_mes > 0 else 0.0
    latas_solicitadas = min(math.ceil(equiv_latas), teto_latas) if teto_latas > 0 else 0

    return {
        "latas": latas_solicitadas,
        "equiv_latas": equiv_latas,
        "teto_latas": teto_latas,
        "g_mes": g_mes,
        "g_dia": g_dia,
        "freq": X,
        "g_porcao": g_porcao,
        "ml_porcao": ml_porcao,
        "ml_dia": ml_dia,
        "kcal_formula": kcal_formula,
        "kcal_comp": comp,
        "kcal_comp_real": max(vet_kcal - kcal_formula, 0.0),
        "limitado_teto": limitado_teto,
        "agua_dia": agua_dia,
        "agua_porcao": agua_porcao,
        "kcal_100g": dados["kcal_100g"],
        "kcal_100ml": dados["kcal_100ml"],
    }


# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
_, main_col, _ = st.columns([0.5, 9, 0.5])

with main_col:
    st.markdown("<h1>🧮 Calculadora Clínica APLV</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5A7260; font-size:1.1rem; margin-top:-0.5rem;'>Insira os dados biométricos para gerar a tabela exata e as métricas do laudo oficial da SESAU-RO.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # ENTRADA DE DADOS (ZERADOS)
    st.header("1. Dados Biométricos")
    with st.container():
        c1, c2, c3, c4, c5 = st.columns(5)
        data_nasc = c1.date_input("Data de Nascimento", value=None, format="DD/MM/YYYY")
        data_aval = c2.date_input("Data da Avaliação", value=None, format="DD/MM/YYYY")
        sexo = c3.selectbox("Sexo", ["Masculino", "Feminino"], index=None, placeholder="Selecione...")
        peso = c4.number_input("Peso (kg)", min_value=0.0, value=None, step=0.1, format="%.3f")
        altura = c5.number_input("Estatura (cm)", min_value=0.0, value=None, step=1.0, format="%.1f")

    # LÓGICA DE PREENCHIMENTO AUTOMÁTICO REVERSO E PROTEÍNAS IOM
    default_kcal = None
    default_ptn = None
    default_freq = 6
    idade_meses = 0
    limite_kcal_teto = None
    vet_maximo_teto = None
    fator_referencia = None

    st.header("2. Prescrição e Requerimentos")
    with st.container():
        c6, c7, c8, c9 = st.columns([2, 1, 1, 1])
        formula_selecionada = c6.selectbox("Fórmula (Protocolo SESAU)", list(tradutor_sesau.keys()), index=None, placeholder="Escolha uma opção")

        if data_nasc is not None and data_aval is not None and sexo is not None and peso is not None:
            idade_meses = (data_aval.year - data_nasc.year) * 12 + (data_aval.month - data_nasc.month)
            if data_aval.day < data_nasc.day: idade_meses -= 1
            idade_meses = max(0, idade_meses)
            
            # Frequência sugerida pela idade (Baseado no estudo de Alimentação Responsiva)
            if idade_meses < 1: default_freq = 8
            elif idade_meses < 4: default_freq = 6
            elif idade_meses < 6: default_freq = 5
            elif idade_meses < 9: default_freq = 4
            else: default_freq = 3
            
            # Necessidades de Proteína Recomendada (IOM, 2005)
            if idade_meses < 6: default_ptn = 1.52
            elif idade_meses < 12: default_ptn = 1.20
            else: default_ptn = 1.05

            # A referência energética do Quadro 3 define o mínimo do VET.
            # A engenharia reversa continua calculando o teto da FÓRMULA, mas não pode
            # reduzir o VET total abaixo da necessidade energética de referência.
            # Assim: VET >= GET, enquanto a quantidade de fórmula continua limitada
            # pelo teto mensal do PAPLVRO dentro de calcular_prescricao_por_vet().
            fator_referencia = obter_fator_energia_paplvro(idade_meses, sexo)

            if formula_selecionada is not None and peso > 0:
                calc_temp = calcular_aplv_matematica(idade_meses, formula_selecionada, default_freq)
                kcal_max_formula = calc_temp['kcal_formula']
                comp = obter_desconto_alimentacao_complementar(idade_meses)
                vet_maximo_teto = kcal_max_formula + comp
                limite_kcal_teto = vet_maximo_teto / peso

                # Nunca iniciar com VET inferior ao GET de referência.
                # Se o teto da fórmula + AC permitir valor maior, preservamos o maior valor.
                default_kcal = max(fator_referencia, limite_kcal_teto)
            elif peso > 0:
                default_kcal = fator_referencia

        if formula_selecionada is not None and data_nasc is not None and data_aval is not None:
            classe_sel = tradutor_sesau[formula_selecionada].get("classe")
            if classe_sel == "FS" and idade_meses < 6:
                st.warning("⚠️ O PAPLVRO não prevê fórmula de soja para menores de 6 meses.")
            if classe_sel == "FSL" and 12 <= idade_meses <= 24:
                st.caption("ℹ️ Para FSL, o protocolo informa dispensação conforme FEH/FAA. Como os tetos divergem entre 12–24 meses, o sistema usa 6 latas (critério conservador da FEH).")

        if limite_kcal_teto is not None and limite_kcal_teto > 0:
            # Em menores de 6 meses, a fórmula deve contemplar 100% das necessidades;
            # portanto, o teto energético da fórmula também funciona como máximo do VET.
            if idade_meses < 6:
                fator_kcal = c7.number_input(
                    "Kcal/kg peso/dia",
                    min_value=float(fator_referencia),
                    max_value=float(max(limite_kcal_teto, fator_referencia)),
                    value=float(min(default_kcal, max(limite_kcal_teto, fator_referencia))),
                    step=1.0,
                    format="%.1f",
                    help=(
                        f"Referência do Quadro 3: {fator_referencia:.1f} kcal/kg/dia. "
                        f"Teto energético da fórmula: {limite_kcal_teto:.1f} kcal/kg/dia."
                    )
                )
            else:
                # Após 6 meses, o teto limita a quantidade de FÓRMULA, não o VET total.
                # Energia adicional pode ser completada pela alimentação complementar.
                fator_kcal = c7.number_input(
                    "Kcal/kg peso/dia",
                    min_value=float(fator_referencia),
                    value=float(default_kcal),
                    step=1.0,
                    format="%.1f",
                    help=(
                        f"Referência mínima do Quadro 3: {fator_referencia:.1f} kcal/kg/dia. "
                        f"O teto da fórmula equivale a {limite_kcal_teto:.1f} kcal/kg/dia "
                        "quando somado à alimentação complementar de referência, mas limita "
                        "somente a fórmula — não reduz o VET total."
                    )
                )
        else:
            fator_kcal = c7.number_input(
                "Kcal/kg peso/dia",
                min_value=float(fator_referencia) if fator_referencia is not None else 0.0,
                value=default_kcal,
                step=1.0,
                format="%.1f"
            )
        fator_ptn = c8.number_input("g PTN/kg peso/dia", min_value=0.0, value=default_ptn, step=0.1, format="%.2f")
        frequencia = c9.number_input("Ofertas/dia", min_value=1, value=default_freq, step=1)

    st.markdown("---")

    # RESULTADOS - SÓ RENDERIZA SE TIVER TUDO PREENCHIDO
    if data_nasc and data_aval and sexo and peso and altura and formula_selecionada and fator_kcal and fator_ptn and frequencia:
        
        vet_kcal = peso * fator_kcal
        
        # GET de referência do laudo: fator energético do Quadro 3 × peso atual.
        # O VET não pode ficar abaixo deste valor. O teto administrativo permanece
        # aplicado exclusivamente à quantidade de fórmula.
        fator_get = obter_fator_energia_paplvro(idade_meses, sexo)
        get_kcal = peso * fator_get

        # Salvaguarda lógica: com o campo kcal/kg limitado inferiormente ao fator
        # de referência, esta condição não deve ocorrer. Mantida por segurança.
        if vet_kcal < get_kcal:
            vet_kcal = get_kcal
            fator_kcal = fator_get

        # Teto e prescrição são calculados separadamente.
        calc_teto = calcular_aplv_matematica(idade_meses, formula_selecionada, frequencia)
        calc = calcular_prescricao_por_vet(vet_kcal, idade_meses, formula_selecionada, frequencia)

        idade_anos_decimal = (data_aval - data_nasc).days / 365.2425
        dri = calcular_dri_2023(idade_meses, idade_anos_decimal, sexo, peso, altura)
        percentual_vet_formula = (calc['kcal_formula'] / vet_kcal * 100.0) if vet_kcal > 0 else 0.0

        imc_calc = peso / ((altura/100.0) ** 2) if altura > 0 else 0
        
        # Uso do z-score oficial com base na tabela da SESAU
        sexo_letra = 'M' if sexo == 'Masculino' else 'F'
        z_peso = calcular_escore_z_oms('peso', sexo_letra, idade_meses, peso)
        z_altura = calcular_escore_z_oms('altura', sexo_letra, idade_meses, altura)
        z_imc = calcular_escore_z_oms('imc', sexo_letra, idade_meses, imc_calc)
        
        str_peso = classificar_peso_sesau(z_peso)
        str_altura = classificar_altura_sesau(z_altura)
        str_imc = classificar_imc_sesau(z_imc)
        
        info_form = tradutor_sesau[formula_selecionada]
        codigo_ses = info_form["codigo"]
        desc_oficial = info_form["desc"]

        st.header("3. Resultados Clínicos e Matemáticos")

        # AVISO DE IDADE DA GENE-SESAU pelo aniversário exato de 2 anos.
        data_limite_paplvro = adicionar_anos(data_nasc, 2)
        if data_aval > data_limite_paplvro:
            st.warning("⚠️ **Atenção:** A criança possui mais de 24 meses (2 anos). De acordo com o regulamento do PAPLVRO (GENE-SESAU), ela não atende ao critério de idade para a dispensação destas fórmulas infantis.")

        if calc['limitado_teto']:
            st.warning("⚠️ O VET informado exigiria quantidade superior ao teto mensal do PAPLVRO. A quantidade de fórmula foi automaticamente limitada ao máximo permitido pelo protocolo.")

        col_esq, col_dir = st.columns([1, 1])

        with col_esq:
            # Cálculo exato da idade em Anos, Meses e Dias
            anos_i = data_aval.year - data_nasc.year
            meses_i = data_aval.month - data_nasc.month
            dias_i = data_aval.day - data_nasc.day
            if dias_i < 0:
                meses_i -= 1
                dias_i += (data_aval.replace(day=1) - datetime.timedelta(days=1)).day
            if meses_i < 0:
                anos_i -= 1
                meses_i += 12
                
            partes = []
            if anos_i > 0: partes.append(f"{anos_i} ano{'s' if anos_i > 1 else ''}")
            if meses_i > 0: partes.append(f"{meses_i} {'meses' if meses_i > 1 else 'mês'}")
            if dias_i > 0 or not partes: partes.append(f"{dias_i} dia{'s' if dias_i > 1 else ''}")
            str_idade = " e ".join([", ".join(partes[:-1]), partes[-1]] if len(partes) > 1 else partes)

            st.markdown('<div class="card-estudo"><h4>📋 AVALIAÇÃO NUTRICIONAL (OMS)</h4>', unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>Idade:</b> {str_idade}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>Peso:</b> {peso:.3f} kg | <b>Altura:</b> {altura:.0f} cm</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>IMC (kg/m²):</b> {imc_calc:.2f}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 15px 0; border-top: 1px dashed #C4C7B6;'>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>A/I:</b> {str_altura}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>P/I:</b> {str_peso}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>IMC/I:</b> {str_imc}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_dir:
            st.markdown('<div class="card-estudo"><h4>🧮 RACIONAL MATEMÁTICO (A → G)</h4>', unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>A)</b> Teto p/ idade/classe: <b>{calc_teto['latas']}</b> latas/mês</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>B)</b> Gramas p/ lata: <b>400g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>C)</b> Teto Mês (A × B): <b>{calc_teto['g_mes']:.0f}g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>D)</b> Teto Dia (C ÷ 30): <b>{calc_teto['g_dia']:.1f}g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>X)</b> Frequência: <b>{calc['freq']}x ao dia</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>E)</b> Pó p/ mamadeira: <b>{calc['g_porcao']:.2f}g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>F)</b> Vol. final preparado/mamadeira: <b>{calc['ml_porcao']:.1f} mL</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>G)</b> Kcal diárias na fórmula: <b>{calc['kcal_formula']:.1f} kcal</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag' style='margin-top:10px;'><b>Solicitação calculada:</b> {calc['g_mes']:.0f}g/mês ({calc['equiv_latas']:.2f} latas eq.) → <b>{calc['latas']} lata(s)</b></p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.header("4. Espelho do Laudo - Tabela Oficial")

        # CAIXAS DE SELEÇÃO PARA AS OPÇÕES 2 E 3
        st.markdown("<p style='color:#5A7260; font-size:0.95rem; margin-top:-0.5rem;'>Adicionar fórmulas alternativas à tabela (Opcional):</p>", unsafe_allow_html=True)
        c_f2, c_f3 = st.columns(2)
        formula_2 = c_f2.selectbox("Opção 2", list(tradutor_sesau.keys()), index=None, placeholder="Escolha uma opção")
        formula_3 = c_f3.selectbox("Opção 3", list(tradutor_sesau.keys()), index=None, placeholder="Escolha uma opção")
        
# FUNÇÃO FANTASMA SÓ PARA A TABELA (MEMÓRIA AMPLIADA E ESTILIZADA)
        def gerar_memoria_formula_html(info_formula, calc_formula, calc_formula_teto, vet_base):
            perc_formula = (
                (calc_formula["kcal_formula"] / vet_base) * 100.0
                if vet_base > 0 else 0.0
            )
            perc_outros = max(100.0 - perc_formula, 0.0)
            kcal_outros = max(vet_base - calc_formula["kcal_formula"], 0.0)

            status_teto = (
                "LIMITADO PELO TETO"
                if calc_formula["limitado_teto"]
                else "DENTRO DO TETO"
            )
            status_class = "mem-inline-status alerta" if calc_formula["limitado_teto"] else "mem-inline-status ok"

            return f"""
            <details class="mem-inline">
                <summary>
                    <span class="mem-inline-icon">🧮</span>
                    <span>Ver memória de cálculo</span>
                    <span class="{status_class}">{status_teto}</span>
                </summary>

                <div class="mem-inline-body">
                    <div class="mem-inline-grid">
                        <div class="mem-inline-card">
                            <span>Diluição padrão</span>
                            <strong>{info_formula["peso_medida"]:.1f} g / {info_formula["vol_agua"]:.0f} mL água</strong>
                        </div>
                        <div class="mem-inline-card">
                            <span>Teto PAPLVRO</span>
                            <strong>{calc_formula_teto["latas"]} × 400 g</strong>
                        </div>
                        <div class="mem-inline-card">
                            <span>Quantidade calculada</span>
                            <strong>{calc_formula["g_mes"]:.0f} g/mês</strong>
                        </div>
                        <div class="mem-inline-card">
                            <span>Solicitação</span>
                            <strong>{calc_formula["latas"]} lata(s)</strong>
                        </div>
                    </div>

                    <div class="mem-inline-section">
                        <div class="mem-inline-title">Energia</div>
                        <div class="mem-inline-row">
                            <span>VET utilizado</span>
                            <b>{vet_base:.1f} kcal/d</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Energia da fórmula</span>
                            <b>{calc_formula["kcal_formula"]:.1f} kcal/d</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Densidade do pó</span>
                            <b>{info_formula["kcal_100g"]:.0f} kcal/100 g</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Densidade preparada</span>
                            <b>{info_formula["kcal_100ml"]:.0f} kcal/100 mL</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>% do VET pela fórmula</span>
                            <b>{perc_formula:.1f}%</b>
                        </div>
                        <div class="mem-inline-equation">
                            ({calc_formula["kcal_formula"]:.1f} ÷ {vet_base:.1f}) × 100 = {perc_formula:.1f}%
                        </div>
                        <div class="mem-inline-note">
                            Restante do VET: {kcal_outros:.1f} kcal/d ({perc_outros:.1f}%).
                        </div>
                    </div>

                    <div class="mem-inline-section">
                        <div class="mem-inline-title">Quantidade diária e por oferta</div>
                        <div class="mem-inline-row">
                            <span>Pó por dia</span>
                            <b>{calc_formula["g_dia"]:.2f} g</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Volume final preparado por dia</span>
                            <b>{calc_formula["ml_dia"]:.1f} mL</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Água para reconstituição</span>
                            <b>{calc_formula["agua_dia"]:.1f} mL/dia</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Frequência</span>
                            <b>{calc_formula["freq"]}x/dia</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Por oferta (volume final)</span>
                            <b>{calc_formula["g_porcao"]:.2f} g / {calc_formula["ml_porcao"]:.1f} mL</b>
                        </div>
                        <div class="mem-inline-row">
                            <span>Água/oferta (memória)</span>
                            <b>{calc_formula["agua_porcao"]:.1f} mL</b>
                        </div>
                    </div>

                    <div class="mem-inline-footer">
                        <b>Conferência:</b> {calc_formula["equiv_latas"]:.2f} lata(s) equivalente(s)
                        de 400 g calculadas, com teto de {calc_formula_teto["latas"]}.
                    </div>
                </div>
            </details>
            """

        def gerar_linha_extra(form_nome):
            if not form_nome:
                return '<tr><td style="height: 35px;"></td><td></td><td></td></tr>'

            calc_e = calcular_prescricao_por_vet(vet_kcal, idade_meses, form_nome, frequencia)
            calc_e_teto = calcular_aplv_matematica(idade_meses, form_nome, frequencia)
            info_e = tradutor_sesau[form_nome]

            memoria_html = gerar_memoria_formula_html(
                info_e,
                calc_e,
                calc_e_teto,
                vet_kcal
            )

            return f'<tr><td><strong>{info_e["codigo"]}</strong> - {info_e["desc"]}{memoria_html}</td><td>{calc_e["g_dia"]:.2f}g / {calc_e["ml_dia"]:.1f} ml</td><td>x 30 = {calc_e["g_mes"]:.0f}g / {(calc_e["ml_dia"]*30):.1f} ml<br><span style="color:#555; font-size:11px;">({calc_e["latas"]} latas)</span></td></tr>'

        linha_2 = gerar_linha_extra(formula_2)
        linha_3 = gerar_linha_extra(formula_3)

        # Memória estilizada da fórmula principal
        memoria_principal_html = gerar_memoria_formula_html(
            info_form,
            calc,
            calc_teto,
            vet_kcal
        )

        # CONSTRUÇÃO DA TABELA HTML IDÊNTICA AO WORD
        html_tabela = f"""
        <div class="tabela-container">
            <table class="tabela-laudo">
                <tr>
                    <td>GET (kcal): {get_kcal:.0f}</td>
                    <td>VET (kcal): {vet_kcal:.0f}</td>
                    <td>Obs.: EER DRI 2023: {dri['eer']:.0f} kcal/d</td>
                </tr>
                <tr>
                    <td>Kcal/kg peso/dia: {fator_kcal:.1f}</td>
                    <td colspan="2">g PTN/kg peso/dia: {fator_ptn:.2f}g</td>
                </tr>
                <tr class="bg-gray">
                    <td style="width: 50%;">Código(s) SES – Descrição da Fórmula</td>
                    <td style="width: 25%;">Quantidade/dia (g/mL)</td>
                    <td style="width: 25%;">Quantidade/mês (g/mL)</td>
                </tr>
                <!-- LINHA TRADUZIDA AUTOMATICAMENTE -->
                <tr>
                    <td>
                        <strong>{codigo_ses}</strong> - {desc_oficial}
                        {memoria_principal_html}
                    </td>
                    <td>{calc['g_dia']:.2f}g / {calc['ml_dia']:.1f} ml</td>
                    <td>x 30 = {calc['g_mes']:.0f}g / {(calc['ml_dia']*30):.1f} ml<br><span style="color:#555; font-size:11px;">({calc['latas']} latas)</span></td>
                </tr>
                <!-- OPÇÕES ADICIONAIS -->
                {linha_2}
                {linha_3}
                <tr>
                    <td>Frasco</td>
                    <td></td>
                    <td>x 30 = </td>
                </tr>
                <tr>
                    <td>Equipo</td>
                    <td></td>
                    <td>x 30 = </td>
                </tr>
                <tr>
                    <td>% VET fórmula: {percentual_vet_formula:.1f}%</td>
                    <td>Diluição (g/porção): {calc['g_porcao']:.2f}g</td>
                    <td>Volume final/porção (mL): {calc['ml_porcao']:.1f}ml</td>
                </tr>
                <tr>
                    <td colspan="3">Nº porções/dia: {calc['ml_porcao']:.1f}ml / {calc['freq']}X/dia.</td>
                </tr>
            </table>
        </div>
        """
        
        st.components.v1.html(f"""
            <style>
                .tabela-container {{
                    background-color: #FFFFFF;
                    padding: 5px;
                    border-radius: 12px;
                    font-family: 'Inter', sans-serif;
                }}
                .tabela-laudo {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                    color: #111111;
                }}
                .tabela-laudo td, .tabela-laudo th {{
                    border: 1px solid #222222;
                    padding: 8px 12px;
                    vertical-align: middle;
                    line-height: 1.4;
                }}
                .bg-gray {{
                    background-color: #F4F4F4;
                    font-weight: 600;
                    text-align: center;
                }}

                /* Memória de cálculo dentro da tabela */
                .mem-inline {{
                    margin-top: 10px;
                }}
                .mem-inline summary {{
                    list-style: none;
                    display: flex;
                    align-items: center;
                    gap: 7px;
                    width: fit-content;
                    padding: 6px 9px;
                    background: #F4F8F4;
                    border: 1px solid #DCE7DD;
                    border-radius: 8px;
                    color: #2D5A34;
                    cursor: pointer;
                    font-weight: 700;
                    font-size: 12px;
                    transition: all .15s ease;
                }}
                .mem-inline summary::-webkit-details-marker {{
                    display: none;
                }}
                .mem-inline summary:hover {{
                    background: #EAF2EB;
                    border-color: #C6D8C8;
                }}
                .mem-inline-icon {{
                    font-size: 13px;
                }}
                .mem-inline-status {{
                    margin-left: 3px;
                    padding: 2px 6px;
                    border-radius: 999px;
                    font-size: 9px;
                    letter-spacing: .03em;
                    font-weight: 800;
                }}
                .mem-inline-status.ok {{
                    background: #E7F2E6;
                    color: #35653A;
                }}
                .mem-inline-status.alerta {{
                    background: #FFF1D8;
                    color: #8A5A11;
                }}
                .mem-inline-body {{
                    margin-top: 8px;
                    padding: 12px;
                    background: linear-gradient(145deg, #FBFCFB 0%, #F1F6F2 100%);
                    border: 1px solid #DDE7DE;
                    border-left: 4px solid #859B48;
                    border-radius: 9px;
                    color: #243528;
                }}
                .mem-inline-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                    gap: 7px;
                    margin-bottom: 9px;
                }}
                .mem-inline-card {{
                    background: #FFFFFF;
                    border: 1px solid #E1E8E2;
                    border-radius: 7px;
                    padding: 8px 9px;
                }}
                .mem-inline-card span {{
                    display: block;
                    color: #748077;
                    font-size: 9.5px;
                    font-weight: 600;
                    margin-bottom: 3px;
                }}
                .mem-inline-card strong {{
                    display: block;
                    color: #203A25;
                    font-size: 11.5px;
                }}
                .mem-inline-section {{
                    background: rgba(255,255,255,.78);
                    border: 1px solid #E1E8E2;
                    border-radius: 7px;
                    padding: 9px 10px;
                    margin-top: 7px;
                }}
                .mem-inline-title {{
                    color: #2D5A34;
                    font-size: 10px;
                    text-transform: uppercase;
                    letter-spacing: .06em;
                    font-weight: 800;
                    margin-bottom: 6px;
                }}
                .mem-inline-row {{
                    display: flex;
                    justify-content: space-between;
                    gap: 10px;
                    padding: 3px 0;
                    border-bottom: 1px dashed #E7ECE7;
                    font-size: 10.5px;
                }}
                .mem-inline-row:last-of-type {{
                    border-bottom: none;
                }}
                .mem-inline-row span {{
                    color: #617066;
                }}
                .mem-inline-row b {{
                    color: #1E3823;
                    white-space: nowrap;
                }}
                .mem-inline-equation {{
                    margin-top: 6px;
                    padding: 6px 7px;
                    border-radius: 6px;
                    background: #F1F4F1;
                    color: #304534;
                    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                    font-size: 9.8px;
                }}
                .mem-inline-note {{
                    margin-top: 5px;
                    color: #66746A;
                    font-size: 9.7px;
                }}
                .mem-inline-footer {{
                    margin-top: 8px;
                    padding-top: 7px;
                    border-top: 1px solid #DCE5DD;
                    color: #526358;
                    font-size: 10px;
                }}
            </style>
            {html_tabela}
        """, height=420, scrolling=True)
        
        # Conferência científica discreta; não altera o cálculo oficial do PAPLVRO.
        with st.expander("📚 Conferência científica — DRI 2023 (não altera o teto PAPLVRO)", expanded=False):
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("GET / TEE", f"{dri['get']:.0f} kcal/d")
            d2.metric("Crescimento", f"+{dri['crescimento']:.0f} kcal/d")
            d3.metric("EER", f"{dri['eer']:.0f} kcal/d")
            d4.metric("EER/kg", f"{dri['eer_kg']:.1f} kcal/kg/d")

            vet_teto_atual = calc_teto['kcal_formula'] + obter_desconto_alimentacao_complementar(idade_meses)
            st.caption(
                f"PAPLVRO/FAO-WHO: {get_kcal:.0f} kcal/d · "
                f"VET adotado: {vet_kcal:.0f} kcal/d · "
                f"Referência fórmula no teto + AC: {vet_teto_atual:.0f} kcal/d."
            )

            if dri['eer'] > vet_teto_atual:
                st.warning(
                    f"A EER estimada pela DRI 2023 ({dri['eer']:.0f} kcal/d) é superior ao "
                    f"valor de referência fórmula no teto + AC ({vet_teto_atual:.0f} kcal/d). "
                    "Use a diferença como sinal para avaliação clínica, evolução antropométrica "
                    "e adequação da alimentação complementar; o teto PAPLVRO permanece inalterado."
                )
            else:
                st.success("A EER estimada pela DRI 2023 não supera a referência formada pela fórmula no teto + alimentação complementar para a fórmula selecionada.")

        # Memória explicativa dos cálculos usados para chegar ao resultado final.
        # É apenas uma conferência matemática e não altera nenhum valor da prescrição.
        with st.expander("🧮 Memória de cálculo — como chegamos a este resultado", expanded=False):
            comp_calculo = obter_desconto_alimentacao_complementar(idade_meses)
            kcal_formula_teorica = max(vet_kcal - comp_calculo, 0.0)
            kcal_formula_final = calc["kcal_formula"]
            kcal_nao_formula = max(vet_kcal - kcal_formula_final, 0.0)
            percentual_nao_formula = (
                (kcal_nao_formula / vet_kcal) * 100.0
                if vet_kcal > 0 else 0.0
            )

            st.markdown(
                f"""
                <div class="memoria-resumo">
                    <div class="memoria-resumo-titulo">Resumo do resultado calculado</div>
                    <div class="memoria-resumo-grid">
                        <div class="memoria-kpi">
                            <span>VET adotado</span>
                            <strong>{vet_kcal:.1f} kcal/d</strong>
                        </div>
                        <div class="memoria-kpi">
                            <span>Energia da fórmula</span>
                            <strong>{kcal_formula_final:.1f} kcal/d</strong>
                        </div>
                        <div class="memoria-kpi">
                            <span>% do VET pela fórmula</span>
                            <strong>{percentual_vet_formula:.1f}%</strong>
                        </div>
                        <div class="memoria-kpi">
                            <span>Solicitação mensal</span>
                            <strong>{calc["latas"]} lata(s)</strong>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="memoria-etapa">
                    <div class="memoria-numero">1</div>
                    <h5>VET adotado</h5>
                    <p>O VET parte do peso atual multiplicado pelo valor energético adotado em kcal/kg/dia.</p>
                    <div class="memoria-equacao">
                        VET = peso × kcal/kg/dia<br>
                        VET = {peso:.3f} kg × {fator_kcal:.1f} kcal/kg/dia<br>
                        <b>VET = {vet_kcal:.1f} kcal/dia</b>
                    </div>
                </div>

                <div class="memoria-etapa">
                    <div class="memoria-numero">2</div>
                    <h5>Parcela considerada para alimentação complementar</h5>
                    <p>Para a faixa etária atual, o protocolo usa <b>{comp_calculo:.0f} kcal/dia</b> como referência inicial de alimentação complementar. Se a fórmula atingir o teto, o restante necessário do VET passa a ser mostrado como contribuição complementar residual.</p>
                    <div class="memoria-equacao">
                        kcal destinadas inicialmente à fórmula = VET − alimentação complementar<br>
                        = {vet_kcal:.1f} − {comp_calculo:.1f}<br>
                        <b>= {kcal_formula_teorica:.1f} kcal/dia</b>
                    </div>
                </div>

                <div class="memoria-etapa">
                    <div class="memoria-numero">3</div>
                    <h5>Conferência com o teto PAPLVRO</h5>
                    <p>O teto quantitativo usado no cálculo é de <b>{calc_teto["latas"]} lata(s) equivalentes de 400 g/mês</b>,
                    totalizando {calc_teto["g_mes"]:.0f} g/mês.</p>
                    <div class="memoria-equacao">
                        Teto energético da fórmula = <b>{calc_teto["kcal_formula"]:.1f} kcal/dia</b><br>
                        Quantidade efetivamente calculada = <b>{calc["g_mes"]:.1f} g/mês</b>
                        ({calc["equiv_latas"]:.2f} lata(s) equivalente(s))
                    </div>
                    <div class="{"memoria-alerta" if calc["limitado_teto"] else "memoria-destaque"}">
                        {"A necessidade teórica ultrapassaria o teto; o cálculo final foi limitado ao quantitativo máximo permitido." if calc["limitado_teto"] else "A quantidade calculada cabe dentro do teto quantitativo configurado."}
                    </div>
                </div>

                <div class="memoria-etapa">
                    <div class="memoria-numero">4</div>
                    <h5>% do VET proveniente da fórmula</h5>
                    <p>Esta é a conferência que relaciona diretamente a energia da fórmula com o VET total.</p>
                    <div class="memoria-equacao">
                        % VET fórmula = (kcal da fórmula ÷ VET) × 100<br>
                        = ({kcal_formula_final:.1f} ÷ {vet_kcal:.1f}) × 100<br>
                        <b>= {percentual_vet_formula:.1f}%</b><br><br>
                        Conferência inversa:<br>
                        {percentual_vet_formula:.1f}% de {vet_kcal:.1f} kcal =
                        <b>{kcal_formula_final:.1f} kcal/dia</b>
                    </div>
                    <div class="memoria-destaque">
                        O restante corresponde a <b>{kcal_nao_formula:.1f} kcal/dia</b>
                        ({percentual_nao_formula:.1f}% do VET).
                    </div>
                </div>

                <div class="memoria-etapa">
                    <div class="memoria-numero">5</div>
                    <h5>Conversão das kcal da fórmula em pó</h5>
                    <p>A quantidade de pó é calculada diretamente pelo valor energético do produto em <b>kcal/100 g</b>, sem usar o volume de água como se fosse volume final.</p>
                    <div class="memoria-equacao">
                        Densidade do pó = {info_form["kcal_100g"]:.0f} kcal/100 g<br>
                        pó/dia = kcal da fórmula × 100 ÷ kcal/100 g<br>
                        = {kcal_formula_final:.1f} × 100 ÷ {info_form["kcal_100g"]:.0f}<br>
                        <b>= {calc["g_dia"]:.2f} g/dia</b><br><br>
                        pó/mês = {calc["g_dia"]:.2f} × 30 =
                        <b>{calc["g_mes"]:.1f} g/mês</b>
                    </div>
                </div>

                <div class="memoria-etapa">
                    <div class="memoria-numero">6</div>
                    <h5>Volume final da preparação pronta</h5>
                    <p>O volume usado no laudo é o <b>volume final da fórmula preparada</b>, calculado pela densidade energética da preparação pronta em kcal/100 mL. O volume de água aparece abaixo apenas como conferência de reconstituição.</p>
                    <div class="memoria-equacao">
                        Densidade preparada = {info_form["kcal_100ml"]:.0f} kcal/100 mL<br>
                        volume final/dia = kcal da fórmula × 100 ÷ kcal/100 mL<br>
                        = {kcal_formula_final:.1f} × 100 ÷ {info_form["kcal_100ml"]:.0f}<br>
                        <b>= {calc["ml_dia"]:.1f} mL/dia de fórmula pronta</b><br><br>

                        Água para reconstituição (somente conferência):<br>
                        relação do fabricante = {info_form["peso_medida"]:.2f} g de pó para {info_form["vol_agua"]:.0f} mL de água<br>
                        água/dia = ({calc["g_dia"]:.2f} ÷ {info_form["peso_medida"]:.2f}) × {info_form["vol_agua"]:.0f}<br>
                        <b>= {calc["agua_dia"]:.1f} mL de água/dia</b>
                    </div>
                </div>

                <div class="memoria-etapa">
                    <div class="memoria-numero">7</div>
                    <h5>Latas e divisão por ofertas</h5>
                    <p>A quantidade mensal é convertida em equivalentes de 400 g e depois dividida pela frequência escolhida.</p>
                    <div class="memoria-equacao">
                        latas equivalentes = {calc["g_mes"]:.1f} ÷ 400 =
                        <b>{calc["equiv_latas"]:.2f}</b><br>
                        solicitação arredondada = <b>{calc["latas"]} lata(s)</b>
                        (teto: {calc_teto["latas"]})<br><br>
                        pó/oferta = {calc["g_dia"]:.2f} ÷ {calc["freq"]} =
                        <b>{calc["g_porcao"]:.2f} g</b><br>
                        volume final/oferta = {calc["ml_dia"]:.1f} ÷ {calc["freq"]} =
                        <b>{calc["ml_porcao"]:.1f} mL de fórmula pronta</b><br>
                        água/oferta (somente memória) = {calc["agua_dia"]:.1f} ÷ {calc["freq"]} =
                        <b>{calc["agua_porcao"]:.1f} mL de água</b><br><br>
                        Conferência do volume final:<br>
                        {calc["ml_porcao"]:.2f} mL × {calc["freq"]} =
                        <b>{(calc["ml_porcao"] * calc["freq"]):.2f} mL/dia</b>
                        ≈ {calc["ml_dia"]:.1f} mL/dia
                    </div>
                </div>

                <div class="memoria-destaque" style="margin-top:14px;">
                    <b>Esta área é somente uma conferência matemática.</b>
                    Ela não modifica VET, teto, fórmula selecionada ou quantidade do laudo.
                </div>
                """,
                unsafe_allow_html=True
            )

        # ==========================================
        # 5. ASSISTENTE CLÍNICO DE TRIAGEM (CDSS)
        # ==========================================
        st.markdown("---")
        st.header("5. Assistente Clínico de Escolha (GENE-SESAU)")
        st.markdown("<p style='color:#5A7260; font-size:1.05rem; margin-top:-0.5rem;'>Sugestão automática de fórmula baseada nos Quadros 6 e 7 do protocolo estadual.</p>", unsafe_allow_html=True)

        with st.expander("🩺 Abrir Triagem Diagnóstica", expanded=False):
            c_diag1, c_diag2 = st.columns(2)
            
            mecanismo = c_diag1.selectbox(
                "Mecanismo da Alergia / Condição",
                ["Selecione...", "APLV - Mediada por IgE", "APLV - Não mediada por IgE", "Intolerância à Lactose (Confirmada)"]
            )
            
            sintomas_graves = c_diag2.radio(
                "Sintomas Graves? (Anafilaxia, Enterocolite, Síndrome de Heiner, etc.)",
                ["Não", "Sim"]
            )

            sintomas_gastro = "Não"
            baixo_risco_anafilaxia = "Sim"

            if mecanismo == "APLV - Mediada por IgE" and 6 <= idade_meses <= 24 and sintomas_graves == "Não":
                c_soja1, c_soja2 = st.columns(2)
                sintomas_gastro = c_soja1.radio("Há sintomas gastrointestinais?", ["Não", "Sim"], horizontal=True)
                baixo_risco_anafilaxia = c_soja2.radio("Baixo risco de reação anafilática?", ["Sim", "Não"], horizontal=True)

            if mecanismo != "Selecione...":
                st.markdown("<br><h5>🎯 Recomendação Oficial do Protocolo</h5>", unsafe_allow_html=True)
                
                # Regra 1: Intolerância à Lactose (Quadro 6)
                if mecanismo == "Intolerância à Lactose (Confirmada)":
                    st.info("**1ª Escolha:** Fórmula infantil sem lactose (FSL - Cód: 264)\n\n💡 *Considere utilizar o leite: Aptamil SL (Sem Lactose)*\n\n*Indicação:* Dor abdominal, inchaço, flatulência, diarreia. Confirmada por exames.")
                
                # Regra 2: Sintomas Graves/Anafilaxia (Sempre FAA - Quadro 6 e 7)
                elif sintomas_graves == "Sim":
                    st.error("**1ª Escolha:** Fórmula infantil à base de aminoácidos livres (FAA - Cód: 274)\n\n💡 *Considere utilizar o leite: Neocate LCP*\n\n*Nota:* As FAA devem ser a primeira escolha em casos graves independentemente da faixa etária.")
                
                # Regra 3: Menores de 6 meses (Quadro 7)
                elif idade_meses < 6:
                    st.success("**1ª Opção:** Fórmula c/ proteína extensamente hidrolisada (FEH - Cód: 261)\n💡 *Considere utilizar o leite: Pregomin Pepti*\n\n**2ª Opção:** Fórmula c/ aminoácidos livres (FAA - Cód: 274)\n💡 *Considere utilizar o leite: Neocate LCP*")
                
                # Regra 4: De 6 a 24 meses (Quadro 7)
                elif idade_meses >= 6 and idade_meses <= 24:
                    if mecanismo == "APLV - Não mediada por IgE":
                        st.success("**1ª Opção:** Fórmula c/ proteína extensamente hidrolisada (FEH - Cód: 261)\n💡 *Considere utilizar o leite: Pregomin Pepti*\n\n**2ª Opção:** Fórmula c/ aminoácidos livres (FAA - Cód: 274)\n💡 *Considere utilizar o leite: Neocate LCP*")
                    elif mecanismo == "APLV - Mediada por IgE":
                        if sintomas_gastro == "Não" and baixo_risco_anafilaxia == "Sim":
                            st.success("**1ª Opção:** Fórmula à base de soja (FS - Cód: 272)\n💡 *Considere utilizar o leite: Aptamil Soja 2*\n\n**2ª Opção:** Fórmula c/ proteína extensamente hidrolisada (FEH - Cód: 261)\n💡 *Considere utilizar o leite: Pregomin Pepti*\n\n**3ª Opção:** Fórmula c/ aminoácidos livres (FAA - Cód: 274)\n💡 *Considere utilizar o leite: Neocate LCP*\n\n*Nota:* FS prevista para maiores de 6 meses, APLV mediada por IgE, sem sintomas gastrointestinais e com baixo risco de reação anafilática.")
                        else:
                            st.warning("**A fórmula de soja não é priorizada com os critérios informados.**\n\n**1ª Opção:** Fórmula c/ proteína extensamente hidrolisada (FEH - Cód: 261)\n💡 *Considere utilizar o leite: Pregomin Pepti*\n\n**2ª Opção:** Fórmula c/ aminoácidos livres (FAA - Cód: 274)\n💡 *Considere utilizar o leite: Neocate LCP*")
                
                # Regra 5: Acima de 24 meses (Fallback)
                else:
                    st.warning("Paciente acima de 24 meses. Avaliar desmame ou necessidade de fórmulas específicas de seguimento.\n\n💡 *Considere utilizar o leite: Neocate Advance (Acima de 1 ano)*")
        
    else:
        st.markdown("<p class='aviso-vazio'>Preencha todos os campos biométricos e selecione a fórmula para gerar a tabela de prescrição do laudo.</p>", unsafe_allow_html=True)
