import streamlit as st
import math
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

from nutri_calc import extrair_ponto, calcular_classificacao_atalah
from nutri_pdf import gerar_pdf_gestante
from nutri_ia import gerar_cardapio_ia

st.set_page_config(page_title="Gestantes | NutriAPS", layout="wide")

# REGRA DE OURO DO MULTIPÁGINAS
if "current_module" not in st.session_state or st.session_state["current_module"] != "gestante":
    st.session_state.clear()
    st.session_state["current_module"] = "gestante"

# INJEÇÃO DE CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1D361F !important; }
    .main { background-color: #ECE5DF !important; padding: 2rem !important; }
    [data-testid="stAppViewContainer"] { background-color: #ECE5DF !important; }
    [data-testid="stSidebar"] { background-color: #DFC8B6 !important; border-right: 1px solid #C4C7B6; }
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
        
        st.markdown("<br><p style='font-size: 14px; margin-bottom: 5px;'><b>Condições Clínicas Especiais:</b></p>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1: is_dmg = st.checkbox("🩸 Diabetes Gestacional (DMG)")
        with cc2: is_has = st.checkbox("🫀 Hipertensão Arterial (HAS)")

    if altura > 0 and peso_atual > 0:
        res_gest = calcular_classificacao_atalah(peso_atual, altura, semana_gestacional, peso_pre_input)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if peso_pre_input > 0.0:
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("IMC Atual", f"{res_gest['imc_atual']:.1f} kg/m²")
            with m2: st.metric("Classificação", res_gest['classificacao_atual'])
            with m3: st.metric("GPG (Ganho)", f"{res_gest['gpg']:.1f} kg")
            with m4: st.metric("Meta Total", f"{res_gest['ganho_min']} a {res_gest['ganho_max']} kg")
        else:
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("IMC Atual", f"{res_gest['imc_atual']:.1f} kg/m²")
            with m2: st.metric("Classificação", res_gest['classificacao_atual'])
            with m3: st.metric("Meta Total*", f"{res_gest['ganho_min']} a {res_gest['ganho_max']} kg")

        laudo_gest_html = f"""
        <div class="laudo-box" style="border-top-color: #859B48;">
            <h3 style="color: #1D361F; margin-top: 0;">Diagnóstico Nutricional Obstétrico</h3>
            <p style="margin-bottom:8px;"><strong>Estado Atual: <span style="color:#859B48;">{res_gest['classificacao_atual']}</span></strong></p>
            <p style="line-height:1.6; font-style: italic; color: #555;">"{res_gest['diagnostico']}"</p>
            <hr style="margin: 12px 0;">
            <h3 style="color: #859B48; margin-top: 0; font-size: 1.1rem;">Conduta e Orientação</h3>
            <p style="line-height:1.6; color: #1D361F;">{res_gest['conselho']}</p>
        </div>
        """
        st.markdown(laudo_gest_html, unsafe_allow_html=True)
        
        st.markdown("<br>### 📈 Curva de Atalah (1997) - Estado Nutricional Atual", unsafe_allow_html=True)
        
        semanas_eixo = list(range(6, 43))
        baixo_lim = [res_gest['tabela_atalah'][s][0] for s in semanas_eixo]
        eutrofia_lim = [res_gest['tabela_atalah'][s][1] for s in semanas_eixo]
        sobrepeso_lim = [res_gest['tabela_atalah'][s][2] for s in semanas_eixo]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=semanas_eixo, y=baixo_lim, line=dict(color='#859B48', width=2), name="Adequado (Mínimo)"))
        fig.add_trace(go.Scatter(x=semanas_eixo, y=eutrofia_lim, fill='tonexty', fillcolor='rgba(133, 155, 72, 0.2)', line=dict(color='#D97706', width=2), name="Adequado (Máximo)"))
        fig.add_trace(go.Scatter(x=semanas_eixo, y=sobrepeso_lim, fill='tonexty', fillcolor='rgba(217, 119, 6, 0.1)', line=dict(color='#DC2626', width=2, dash='dash'), name="Sobrepeso (Máximo)"))
        fig.add_trace(go.Scatter(x=[semana_gestacional], y=[res_gest['imc_atual']], mode='markers+text', text=["📍 IMC Atual"], textposition="top center", marker=dict(color='#1D361F', size=14, line=dict(color='#FFFFFF', width=2)), name="Visita Atual", showlegend=False))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#F7F3F0', font=dict(color='#1D361F'), xaxis_title="Semana Gestacional", yaxis_title="IMC Atual (kg/m²)",
            margin=dict(l=40, r=40, t=40, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig)
        
        st.session_state["dados_paciente"] = {
            "nome": nome, "idade": idade, "sexo": "Feminino", "peso": float(peso_atual), "altura": float(altura),
            "is_gestante": True, "semana": semana_gestacional, "res_gest": res_gest,
            "is_dmg": is_dmg, "is_has": is_has
        }

        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = gerar_pdf_gestante(st.session_state["dados_paciente"])
        
        if nome:
            st.download_button(
                label="📥 Baixar Relatório Gestante (PDF)",
                data=pdf_bytes,
                file_name=f"Relatorio_Gestante_{nome}.pdf",
                mime="application/pdf",
                use_container_width=True
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
                st.download_button(label="⬇️ Baixar PDF do Cardápio", data=pdf_bytes_card, file_name=f"Plano_Alimentar_{dados['nome'].replace(' ', '_')}.pdf", mime="application/pdf")