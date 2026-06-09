import streamlit as st

# 1. CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="NutriAPS | Home", layout="wide", initial_sidebar_state="expanded")

# 2. INJEÇÃO DE CSS GLOBAL
def injetar_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1D361F !important; }

        /* Proteção dos ícones */
        .material-icons, .material-symbols-rounded,
        [data-testid*="Icon"], [data-testid*="Icon"] *,
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="collapsedControl"] *, [class*="icon"] {
            font-family: "Material Symbols Rounded", "Material Icons" !important;
        }

        .main { background-color: #ECE5DF !important; padding: 2rem !important; }
        [data-testid="stAppViewContainer"] { background-color: #ECE5DF !important; }

        /* ===================== SIDEBAR (TEMA CLARO & ELEGANTE) ===================== */
        [data-testid="stSidebar"] {
            background-color: #F7F9F7 !important; /* Fundo super claro */
            border-right: 1px solid #E2EBE3 !important; /* Borda sutil */
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }
        [data-testid="stSidebarNav"] { display: none !important; }

        .sidebar-logo {
            padding: 2rem 1.4rem 1.4rem 1.4rem;
            border-bottom: 1px solid #E2EBE3;
            margin-bottom: 1.4rem;
        }
        .sidebar-logo .logo-title {
            font-size: 1.3rem; font-weight: 700; color: #1D361F; letter-spacing: -0.02em;
        }
        .sidebar-logo .logo-sub {
            font-size: 0.75rem; color: #5A7260; margin-top: 0.2rem;
        }

        .nav-group-label {
            font-size: 0.65rem; font-weight: 700; letter-spacing: 0.10em;
            text-transform: uppercase; color: #859B48;
            padding: 0 1.4rem; margin-bottom: 0.4rem;
        }

        [data-testid="stSidebar"] [data-testid="stPageLink"] { margin: 0 0.7rem 0.15rem 0.7rem !important; }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a {
            display: flex !important; align-items: center !important; gap: 0.55rem !important;
            padding: 0.6rem 0.85rem !important; border-radius: 9px !important;
            font-size: 0.88rem !important; font-weight: 600 !important;
            color: #2D5A34 !important; text-decoration: none !important;
            transition: background 0.15s ease, color 0.15s ease !important;
            background: transparent !important;
        }
        [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: #E8F0E9 !important; color: #1D361F !important;
        }

        /* --- FIX DEFINITIVO DO FOOTER DA SIDEBAR (MÁGICA DO FLEXBOX) --- */
        [data-testid="stSidebarUserContent"] {
            display: flex !important;
            flex-direction: column !important;
            min-height: 92vh !important; /* Força o contêiner a esticar verticalmente */
        }
        
        .sidebar-footer {
            margin-top: auto !important; /* Empurra o elemento para a base do contêiner flexível */
            text-align: center !important;
            font-size: 0.68rem !important;
            color: #8A9A8E !important;
            line-height: 1.6 !important;
            padding-bottom: 1rem !important;
        }

        /* ===================== HERO BANNER ===================== */
        .hero-banner {
            background: linear-gradient(135deg, #2D5A34 0%, #4A8C55 60%, #6BAF76 100%);
            border-radius: 20px; padding: 2.8rem 3rem; margin-bottom: 2rem;
            display: flex; flex-direction: column; gap: 0.5rem;
            box-shadow: 0 8px 24px rgba(45, 90, 52, 0.15);
        }
        .hero-banner h1 { color: white !important; font-size: 2.2rem; margin: 0; letter-spacing: -0.03em; }
        .hero-banner p { color: rgba(255,255,255,0.85) !important; font-size: 1.05rem; margin: 0; max-width: 520px; }
        .hero-badge {
            display: inline-block; background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.3); border-radius: 999px;
            padding: 0.25rem 0.9rem; font-size: 0.78rem; font-weight: 600;
            color: white !important; letter-spacing: 0.04em;
            margin-bottom: 0.8rem; width: fit-content;
        }

        /* ===================== CARDS CLICÁVEIS ===================== */
        a.card-link {
            text-decoration: none !important;
            display: block;
            height: 100%;
        }
        .card-wrapper {
            background: #FDFAF7;
            border: 1px solid rgba(45, 90, 52, 0.12);
            border-radius: 16px;
            padding: 1.8rem 1.8rem 1.6rem 1.8rem;
            transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
            box-shadow: 0 2px 8px rgba(45, 90, 52, 0.08);
            height: 100%;
            position: relative;
        }
        
        a.card-link:hover .card-wrapper {
            box-shadow: 0 10px 28px rgba(45, 90, 52, 0.15);
            transform: translateY(-3px);
            border-color: rgba(45, 90, 52, 0.3);
        }
        
        .card-icon { font-size: 2.2rem; margin-bottom: 0.8rem; display: block; }
        .card-title { font-size: 1.1rem; font-weight: 700; color: #1D361F; margin-bottom: 0.5rem; }
        .card-desc { font-size: 0.88rem; color: #5A7260; line-height: 1.55; }
        .card-tags { margin-top: 1.1rem; display: flex; flex-wrap: wrap; gap: 0.4rem; }
        .tag {
            background: #E8F0E9; color: #2D5A34; border-radius: 999px;
            padding: 0.2rem 0.7rem; font-size: 0.74rem; font-weight: 600;
        }
        
        .card-arrow {
            position: absolute; bottom: 1.1rem; right: 1.3rem;
            font-size: 1.2rem; color: rgba(45, 90, 52, 0.35);
            transition: color 0.2s ease, transform 0.2s ease;
        }
        a.card-link:hover .card-arrow {
            color: #2D5A34; transform: translate(2px, -2px);
        }

        /* ===================== INSTRUÇÃO ===================== */
        .instrucao-box {
            background: rgba(45, 90, 52, 0.07); border-left: 4px solid #4A8C55;
            border-radius: 0 12px 12px 0; padding: 1rem 1.4rem;
            margin-top: 1.8rem; font-size: 0.92rem; color: #2D5A34;
        }

        h1, h2, h3 { color: #1D361F !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
        </style>
    """, unsafe_allow_html=True)

injetar_css()

# Limpar memória ao acessar a Home
if "current_module" not in st.session_state or st.session_state["current_module"] != "home":
    st.session_state.clear()
    st.session_state["current_module"] = "home"

# ==========================================
# SIDEBAR (CLEAN THEME)
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

    # Rodapé perfeitamente isolado e empurrado pelo Flexbox
    st.markdown("""
        <div class="sidebar-footer">
            NutriAPS · v1.0<br>
            Residência Multiprofissional<br>
            Atenção Básica - 2026
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
_, main_col, _ = st.columns([0.5, 9, 0.5])

with main_col:

    # --- HERO ---
    st.markdown("""
        <div class="hero-banner">
            <span class="hero-badge">APS · Atenção Primária à Saúde</span>
            <h1>🍏 NutriAPS</h1>
            <p>Sistema integrado de avaliação nutricional e planejamento clínico para a Atenção Básica de Buritis-RO.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- TÍTULO DA SEÇÃO ---
    st.markdown("#### Módulos disponíveis")
    st.markdown(
        "<p style='color:#5A7260; font-size:0.9rem; margin-top:-0.5rem; margin-bottom:1.4rem;'>"
        "Clique em um módulo para iniciar o atendimento.</p>",
        unsafe_allow_html=True
    )

    # --- CARDS CLICÁVEIS NATIVOS ---
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
            <a href="Populacao_Geral" target="_self" class="card-link">
                <div class="card-wrapper">
                    <span class="card-icon">👥</span>
                    <div class="card-title">População Geral</div>
                    <div class="card-desc">
                        Avaliação antropométrica de adultos, cálculo de gasto energético total (GET),
                        rastreio nutricional (PRAR) e prescrição de dietas personalizadas.
                    </div>
                    <div class="card-tags">
                        <span class="tag">Antropometria</span>
                        <span class="tag">GET</span>
                        <span class="tag">PRAR</span>
                        <span class="tag">Dieta</span>
                    </div>
                    <span class="card-arrow">↗</span>
                </div>
            </a>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <a href="Gestantes" target="_self" class="card-link">
                <div class="card-wrapper">
                    <span class="card-icon">🤰</span>
                    <div class="card-title">Gestantes</div>
                    <div class="card-desc">
                        Acompanhamento obstétrico completo com curva de ganho de peso gestacional
                        (Padrão MS 2026), gestão de DMG/HAS e diário clínico por consulta.
                    </div>
                    <div class="card-tags">
                        <span class="tag">Ganho de Peso</span>
                        <span class="tag">Curva MS 2026</span>
                        <span class="tag">DMG · HAS</span>
                        <span class="tag">Diário Clínico</span>
                    </div>
                    <span class="card-arrow">↗</span>
                </div>
            </a>
        """, unsafe_allow_html=True)

    # --- INSTRUÇÃO ---
    st.markdown("""
        <div class="instrucao-box">
            💡 <strong>Como usar:</strong> clique em qualquer card acima ou use o <strong>menu lateral</strong> para navegar.
            Ao retornar à Home, os dados do atendimento anterior são limpos automaticamente.
        </div>
    """, unsafe_allow_html=True)