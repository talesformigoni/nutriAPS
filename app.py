import streamlit as st

# 1. CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="NutriAPS | Home", layout="wide", initial_sidebar_state="expanded")

# 2. INJEÇÃO DE CSS GLOBAL
def injetar_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1D361F !important; }
                /* --- FIX DO MENU LATERAL (Protege os ícones do Streamlit) --- */
        i, .material-symbols-rounded, [data-testid="stSidebarCollapseButton"] span, [data-testid="stSidebarCollapseButton"] svg { 
        font-family: "Material Symbols Rounded", "Material Icons" !important; 
        }
        .main { background-color: #ECE5DF !important; padding: 2rem !important; }
        [data-testid="stAppViewContainer"] { background-color: #ECE5DF !important; }
        [data-testid="stSidebar"] { background-color: #DFC8B6 !important; border-right: 1px solid #C4C7B6; box-shadow: 2px 0 10px rgba(0,0,0,0.02); }
        [data-testid="stSidebarNav"] { padding-top: 2rem; }
        h1, h2, h3 { color: #1D361F !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
        </style>
    """, unsafe_allow_html=True)

injetar_css()

# REGRA DE OURO: Limpar a memória ao acessar a Home
if "current_module" not in st.session_state or st.session_state["current_module"] != "home":
    st.session_state.clear()
    st.session_state["current_module"] = "home"

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
main_col_1, main_col_2, main_col_3 = st.columns([1, 8, 1])

with main_col_2:
    st.title("🍏 Mapa de Saúde Nutricional")
    st.markdown("<p style='font-size: 1.2rem; color: #1D361F; opacity: 0.8;'>Sistema Integrado de Avaliação Nutricional e Planejamento Clínico</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    ### Bem-vindo ao Sistema!
    Utilize o **menu lateral à esquerda** para navegar entre os módulos do sistema:

    * **👥 População Geral:** Avaliação de adultos, cálculo de GET, rastreio PRAR e prescrição de dietas.
    * **🤰 Gestantes:** Acompanhamento obstétrico, curva de Atalah, gestão de DMG/HAS e diário clínico.
    
    *Selecione um módulo na barra lateral para iniciar o atendimento.*
    """)