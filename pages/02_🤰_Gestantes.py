import streamlit as st
import math
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

from nutri_calc import avaliar_gestante_ms2026
from nutri_pdf import gerar_pdf_gestante
from nutri_ia import gerar_cardapio_ia

st.set_page_config(page_title="Gestantes | NutriAPS", layout="wide")

# REGRA DE OURO DO MULTIPÁGINAS
if "current_module" not in st.session_state or st.session_state["current_module"] != "gestante":
    st.session_state.clear()
    st.session_state["current_module"] = "gestante"

# INJEÇÃO DE CSS PADRONIZADO (TEMA CLARO + FLEXBOX FOOTER)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1D361F !important; }
    
    /* --- PROTEÇÃO ABSOLUTA DE ÍCONES --- */
    .material-icons, 
    .material-symbols-rounded, 
    [data-testid*="Icon"], 
    [data-testid*="Icon"] *, 
    [data-testid="stSidebarCollapseButton"] *, 
    [data-testid="collapsedControl"] *,
    [class*="icon"] {
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
        margin-top: auto !important; /* Empurra o texto pro fundo */
        text-align: center !important;
        font-size: 0.68rem !important;
        color: #8A9A8E !important;
        line-height: 1.6 !important;
        padding-bottom: 1rem !important;
    }

    /* ===================== ESTILOS ESPECÍFICOS DA PÁGINA ===================== */
    h1, h2, h3 { color: #1D361F !important; font-weight: 700 !important; }
    h1 { font-size: 2.2rem !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.5rem !important; margin-top: 1rem !important; margin-bottom: 1.2rem !important; border-bottom: 2px solid #C4C7B6; padding-bottom: 10px; }
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6q9sum, .st-emotion-cache-ocquxy { background-color: #DFC8B6 !important; border-radius: 16px !important; padding: 20px !important; border: 1px solid rgba(196, 199, 182, 0.5) !important; box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important; }
    [data-testid="InputInstructions"] { display: none !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] { background-color: #F7F3F0 !important; border: 1px solid #C4C7B6 !important; border-radius: 10px !important; height: 45px !important; }
    .stTextInput input:focus, .stNumberInput input:focus { border-color: #859B48 !important; box-shadow: 0 0 0 3px rgba(133, 155, 72, 0.1) !important; }
    .stButton button { background-color: #859B48 !important; color: #FFFFFF !important; border: none !important; border-radius: 12px !important; padding: 0.6rem 1.5rem !important; font-weight: 600 !important; width: 100% !important; text-transform: uppercase; }
    .stButton button:hover { background-color: #1D361F !important; color: #FFFFFF !important; transform: translateY(-2px); }
    [data-testid="stMetric"] { background-color: #FFFFFF !important; border-radius: 12px !important; padding: 15px 20px !important; border: 1px solid #C4C7B6 !important; }
    [data-testid="stMetricValue"] { color: #859B48 !important; font-weight: 700 !important; }
    .stTabs [data-baseweb="tab"] { background-color: #DFC8B6 !important; border-radius: 10px 10px 0 0 !important; color: #1D361F !important; font-weight: 600 !important; border: 1px solid #C4C7B6 !important; }
    .stTabs [aria-selected="true"] { background-color: #859B48 !important; color: white !important; border-color: #859B48 !important; }
    .laudo-box { background-color: #FFFFFF; padding: 2rem; border-radius: 16px; border: 1px solid #C4C7B6; border-top: 6px solid #859B48; margin-top: 20px; }
    .stSlider div[data-baseweb="slider"] div[aria-hidden="true"] { display: none !important; }
    .stSlider div[data-baseweb="slider"] [role="slider"] { background-color: #859B48 !important; box-shadow: 0 0 0 5px rgba(133, 155, 72, 0.25) !important; border: none !important; }
    .stProgress > div > div > div > div { background-color: #859B48 !important; }
    hr { border-top: 1px solid #C4C7B6 !important; opacity: 0.5; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR PADRONIZADA
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
main_col_1, main_col_2, main_col_3 = st.columns([1, 8, 1])

with main_col_2:
    st.title("Atendimento: Pré-Natal (Gestante)")
    st.markdown("---")

    st.header("1. Dados Obstétricos")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo da Gestante", placeholder="Ex: Maria da Silva")
            idade = st.number_input("Idade (anos)", min_value=10, max_value=60, value=25, step=1)
            col_sub_sem, col_sub_dias = st.columns(2)
            with col_sub_sem:
                ig_semanas = st.number_input("Idade Gestacional (Semanas)", min_value=6, max_value=42, value=20, step=1)
            with col_sub_dias:
                ig_dias = st.number_input("Dias (Opcional)", min_value=0, max_value=6, value=0, step=1)
            semana_gestacional = ig_semanas + 1 if ig_dias >= 4 else ig_semanas
            
        with col2:
            altura = st.number_input("Altura (cm)", min_value=100, max_value=220, value=160, step=1)
            peso_atual = st.number_input("Peso Atual na Consulta (kg)", min_value=30.0, max_value=250.0, value=64.0, step=0.1)
            peso_pre_input = st.number_input("Peso Pré-Gestacional (kg) [Opcional - Deixe 0.0]", min_value=0.0, max_value=200.0, value=0.0, step=0.1)
        
        # --- RASTREIO DE DIABETES GESTACIONAL E HAS ---
        st.markdown("<br><p style='font-size: 15px; margin-bottom: 5px; color: #859B48;'><b>🩸 Rastreio e Condições Clínicas (SBD/MS):</b></p>", unsafe_allow_html=True)
        
        with st.expander("Inserir Exames Glicêmicos (Jejum e TOTG 75g)"):
            st.caption("Preencha os valores disponíveis para rastreio automático.")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                glicemia_jejum = st.number_input("Glicemia de Jejum (mg/dL)", min_value=0, max_value=400, value=0, step=1, help="Geralmente feita na 1ª consulta ou 3º trimestre.")
            with col_ex2:
                st.write("TOTG 75g (24 a 28 semanas):")
                totg_jejum = st.number_input("Jejum (mg/dL)", min_value=0, max_value=400, value=0, step=1, key="totg_j")
                totg_1h = st.number_input("1 hora após (mg/dL)", min_value=0, max_value=400, value=0, step=1, key="totg_1")
                totg_2h = st.number_input("2 horas após (mg/dL)", min_value=0, max_value=400, value=0, step=1, key="totg_2")

        # Algoritmo de Diagnóstico de DMG
        diagnostico_dmg = "Sem rastreio"
        is_dmg = False
        alerta_dmg = ""

        if glicemia_jejum > 0 or totg_jejum > 0 or totg_1h > 0 or totg_2h > 0:
            # Regras TOTG 75g
            if (totg_jejum >= 126) or (totg_2h >= 200):
                diagnostico_dmg = "DM Prévio na Gravidez"
                alerta_dmg = "Atenção: Valores indicam Diabetes Mellitus prévio. Encaminhar para Alto Risco (PNAR)."
                is_dmg = True
            elif (92 <= totg_jejum <= 125) or (totg_1h >= 180) or (153 <= totg_2h <= 199):
                diagnostico_dmg = "DMG Confirmado (TOTG)"
                alerta_dmg = "Diabetes Mellitus Gestacional diagnosticado via TOTG. Iniciar controle não farmacológico."
                is_dmg = True
            # Regras Jejum isolado
            elif glicemia_jejum >= 126:
                diagnostico_dmg = "DM Prévio na Gravidez"
                alerta_dmg = "Atenção: Glicemia de jejum indica Diabetes Mellitus prévio. Encaminhar ao PNAR."
                is_dmg = True
            elif 92 <= glicemia_jejum <= 125:
                diagnostico_dmg = "DMG Confirmado (Jejum)"
                alerta_dmg = "Diabetes Mellitus Gestacional diagnosticado. Iniciar MEV e controle de peso."
                is_dmg = True
            else:
                diagnostico_dmg = "Glicemia Normal"

        if is_dmg:
            st.error(f"🩸 {diagnostico_dmg} | {alerta_dmg}")
        elif diagnostico_dmg == "Glicemia Normal":
            st.success("🩸 Exames dentro da normalidade (< 92 mg/dL no jejum).")

        # Mantendo o HAS manual por enquanto
        is_has = st.checkbox("🫀 Hipertensão Arterial (HAS) / Pré-eclâmpsia")

        if altura > 0 and peso_atual > 0:
            # 1. Nova Chamada MS 2026
            res_gest = avaliar_gestante_ms2026(peso_atual, altura, semana_gestacional, peso_pre_input)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. EXIBIÇÃO DINÂMICA DE CARDS (Padrão MS 2026)
            if peso_pre_input > 0.0:
                m1, m2, m3, m4 = st.columns(4)
                with m1: st.metric("IMC Pré", f"{res_gest['imc_pre']:.1f} kg/m²")
                with m2: st.metric("Classificação", res_gest['classificacao_pre'])
                with m3: st.metric("Ganho Atual", f"{res_gest['ganho_atual']:.1f} kg")
                with m4: st.metric("Meta Total", f"{res_gest['meta_total_min']} a {res_gest['meta_total_max']} kg")
            else:
                m1, m2, m3 = st.columns(3)
                with m1: st.metric("IMC (Base)", f"{res_gest['imc_pre']:.1f} kg/m²")
                with m2: st.metric("Classificação", res_gest['classificacao_pre'])
                with m3: st.metric("Meta Total*", f"{res_gest['meta_total_min']} a {res_gest['meta_total_max']} kg", help="Meta calculada com base no peso da consulta atual.")

            # 3. Laudo Dinâmico
            laudo_gest_html = f"""
            <div class="laudo-box" style="border-top-color: #859B48;">
                <h3 style="color: #1D361F; margin-top: 0;">Diagnóstico Nutricional Obstétrico</h3>
                <p style="margin-bottom:8px;"><strong>Status do Ganho: <span style="color:#859B48;">{res_gest['status_ganho']}</span></strong></p>
                <p style="line-height:1.6; font-style: italic; color: #555;">"{res_gest['diagnostico']}"</p>
                <hr style="margin: 12px 0;">
                <h3 style="color: #859B48; margin-top: 0; font-size: 1.1rem;">Conduta e Orientação</h3>
                <p style="line-height:1.6; color: #1D361F;">{res_gest['conselho']}</p>
            </div>
            """
            st.markdown(laudo_gest_html, unsafe_allow_html=True)
            
            # 4. GRÁFICO OFICIAL PLOTLY (PADRÃO MS 2026)
            dados_ms = res_gest['dados_ms']
            perc = dados_ms['percentis']

            # --- pdf_mode vindo do session_state (False = tela colorida, True = PDF cinza) ---
            pdf_mode = st.session_state.get('pdf_mode', False)

            # --- Paleta de cores por classificação (tela) ou cinza (PDF) ---
            if not pdf_mode:
                if res_gest['classificacao_pre'] == "Baixo Peso":
                    c_fill = 'rgba(155, 89, 182, 0.25)'
                    c_safe = '#9C4BB5'
                    c_out  = '#7B2D8B'
                elif res_gest['classificacao_pre'] == "Eutrofia":
                    c_fill = 'rgba(46, 204, 113, 0.20)'
                    c_safe = '#2ECC71'
                    c_out  = '#1E7A3A'
                elif res_gest['classificacao_pre'] == "Sobrepeso":
                    c_fill = 'rgba(232, 98, 122, 0.20)'
                    c_safe = '#E8627A'
                    c_out  = '#C0392B'
                else:  # Obesidade
                    c_fill = 'rgba(230, 126, 34, 0.20)'
                    c_safe = '#F39C12'
                    c_out  = '#D35400'
            else:
                c_fill = 'rgba(200, 200, 200, 0.30)'
                c_safe = '#555555'
                c_out  = '#999999'

            x_vals = list(range(10, 41))

            fig = go.Figure()

            # --- Curvas dos percentis (ordem crescente para tonexty funcionar) ---
            keys_sorted = sorted(perc.keys(), key=lambda k: float(k.replace('P', '')))

            for k in keys_sorted:
                is_safe_boundary = (k == dados_ms["safe_min_key"] or k == dados_ms["safe_max_key"])

                line_color = c_safe if is_safe_boundary else c_out
                line_dash  = 'solid' if is_safe_boundary else 'dash'
                line_width = 2.5 if is_safe_boundary else 1.5

                fill_mode  = 'tonexty' if k == dados_ms["safe_max_key"] else 'none'
                fill_color = c_fill    if k == dados_ms["safe_max_key"] else 'rgba(0,0,0,0)'

                fig.add_trace(go.Scatter(
                    x=x_vals, y=perc[k],
                    mode='lines',
                    fill=fill_mode,
                    fillcolor=fill_color,
                    line=dict(color=line_color, width=line_width, dash=line_dash, shape='spline'),
                    name=k,
                    showlegend=False
                ))

                # Label do percentil à direita (semana 40)
                fig.add_annotation(
                    x=40.8, y=perc[k][-1],
                    text=f"<b>{k}</b>",
                    showarrow=False,
                    font=dict(color=line_color, size=10, family="Inter, sans-serif"),
                    xanchor="left",
                    yanchor="middle"
                )

            # --- Ponto da paciente atual ---
            marker_text = ["● Atual"] if pdf_mode else ["📍 Atual"]
            fig.add_trace(go.Scatter(
                x=[semana_gestacional],
                y=[res_gest['ganho_atual'] if peso_pre_input > 0 else None],
                mode='markers+text',
                text=marker_text,
                textposition="top center",
                marker=dict(color='#000000', size=10),
                name="Atual",
                showlegend=False
            ))

            # --- Linhas verticais dos trimestres ---
            fig.add_vline(x=13, line_width=1, line_dash="dash", line_color="rgba(120,120,120,0.5)")
            fig.add_vline(x=27, line_width=1, line_dash="dash", line_color="rgba(120,120,120,0.5)")

            # --- Barras coloridas dos trimestres abaixo do eixo X ---
            cor_trim = "gray" if pdf_mode else None
            fig.add_shape(type="line", x0=10, x1=13, y0=-10.3, y1=-10.3,
                          line=dict(color=cor_trim or "#9B59B6", width=4))
            fig.add_shape(type="line", x0=13.1, x1=27, y0=-10.3, y1=-10.3,
                          line=dict(color=cor_trim or "#5B9BD5", width=4))
            fig.add_shape(type="line", x0=27.1, x1=40, y0=-10.3, y1=-10.3,
                          line=dict(color=cor_trim or "#A8C8E8", width=4))

            # --- Labels dos trimestres ---
            for txt, xpos in [("1º Trimestre", 11.5), ("2º Trimestre", 20.5), ("3º Trimestre", 34.0)]:
                fig.add_annotation(
                    x=xpos, y=-10.0,
                    text=txt,
                    showarrow=False,
                    font=dict(color="gray", size=10, family="Inter, sans-serif"),
                    yanchor="bottom"
                )

            # --- Seta indicando direção do eixo X (modelo MS) ---
            fig.add_annotation(
                x=25, y=-11.0,
                text="◄──────── SEMANA DE GESTAÇÃO ────────►",
                showarrow=False,
                font=dict(color="gray", size=9),
                xanchor="center"
            )

            # --- Layout geral ---
            fig.update_layout(
                title=dict(
                    text=(
                        f"<b>GRÁFICO DE ACOMPANHAMENTO DO GANHO DE PESO</b><br>"
                        f"<sup><b>{res_gest['classificacao_pre'].upper()}</b> "
                        f"({dados_ms['limite_imc']})<br>"
                        f"GANHO DE PESO RECOMENDADO ATÉ 40 SEMANAS DE GESTAÇÃO: "
                        f"{dados_ms['rec_ganho']}</sup>"
                    ),
                    font=dict(size=13, family="Inter, sans-serif", color='#1D361F')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='#FFFFFF',
                font=dict(family="Inter, sans-serif"),
                xaxis=dict(
                    title="",
                    range=[9.5, 43],
                    dtick=1,
                    tick0=10,
                    tickmode='linear',
                    showgrid=True,
                    gridcolor='rgba(180, 180, 180, 0.5)',
                    gridwidth=0.8,
                    zeroline=False,
                    showline=True,
                    linecolor='rgba(180,180,180,0.8)'
                ),
                yaxis=dict(
                    title="GANHO DE PESO GESTACIONAL (kg)",
                    range=[-11.5, 25.5],
                    dtick=1,
                    showgrid=True,
                    gridcolor='rgba(180, 180, 180, 0.5)',
                    gridwidth=0.8,
                    zeroline=True,
                    zerolinecolor='rgba(120,120,120,0.6)',
                    zerolinewidth=1,
                    showline=True,
                    linecolor='rgba(180,180,180,0.8)'
                ),
                margin=dict(l=50, r=90, t=90, b=70)
            )

            # --- Fonte bibliográfica (fixada abaixo do gráfico via paper ref) ---
            fig.add_annotation(
                x=0, y=-0.20,
                xref="paper", yref="paper",
                text=(
                    "Fonte: KAC, G. <i>et al.</i> Gestational weight gain charts: results from the Brazilian "
                    "Maternal and Child Nutrition Consortium. <i>Am. J. Clin. Nutr.</i>, "
                    "v. 113, n. 5, p. 1351-1360, 2021. DOI: https://doi.org/10.1093/ajcn/nqaa402"
                ),
                showarrow=False,
                font=dict(size=7.5, color="gray", family="Inter, sans-serif"),
                xanchor="left",
                align="left"
            )

            st.plotly_chart(fig, use_container_width=True)
            
            # 5. O SESSION STATE CORRETO E COMPLETO
            st.session_state["dados_paciente"] = {
                "nome": nome, "idade": idade, "sexo": "Feminino", "peso": float(peso_atual), "altura": float(altura),
                "is_gestante": True, "semana": semana_gestacional, "res_gest": res_gest,
                "is_dmg": is_dmg, "is_has": is_has,
                "diagnostico_dmg": diagnostico_dmg,
                "alerta_dmg": alerta_dmg
            }
            
            st.markdown("<br>", unsafe_allow_html=True)
            pdf_bytes = gerar_pdf_gestante(st.session_state["dados_paciente"])
            
            if nome:
                st.download_button(
                    label="📥 Baixar Relatório Gestante (PDF)",
                    data=pdf_bytes,
                    file_name=f"Relatorio_Gestante_{nome}.pdf",
                    mime="application/pdf",
                    width="stretch" # <---- CORREÇÃO AQUI
                )
            else:
                st.info("Preencha o nome da gestante para liberar o download do PDF.")

    st.markdown("---")
    st.header("2. Planejamento de Cardápio (Gestante)")

    if "dados_paciente" not in st.session_state or st.session_state["dados_paciente"].get("is_gestante") == False:
        st.info("⚠️ Preencha os dados da gestante acima para liberar o cardápio.")
    else:
        dados = st.session_state["dados_paciente"]
        get_base = 2000.0

        if "kcal_alvo" not in st.session_state:
            st.session_state["kcal_alvo"] = get_base

        with st.container():
            st.markdown("### Configuração de Energia")
            e_col1, e_col2 = st.columns([3, 1])
            with e_col1:
                get_editavel = st.number_input("Definir Energia Alvo (kcal/dia)", min_value=800, max_value=5000, value=int(st.session_state["kcal_alvo"]), step=10)
            with e_col2:
                st.write(""); st.write("")
                if st.button("Resetar p/ Valor Base"):
                    st.session_state["kcal_alvo"] = get_base
                    st.rerun()

        get = st.session_state["kcal_alvo"]

        st.markdown("### Metas de Macronutrientes")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: perc_cho = st.slider("Carboidratos (%)", 30, 70, 50, 1)
        with col_m2: perc_ptn = st.slider("Proteínas (%)", 10, 50, 20, 1)
        with col_m3: perc_lip = st.slider("Lipídeos (%)", 10, 45, 30, 1)

        soma = perc_cho + perc_ptn + perc_lip
        if soma != 100:
            st.warning(f"⚠️ Distribuição incorreta: {soma}%. Ajuste os sliders para somar 100%.")
        else:
            st.success(f"Distribuição validada: CHO {get*perc_cho/400:.0f}g | PTN {get*perc_ptn/400:.0f}g | LIP {get*perc_lip/900:.0f}g")

        st.markdown("---")
        st.subheader("📝 Construção do Cardápio")
        
        modo_cardapio = st.radio("Escolha o método de elaboração:", ["🤖 Gerador Inteligente (IA)", "✍️ Estruturação Manual"], horizontal=True)

        if modo_cardapio == "🤖 Gerador Inteligente (IA)":
            habitos_input = st.text_area("Rotina e preferências da paciente:", placeholder="Ex: Gestante tem muita azia pela manhã...", height=120)
            if st.button("✨ Gerar Cardápio Inteligente"):
                if not habitos_input.strip(): st.warning("⚠️ Forneça detalhes sobre a rotina.")
                else:
                    with st.spinner("Estruturando o cardápio ideal..."):
                        try:
                            resultado = gerar_cardapio_ia(dados_paciente=dados, habitos_texto=habitos_input.strip())
                            st.session_state["cardapio_ia"] = resultado
                        except Exception as e:
                            st.error(f"Erro na geração: {e}")
        else:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                cafe = st.text_area("☕ Café da Manhã", height=80)
                almoco = st.text_area("🍲 Almoço", height=80)
                jantar = st.text_area("🍽️ Jantar", height=80)
            with col_m2:
                lanche_m = st.text_area("🥪 Lanche da Manhã", height=80)
                lanche_t = st.text_area("🍎 Lanche da Tarde", height=80)
                ceia = st.text_area("🌙 Ceia", height=80)
                
            if st.button("💾 Salvar Cardápio Manual"):
                texto_manual = ""
                if cafe.strip(): texto_manual += f"**Café da manhã**\n{cafe.strip()}\n\n"
                if lanche_m.strip(): texto_manual += f"**Lanche da manhã**\n{lanche_m.strip()}\n\n"
                if almoco.strip(): texto_manual += f"**Almoço**\n{almoco.strip()}\n\n"
                if lanche_t.strip(): texto_manual += f"**Lanche da tarde**\n{lanche_t.strip()}\n\n"
                if jantar.strip(): texto_manual += f"**Jantar**\n{jantar.strip()}\n\n"
                if ceia.strip(): texto_manual += f"**Ceia**\n{ceia.strip()}\n\n"
                
                if texto_manual:
                    st.session_state["cardapio_ia"] = texto_manual
                    st.success("✅ Cardápio salvo!")
                else: st.warning("⚠️ Preencha pelo menos uma refeição.")

if "cardapio_ia" in st.session_state and st.session_state["cardapio_ia"]:
                st.markdown("### 📋 Cardápio Final")
                st.markdown(f'<div class="laudo-box">{st.session_state["cardapio_ia"]}</div>', unsafe_allow_html=True)
                if st.button("📄 Exportar Cardápio em PDF"):
                    from nutri_pdf import gerar_pdf_cardapio_ia
                    pdf_bytes_card = gerar_pdf_cardapio_ia(dados_paciente=dados, texto_cardapio=st.session_state["cardapio_ia"])
                    st.download_button(
                        label="⬇️ Baixar PDF do Cardápio", 
                        data=pdf_bytes_card, 
                        file_name=f"Plano_Alimentar_{dados['nome'].replace(' ', '_')}.pdf", 
                        mime="application/pdf",
                        width="stretch" # <---- ADICIONE ISTO AQUI TAMBÉM
                    )
