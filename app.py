from nutri_calc import calcular_imc, calcular_necessidades_energeticas, extrair_ponto
from nutri_pdf import gerar_pdf_paciente
from nutri_foods import carregar_tabela_alimentos
from nutri_ia import gerar_cardapio_ia
from nutri_calc import calcular_imc, calcular_necessidades_energeticas, extrair_ponto, calcular_classificacao_atalah

import math
import pandas as pd
import streamlit as st
import datetime
from fpdf import FPDF
import os
import plotly.express as px

# 1. CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="Mapa de Saúde Nutricional", layout="wide", initial_sidebar_state="expanded")

# 2. INJEÇÃO DE CSS — DESIGN SYSTEM PREMIUM (SaaS Minimalist)
# Cores: Background: #ECE5DF | Cards: #DFC8B6 | Bordas: #C4C7B6 | Accent: #859B48 | Text: #1D361F
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Reset e Variáveis Globais */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
        color: #1D361F !important;
    }

    /* Container Principal */
    .main {
        background-color: #ECE5DF !important;
        padding: 2rem !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #ECE5DF !important;
    }

    /* Sidebar Redesign */
    [data-testid="stSidebar"] {
        background-color: #DFC8B6 !important;
        border-right: 1px solid #C4C7B6;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }
    
    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }

    /* Cabeçalhos */
    h1, h2, h3 {
        color: #1D361F !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    h1 { font-size: 2.2rem !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.5rem !important; margin-top: 1rem !important; margin-bottom: 1.2rem !important; border-bottom: 2px solid #C4C7B6; padding-bottom: 10px; }

    /* Cards e Containers */
    .st-emotion-cache-12w0qpk, .st-emotion-cache-6q9sum, .st-emotion-cache-ocquxy {
        background-color: #DFC8B6 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid rgba(196, 199, 182, 0.5) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    }

    /* Esconde o "Press Enter to apply" */
    [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Input Fields Modernization */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {
        background-color: #F7F3F0 !important;
        border: 1px solid #C4C7B6 !important;
        border-radius: 10px !important;
        color: #1D361F !important;
        height: 45px !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #859B48 !important;
        box-shadow: 0 0 0 3px rgba(133, 155, 72, 0.1) !important;
    }

    /* Botões Premium */
    .stButton button {
        background-color: #859B48 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px rgba(133, 155, 72, 0.2) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stButton button:hover {
        background-color: #1D361F !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(29, 54, 31, 0.2) !important;
    }

    /* Metric Cards Redesign */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        border: 1px solid #C4C7B6 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    [data-testid="stMetricValue"] {
        color: #859B48 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #1D361F !important;
        font-weight: 500 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #DFC8B6 !important;
        border-radius: 10px 10px 0 0 !important;
        color: #1D361F !important;
        padding: 10px 25px !important;
        font-weight: 600 !important;
        border: 1px solid #C4C7B6 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #859B48 !important;
        color: white !important;
        border-color: #859B48 !important;
    }

    /* Laudo Box Customizada */
    .laudo-box {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #C4C7B6;
        border-top: 6px solid #859B48;
        color: #1D361F;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-top: 20px;
    }

    /* Slider Customization */
    /* Remove a marcação sob os números para um visual mais limpo */
    .stSlider div[data-baseweb="slider"] div[aria-hidden="true"] {
        display: none !important;
    }

    /* Bolinha (Thumb) com o halo translúcido inspirado na referência */
    .stSlider div[data-baseweb="slider"] [role="slider"] {
        background-color: #859B48 !important;
        box-shadow: 0 0 0 5px rgba(133, 155, 72, 0.25) !important;
        border: none !important;
        transition: box-shadow 0.2s ease !important;
    }

    /* Efeito de destaque quando o usuário clica/arrasta o slider */
    .stSlider div[data-baseweb="slider"] [role="slider"]:hover,
    .stSlider div[data-baseweb="slider"] [role="slider"]:focus {
        box-shadow: 0 0 0 8px rgba(133, 155, 72, 0.4) !important;
        outline: none !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #859B48 !important;
    }

    /* Divider */
    hr { border-top: 1px solid #C4C7B6 !important; opacity: 0.5; }

    /* Tags e Alertas */
    .stAlert {
        border-radius: 12px !important;
        border-left: 5px solid #859B48 !important;
        background-color: #F7F3F0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INTERFACE
# ==========================================
# Usando colunas para centralizar o conteúdo e dar ar de dashboard SaaS
main_col_1, main_col_2, main_col_3 = st.columns([1, 8, 1])

with main_col_2:
    st.title("Mapa de Saúde Nutricional")
    st.markdown("<p style='font-size: 1.1rem; color: #1D361F; opacity: 0.8;'>Sistema Integrado de Avaliação Nutricional e Planejamento Clínico</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.header("1. Dados do Paciente")

    # Seleção de Perfil Clínico no padrão SaaS minimalista
    perfil_clinico = st.radio(
        "Tipo de Atendimento:",
        ["👤 População Geral", "🤰 Pré-Natal (Gestante)"],
        horizontal=True,
        key="perfil_clinico_seletor"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if perfil_clinico == "👤 População Geral":
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo", placeholder="Ex: Maria da Silva")
                idade = st.number_input("Idade (anos)", min_value=0, max_value=120, value=30, step=1)
                sexo = st.selectbox("Sexo biológico", ["Feminino", "Masculino"])
            with col2:
                peso = st.number_input("Peso (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.5)
                altura = st.number_input("Altura (cm)", min_value=50, max_value=230, value=170, step=1)
                atividade = st.selectbox(
                    "Nível de Atividade Física",
                    [
                        "Sedentário (sem exercício / trabalho sentado)",
                        "Leve (caminhada ou exercício leve 1-3x/sem)",
                        "Moderado (exercício 3-5x/sem)",
                        "Intenso (exercício pesado 6-7x/sem)",
                        "Muito Intenso (atleta / trabalho físico pesado)",
                    ]
                )

        if altura > 0:
            imc_rt = peso / ((altura / 100) ** 2)
            if imc_rt < 18.5:   classif_rt = "Magreza"
            elif imc_rt < 25:   classif_rt = "Eutrofia ✓"
            elif imc_rt < 30:   classif_rt = "Sobrepeso"
            elif imc_rt < 35:   classif_rt = "Obesidade Grau I"
            elif imc_rt < 40:   classif_rt = "Obesidade Grau II"
            else:               classif_rt = "Obesidade Grau III"
            
            st.markdown(f"""
                <div style="background-color: #859B48; color: white; padding: 15px; border-radius: 12px; margin-top: 15px; text-align: center;">
                    <strong>IMC ATUAL:</strong> {imc_rt:.1f} kg/m² &nbsp; | &nbsp; <strong>Classificação:</strong> {classif_rt}
                </div>
            """, unsafe_allow_html=True)
            
    else:
        # MÓDULO OBSTÉTRICO - ATALAH (1997) COM OPCIONAL PRÉ-GESTACIONAL
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome Completo da Gestante", placeholder="Ex: Maria da Silva")
                idade = st.number_input("Idade (anos)", min_value=10, max_value=60, value=25, step=1)
                
                # Divisão em duas subcolunas para Semanas e Dias lado a lado
                col_sub_sem, col_sub_dias = st.columns(2)
                with col_sub_sem:
                    ig_semanas = st.number_input("Idade Gestacional (Semanas)", min_value=6, max_value=42, value=20, step=1)
                with col_sub_dias:
                    ig_dias = st.number_input("Dias (Opcional)", min_value=0, max_value=6, value=0, step=1)
                
                # Regra de arredondamento: 4 a 6 dias arredonda para a próxima semana
                semana_gestacional = ig_semanas + 1 if ig_dias >= 4 else ig_semanas
                
            with col2:
                altura = st.number_input("Altura (cm)", min_value=100, max_value=220, value=160, step=1)
                peso_atual = st.number_input("Peso Atual na Consulta (kg)", min_value=30.0, max_value=250.0, value=64.0, step=0.1)
                peso_pre_input = st.number_input("Peso Pré-Gestacional (kg) [Opcional - Deixe 0.0 se não souber]", min_value=0.0, max_value=200.0, value=0.0, step=0.1)
            
            # Evita quebras no restante do sistema definindo variáveis globais
            peso = peso_atual
            sexo = "Feminino"
            atividade = "Sedentário (sem exercício / trabalho sentado)"
            
        if altura > 0 and peso_atual > 0:
            # Enviamos o peso_pre_input para a nossa nova função analítica
            res_gest = calcular_classificacao_atalah(peso_atual, altura, semana_gestacional, peso_pre_input)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # EXIBIÇÃO DINÂMICA DE CARDS: Se informou o peso pré-gestacional, exibe bloco com 4 colunas
            if peso_pre_input > 0.0:
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("IMC Atual", f"{res_gest['imc_atual']:.1f} kg/m²")
                with m2:
                    st.metric("Classificação (Atalah)", res_gest['classificacao_atual'])
                with m3:
                    st.metric("Ganho Real até Aqui (GPG)", f"{res_gest['gpg']:.1f} kg")
                with m4:
                    st.metric("Meta de Ganho Total", f"{res_gest['ganho_min']} a {res_gest['ganho_max']} kg", help="Meta oficial baseada no IMC Pré-Gestacional.")
            else:
                # Se não informou, exibe apenas as 3 métricas essenciais sem quebrar o layout
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("IMC Atual", f"{res_gest['imc_atual']:.1f} kg/m²")
                with m2:
                    st.metric("Classificação (Atalah)", res_gest['classificacao_atual'])
                with m3:
                    st.metric("Meta de Ganho Total*", f"{res_gest['ganho_min']} a {res_gest['ganho_max']} kg", help="Meta estimada através do IMC atual da semana.")

            laudo_gest_html = f"""
            <div class="laudo-box" style="border-top-color: #859B48; background-color: #FFFFFF;">
                <h3 style="color: #1D361F; margin-top: 0;">Diagnóstico Obstétrico</h3>
                <p style="margin-bottom:8px;"><strong>Estado Nutricional Atual: <span style="color:#859B48;">{res_gest['classificacao_atual']}</span></strong></p>
                <p style="line-height:1.6; font-style: italic; color: #555;">"{res_gest['diagnostico']}"</p>
                <hr style="margin: 12px 0; border-top: 1px solid #C4C7B6;">
                <h3 style="color: #859B48; margin-top: 0; font-size: 1.1rem;">Conduta e Orientação</h3>
                <p style="line-height:1.6; color: #1D361F;">{res_gest['conselho']}</p>
            </div>
            """
            st.markdown(laudo_gest_html, unsafe_allow_html=True)
            
            st.markdown("<br>### 📈 Curva de Atalah (1997) - Estado Nutricional Atual", unsafe_allow_html=True)
            import plotly.graph_objects as go
            
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
                "is_gestante": True, "semana": semana_gestacional, "res_gest": res_gest
            }

    st.markdown("---")

    st.header("2. Avaliação de Hábitos Alimentares")
    st.caption("Protocolo PRAR — Pontuação de Risco Alimentar Rápida | Maior pontuação = maior risco")

    perguntas = [
        ("Frutas ou hortaliças por dia",
         ["Nenhuma (3 pts)", "1 a 2 porções (2 pts)", "3 a 4 porções (1 pt)", "5 ou mais (0 pts)"]),
        ("Bebidas adoçadas, sucos industrializados ou doces",
         ["Todo dia (3 pts)", "3 a 4 vezes/semana (2 pts)", "1 a 2 vezes/semana (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Água ingerida por dia",
         ["Menos de 4 copos / 1 litro (3 pts)", "4 a 6 copos (2 pts)", "7 a 9 copos (1 pt)", "10 copos ou mais (0 pts)"]),
        ("Ultraprocessados salgados (embutidos, salgadinhos, fast food)",
         ["Todo dia (3 pts)", "3 a 4 vezes/semana (2 pts)", "1 a 2 vezes/semana (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Substitui refeições principais por lanches ou beliscos",
         ["Quase sempre (3 pts)", "Algumas vezes/semana (2 pts)", "Raramente (1 pt)", "Nunca (0 pts)"]),
        ("Come distraído — celular, TV, tela",
         ["Sempre (3 pts)", "Frequentemente (2 pts)", "Raramente (1 pt)", "Nunca (0 pts)"]),
        ("Adiciona sal extra ou come comidas muito salgadas",
         ["Todo dia (3 pts)", "Frequentemente (2 pts)", "Às vezes (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Atividade física regular (caminhada, academia, esporte)",
         ["Não pratica nada (3 pts)", "Às vezes, menos de 1x/sem (2 pts)", "1 a 2x/semana (1 pt)", "3x/semana ou mais (0 pts)"]),
        ("Regularidade dos horários das refeições",
         ["Muito irregular — pulo refeições com frequência (3 pts)", "Irregular (2 pts)", "Mais ou menos regular (1 pt)", "Muito regular — horários fixos (0 pts)"]),
        ("Consumo de bebidas alcoólicas",
         ["Diariamente (3 pts)", "Nos fins de semana (2 pts)", "Raramente (1 pt)", "Nunca (0 pts)"]),
    ]

    respostas = []
    # Usando cards para as perguntas do formulário
    with st.container():
        for i, (pergunta, opcoes) in enumerate(perguntas):
            resp = st.radio(f"{i+1}. {pergunta}:", opcoes, key=f"q{i}", horizontal=True)
            respostas.append((pergunta, resp))
            if i < len(perguntas) - 1: st.markdown("<hr style='margin: 10px 0; border-top: 1px solid #C4C7B6;'>", unsafe_allow_html=True)

    total_pontos = sum(extrair_ponto(r[1]) for r in respostas)
    max_pontos = len(perguntas) * 3
    perc_risco = total_pontos / max_pontos

    st.markdown(f"**Pontuação PRAR:** {total_pontos} / {max_pontos}")
    st.progress(perc_risco)
    st.markdown("---")

    tab_avaliacao, tab_cardapio = st.tabs(["📋 Avaliação e PDF", "🍽️ Cardápio"])

    with tab_avaliacao:
        st.write("") # Adiciona um respiro visual (opcional) antes do botão
        col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 1.5, 1])
        with col_btn_2:
            gerar_btn = st.button("GERAR AVALIAÇÃO E PDF", use_container_width=True)

        if gerar_btn:
            if not nome:
                st.warning("⚠️ Preencha o nome do paciente antes de gerar.")
            else:
                # Lógica de cálculo (Mantida)
                tmb, get, formula_nome = calcular_necessidades_energeticas(
                    peso=peso, altura_cm=altura, idade=idade, sexo=sexo, atividade=atividade, is_atleta=False, bf=None,
                )

                imc = peso / ((altura / 100) ** 2)
                if imc < 18.5: classif_imc = "Magreza"
                elif imc < 25: classif_imc = "Eutrofia"
                elif imc < 30: classif_imc = "Sobrepeso"
                elif imc < 35: classif_imc = "Obesidade G.I"
                elif imc < 40: classif_imc = "Obesidade G.II"
                else:          classif_imc = "Obesidade G.III"

                if perc_risco <= 0.33:
                    risco, cor, explicacao = "Baixo", "#859B48", "Parabéns! Seus hábitos são protetores da saúde. Continue priorizando alimentos in natura."
                elif perc_risco <= 0.66:
                    risco, cor, explicacao = "Moderado", "#D97706", "Você tem uma boa base, mas há espaço importante para melhorias. Vamos trabalhar trocas graduais."
                else:
                    risco, cor, explicacao = "Alto", "#DC2626", "Atenção: vários hábitos da sua rotina aumentam o risco de doenças crônicas. Vamos focar em mudanças graduais."

                st.session_state["dados_paciente"] = {
                    "nome": nome, "idade": idade, "sexo": sexo, "peso": float(peso),
                    "altura": float(altura), "tmb": float(tmb), "get": float(get),
                    "imc": float(imc), "classif_imc": classif_imc,
                }

                st.header("📋 Resultado da Avaliação")
                c1, c2, c3 = st.columns(3)
                c1.metric("Metabolismo Basal", f"{tmb:.0f} kcal")
                c2.metric("Gasto Diário Total", f"{get:.0f} kcal")
                c3.metric("IMC", f"{imc:.1f} — {classif_imc}")

                st.write(f"📝 Fórmula selecionada automaticamente: {formula_nome}")

                laudo_html = f"""
                <div class="laudo-box" style="border-top-color: {cor};">
                    <h3 style="color: {cor}; margin-top: 0;">Diagnóstico Clínico — {nome}</h3>
                    <p style="margin-bottom:8px;"><strong>Risco Alimentar: <span style="color:{cor};">{risco}</span></strong></p>
                    <p style="line-height:1.6;">{explicacao}</p>
                    <div style="margin-top: 15px; font-size: 0.9rem; color: #666;">Pontuação PRAR Final: {total_pontos}/{max_pontos}</div>
                </div>
                """
                st.markdown(laudo_html, unsafe_allow_html=True)

                pdf_bytes = gerar_pdf_paciente(
                    nome, idade, sexo, peso, altura, imc, classif_imc, tmb, get, formula_nome, risco, explicacao, respostas
                )

                st.success("✅ Relatório estruturado com sucesso!")
                st.download_button(
                    label="📄 Baixar Relatório PDF Profissional",
                    data=pdf_bytes,
                    file_name=f"Mapa_Nutricional_{nome.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )

    with tab_cardapio:
        st.header("🍽️ Planejamento de Cardápio")

        if "dados_paciente" not in st.session_state:
            st.info("⚠️ Realize a avaliação na aba anterior para carregar os dados biométricos.")
            st.stop()
        else:
            dados = st.session_state["dados_paciente"]

        st.subheader(f"Plano Estratégico: {dados['nome']}")
        c1, c2, c3 = st.columns(3)

        # --- BIFURCAÇÃO INTELIGENTE: GESTANTE VS POPULAÇÃO GERAL ---
        is_gestante = dados.get("is_gestante", False)

        if is_gestante:
            res = dados["res_gest"]
            c1.metric("Idade Gestacional", f"{dados['semana']} Semanas")
            c2.metric("Peso Atual", f"{dados['peso']:.1f} kg")
            c3.metric("IMC Atual", f"{res['imc_atual']:.1f} kg/m²")
            
            # Valor base de segurança para gestantes (já que não calculamos GET)
            get_base = 2000.0 
        else:
            c1.metric("GET Estimado", f"{dados['get']:.0f} kcal")
            c2.metric("Peso Atual", f"{dados['peso']:.1f} kg")
            c3.metric("IMC Atual", f"{dados['imc']:.1f}")
            
            # Valor base para população geral é o próprio GET
            get_base = float(dados["get"])

        # --- CONFIGURAÇÃO DE ENERGIA ---
        if "kcal_alvo" not in st.session_state:
            st.session_state["kcal_alvo"] = get_base

        # Sessão de energia com layout melhorado
        with st.container():
            st.markdown("### Configuração de Energia")
            e_col1, e_col2 = st.columns([3, 1])
            with e_col1:
                get_editavel = st.number_input("Definir Energia Alvo (kcal/dia)", min_value=800, max_value=5000, value=int(st.session_state["kcal_alvo"]), step=10)
            with e_col2:
                st.write("")
                st.write("")
                # Botão adaptado para servir tanto para GET quanto para a Base da Gestante
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
        
        modo_cardapio = st.radio(
            "Escolha o método de elaboração:",
            ["🤖 Gerador Inteligente (IA)", "✍️ Estruturação Manual (Qualitativa)"],
            horizontal=True
        )

        if modo_cardapio == "🤖 Gerador Inteligente (IA)":
            st.caption("Descreva os hábitos e a IA montará uma sugestão completa com base no GET.")
            habitos_input = st.text_area(
                "Rotina e preferências do paciente:",
                placeholder="Ex: Paciente prefere café da manhã rápido, gosta de frutas cítricas...",
                height=120,
            )

            if st.button("✨ Gerar Cardápio Inteligente"):
                if not habitos_input.strip():
                    st.warning("⚠️ Forneça detalhes sobre a rotina para a IA trabalhar.")
                else:
                    with st.spinner("Nossa IA está estruturando o cardápio ideal..."):
                        try:
                            resultado = gerar_cardapio_ia(dados_paciente=st.session_state["dados_paciente"], habitos_texto=habitos_input.strip())
                            st.session_state["cardapio_ia"] = resultado
                        except Exception as e:
                            st.error(f"Erro na geração: {e}")

        else:
            st.caption("Preencha qualitativamente as opções para cada refeição. Deixe em branco as que não se aplicam.")
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
                # A formatação abaixo garante que o nutri_pdf.py reconheça os subtítulos
                if cafe.strip(): texto_manual += f"**Café da manhã**\n{cafe.strip()}\n\n"
                if lanche_m.strip(): texto_manual += f"**Lanche da manhã**\n{lanche_m.strip()}\n\n"
                if almoco.strip(): texto_manual += f"**Almoço**\n{almoco.strip()}\n\n"
                if lanche_t.strip(): texto_manual += f"**Lanche da tarde**\n{lanche_t.strip()}\n\n"
                if jantar.strip(): texto_manual += f"**Jantar**\n{jantar.strip()}\n\n"
                if ceia.strip(): texto_manual += f"**Ceia**\n{ceia.strip()}\n\n"
                
                if texto_manual:
                    st.session_state["cardapio_ia"] = texto_manual
                    st.success("✅ Cardápio manual estruturado com sucesso!")
                else:
                    st.warning("⚠️ Preencha pelo menos uma refeição para salvar.")

        # Área comum para exibir e exportar o cardápio
        if "cardapio_ia" in st.session_state and st.session_state["cardapio_ia"]:
            st.markdown("### 📋 Cardápio Final")
            st.markdown(f'<div class="laudo-box">{st.session_state["cardapio_ia"]}</div>', unsafe_allow_html=True)

            if st.button("📄 Exportar Cardápio em PDF"):
                from nutri_pdf import gerar_pdf_cardapio_ia
                pdf_bytes_card = gerar_pdf_cardapio_ia(dados_paciente=st.session_state["dados_paciente"], texto_cardapio=st.session_state["cardapio_ia"])
                st.download_button(label="⬇️ Baixar PDF do Cardápio", data=pdf_bytes_card, file_name=f"Plano_Alimentar_{dados['nome'].replace(' ', '_')}.pdf", mime="application/pdf")
