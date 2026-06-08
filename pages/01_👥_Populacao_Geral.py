import streamlit as st
import math
import pandas as pd
import datetime

from nutri_calc import calcular_imc, calcular_necessidades_energeticas, extrair_ponto
from nutri_pdf import gerar_pdf_paciente
from nutri_foods import carregar_tabela_alimentos
from nutri_ia import gerar_cardapio_ia

st.set_page_config(page_title="População Geral | NutriAPS", layout="wide")

# REGRA DE OURO DO MULTIPÁGINAS
if "current_module" not in st.session_state or st.session_state["current_module"] != "geral":
    st.session_state.clear()
    st.session_state["current_module"] = "geral"

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
    st.title("Atendimento: População Geral")
    st.markdown("---")

    st.header("1. Dados Biométricos")
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

    st.markdown("---")
    st.header("2. Avaliação de Hábitos Alimentares")
    st.caption("Protocolo PRAR — Pontuação de Risco Alimentar Rápida | Maior pontuação = maior risco")

    perguntas = [
        ("Frutas ou hortaliças por dia", ["Nenhuma (3 pts)", "1 a 2 porções (2 pts)", "3 a 4 porções (1 pt)", "5 ou mais (0 pts)"]),
        ("Bebidas adoçadas, sucos industrializados ou doces", ["Todo dia (3 pts)", "3 a 4 vezes/semana (2 pts)", "1 a 2 vezes/semana (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Água ingerida por dia", ["Menos de 4 copos / 1 litro (3 pts)", "4 a 6 copos (2 pts)", "7 a 9 copos (1 pt)", "10 copos ou mais (0 pts)"]),
        ("Ultraprocessados salgados (embutidos, salgadinhos, fast food)", ["Todo dia (3 pts)", "3 a 4 vezes/semana (2 pts)", "1 a 2 vezes/semana (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Substitui refeições principais por lanches ou beliscos", ["Quase sempre (3 pts)", "Algumas vezes/semana (2 pts)", "Raramente (1 pt)", "Nunca (0 pts)"]),
        ("Come distraído — celular, TV, tela", ["Sempre (3 pts)", "Frequentemente (2 pts)", "Raramente (1 pt)", "Nunca (0 pts)"]),
        ("Adiciona sal extra ou come comidas muito salgadas", ["Todo dia (3 pts)", "Frequentemente (2 pts)", "Às vezes (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Atividade física regular (caminhada, academia, esporte)", ["Não pratica nada (3 pts)", "Às vezes, menos de 1x/sem (2 pts)", "1 a 2x/semana (1 pt)", "3x/semana ou mais (0 pts)"]),
        ("Regularidade dos horários das refeições", ["Muito irregular — pulo refeições com frequência (3 pts)", "Irregular (2 pts)", "Mais ou menos regular (1 pt)", "Muito regular — horários fixos (0 pts)"]),
        ("Consumo de bebidas alcoólicas", ["Diariamente (3 pts)", "Nos fins de semana (2 pts)", "Raramente (1 pt)", "Nunca (0 pts)"]),
    ]

    respostas = []
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
        st.write("")
        col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 1.5, 1])
        with col_btn_2:
            gerar_btn = st.button("GERAR AVALIAÇÃO E PDF", use_container_width=True)

        if gerar_btn:
            if not nome:
                st.warning("⚠️ Preencha o nome do paciente antes de gerar.")
            else:
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
                    "imc": float(imc), "classif_imc": classif_imc, "is_gestante": False
                }

                st.header("📋 Resultado da Avaliação")
                c1, c2, c3 = st.columns(3)
                c1.metric("Metabolismo Basal", f"{tmb:.0f} kcal")
                c2.metric("Gasto Diário Total", f"{get:.0f} kcal")
                c3.metric("IMC", f"{imc:.1f} — {classif_imc}")

                st.write(f"📝 Fórmula selecionada: {formula_nome}")

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

        if "dados_paciente" not in st.session_state or st.session_state["dados_paciente"].get("is_gestante", True):
            st.info("⚠️ Realize a avaliação na aba 'Avaliação e PDF' para carregar os dados biométricos.")
        else:
            dados = st.session_state["dados_paciente"]

            st.subheader(f"Plano Estratégico: {dados['nome']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("GET Estimado", f"{dados['get']:.0f} kcal")
            c2.metric("Peso Atual", f"{dados['peso']:.1f} kg")
            c3.metric("IMC Atual", f"{dados['imc']:.1f}")
            
            get_base = float(dados["get"])

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
                habitos_input = st.text_area("Rotina e preferências do paciente:", placeholder="Ex: Paciente prefere café da manhã rápido...", height=120)
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