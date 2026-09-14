import streamlit as st
import datetime
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
        "desc": "Fórmula infantil extensamente hidrolisada para lactentes de primeira infância, com alergia à proteína do leite de vaca ou de soja e distúrbios absortivos.",
        "peso_medida": 4.3, "vol_agua": 30.0
    },
    "Aptamil SL (Sem Lactose)": {
        "codigo": "264",
        "desc": "Fórmula infantil sem lactose (FSL).",
        "peso_medida": 4.3, "vol_agua": 30.0
    },
    "Neocate LCP (Até 3 anos)": {
        "codigo": "274",
        "desc": "Fórmula Infantil à base de aminoácidos para crianças de primeira infância, isenta de proteína láctea, lactose (sem lactose adicionada), sacarose, galactose, frutose e glúten.",
        "peso_medida": 4.6, "vol_agua": 30.0
    },
    "Aptamil Soja 1 (0 a 6 meses)": {
        "codigo": "272",
        "desc": "Fórmula infantil de seguimento à base de soja, isenta de lactose e glúten, isenta de lactose e glúten(com DHA e ARA). Fase 1.",
        "peso_medida": 4.6, "vol_agua": 30.0
    },
    "Aptamil Soja 2 (A partir 6 meses)": {
        "codigo": "272",
        "desc": "Fórmula infantil de seguimento à base de soja, isenta de lactose e glúten, isenta de lactose e glúten(com DHA e ARA). Fase 2.",
        "peso_medida": 4.7, "vol_agua": 30.0
    },
    "Neocate Advance (Acima 1 ano)": {
        "codigo": "258",
        "desc": "Dieta pediátrica para nutrição enteral à base de aminoácidos livres com restrição de lactose, para crianças de segunda e terceira infância.",
        "peso_medida": 25.0, "vol_agua": 85.0
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
# LÓGICA MATEMÁTICA SILENCIOSA (A -> G)
# ==========================================
def calcular_aplv_matematica(idade_meses, tipo_formula):
    dados = tradutor_sesau[tipo_formula]
    
    if idade_meses < 3: A = 9
    elif idade_meses < 6: A = 10
    elif idade_meses < 9: A = 8
    elif idade_meses < 12: A = 7
    else: A = 7 if "Neocate" in tipo_formula else 6

    B = 400
    C = A * B
    D = C / 30.0

    if idade_meses < 1: X = 8
    elif idade_meses < 4: X = 6
    elif idade_meses < 6: X = 5
    elif idade_meses < 9: X = 4
    else: X = 3

    E = D / X
    F = (E * dados["vol_agua"]) / dados["peso_medida"]
    F_total = F * X
    G = (F_total * 69.0) / 100.0

    return {
        "latas": A, "g_mes": C, "g_dia": D, "freq": X, 
        "g_porcao": E, "ml_porcao": F, "ml_dia": F_total, "kcal_formula": G
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
        sexo = c3.selectbox("Sexo", [None, "Masculino", "Feminino"], index=0)
        peso = c4.number_input("Peso (kg)", min_value=0.0, value=None, step=0.1, format="%.3f")
        altura = c5.number_input("Estatura (cm)", min_value=0.0, value=None, step=1.0, format="%.1f")

    # LÓGICA DE PREENCHIMENTO AUTOMÁTICO REVERSO E PROTEÍNAS IOM
    default_kcal = None
    default_ptn = None
    idade_meses = 0

    st.header("2. Prescrição e Requerimentos")
    with st.container():
        c6, c7, c8 = st.columns([2, 1, 1])
        formula_selecionada = c6.selectbox("Fórmula (Protocolo SESAU)", list(tradutor_sesau.keys()), index=None)

        if data_nasc is not None and data_aval is not None and sexo is not None and peso is not None:
            idade_meses = (data_aval.year - data_nasc.year) * 12 + (data_aval.month - data_nasc.month)
            if data_aval.day < data_nasc.day: idade_meses -= 1
            idade_meses = max(0, idade_meses)
            
            # Necessidades de Proteína Recomendada (IOM, 2005)
            if idade_meses < 6: default_ptn = 1.52
            elif idade_meses < 12: default_ptn = 1.20
            else: default_ptn = 1.05

            # Engenharia Reversa do Kcal/kg peso/dia com base no máximo de latas permitidas
            if formula_selecionada is not None and peso > 0:
                calc_temp = calcular_aplv_matematica(idade_meses, formula_selecionada)
                kcal_max_formula = calc_temp['kcal_formula']
                
                # Desconto de Alimentação Complementar (CONITEC)
                if idade_meses < 6: comp = 0
                elif idade_meses < 8: comp = 200
                elif idade_meses < 12: comp = 300
                else: comp = 550
                
                vet_maximo = kcal_max_formula + comp
                default_kcal = vet_maximo / peso
            elif peso > 0:
                # Fallback genérico caso a fórmula ainda não tenha sido escolhida (FAO/WHO 2004)
                is_masc = (sexo == "Masculino")
                if idade_meses < 3: default_kcal = 105.0 if is_masc else 100.0
                elif idade_meses < 6: default_kcal = 81.0 if is_masc else 83.0
                elif idade_meses < 9: default_kcal = 79.0 if is_masc else 78.0
                elif idade_meses < 12: default_kcal = 80.0 if is_masc else 79.0
                else: default_kcal = 83.0 if is_masc else 80.0

        fator_kcal = c7.number_input("Kcal/kg peso/dia", min_value=0.0, value=default_kcal, step=1.0, format="%.1f")
        fator_ptn = c8.number_input("g PTN/kg peso/dia", min_value=0.0, value=default_ptn, step=0.1, format="%.2f")

    st.markdown("---")

    # RESULTADOS - SÓ RENDERIZA SE TIVER TUDO PREENCHIDO
    if data_nasc and data_aval and sexo and peso and altura and formula_selecionada and fator_kcal and fator_ptn:
        
        vet_kcal = peso * fator_kcal
        
        # GET Independente (Schofield 0-3 anos * Fator de Atividade 1.5)
        if sexo == 'Masculino':
            get_kcal = ((59.512 * peso) - 30.4) * 1.5
        else:
            get_kcal = ((58.317 * peso) - 31.1) * 1.5
        get_kcal = get_kcal if get_kcal > 0 else 0
        
        calc = calcular_aplv_matematica(idade_meses, formula_selecionada)
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
        col_esq, col_dir = st.columns([1, 1])

        with col_esq:
            st.markdown('<div class="card-estudo"><h4>📋 AVALIAÇÃO NUTRICIONAL (OMS)</h4>', unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>Idade:</b> {idade_meses} meses</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>Peso:</b> {peso:.3f} kg | <b>Altura:</b> {altura:.0f} cm</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>IMC (kg/m²):</b> {imc_calc:.2f}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 15px 0; border-top: 1px dashed #C4C7B6;'>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>A/I:</b> {str_altura}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>P/I:</b> {str_peso}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='linha-info'><b>IMC/I:</b> {str_imc}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_dir:
            st.markdown('<div class="card-estudo"><h4>🧮 RACIONAL MATEMÁTICO (A → G)</h4>', unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>A)</b> Latas p/ idade: <b>{calc['latas']}</b> latas/mês</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>B)</b> Gramas p/ lata: <b>400g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>C)</b> Total Mês (A × B): <b>{calc['g_mes']:.0f}g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>D)</b> Total Dia (C ÷ 30): <b>{calc['g_dia']:.1f}g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>X)</b> Frequência: <b>{calc['freq']}x ao dia</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>E)</b> Pó p/ mamadeira (D ÷ X): <b>{calc['g_porcao']:.2f}g</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>F)</b> Vol. Água p/ mamadeira: <b>{calc['ml_porcao']:.0f} mL</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p class='passo-ag'><b>G)</b> Kcal diárias na fórmula: <b>{calc['kcal_formula']:.1f} kcal</b></p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.header("4. Espelho do Laudo - Tabela Oficial")
        # CONSTRUÇÃO DA TABELA HTML IDÊNTICA AO WORD
        html_tabela = f"""
        <div class="tabela-container">
            <table class="tabela-laudo">
                <tr>
                    <td>GET (kcal): {get_kcal:.0f}</td>
                    <td>VET (kcal): {vet_kcal:.0f}</td>
                    <td>Obs.: </td>
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
                    <td><strong>{codigo_ses}</strong> - {desc_oficial}</td>
                    <td>{calc['g_dia']:.2f}g / {calc['ml_dia']:.0f} ml</td>
                    <td>x 30 = {calc['g_mes']:.0f}g / {(calc['ml_dia']*30):.0f} ml<br><span style="color:#555; font-size:11px;">({calc['latas']} latas)</span></td>
                </tr>
                <!-- LINHAS VAZIAS PADRÃO DO MODELO -->
                <tr>
                    <td style="height: 35px;"></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td style="height: 35px;"></td>
                    <td></td>
                    <td></td>
                </tr>
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
                    <td>% VET fórmula: {calc['kcal_formula']:.2f}</td>
                    <td>Diluição (g/porção): {calc['g_porcao']:.2f}g</td>
                    <td>Volume final/porção (mL): {calc['ml_porcao']:.0f}ml</td>
                </tr>
                <tr>
                    <td colspan="3">Nº porções/dia: {calc['ml_porcao']:.0f}ml / {calc['freq']}X/dia.</td>
                </tr>
            </table>
        </div>
        """
        
        st.markdown(html_tabela, unsafe_allow_html=True)
        
    else:
        st.markdown("<p class='aviso-vazio'>Preencha todos os campos biométricos e selecione a fórmula para gerar a tabela de prescrição do laudo.</p>", unsafe_allow_html=True)