import streamlit as st
import re

st.set_page_config(page_title="Linha de Obesidade | NutriAPS", layout="wide")

if "current_module" not in st.session_state or st.session_state["current_module"] != "obesidade":
    st.session_state.clear()
    st.session_state["current_module"] = "obesidade"

def extrair_ponto(texto):
    """Extrai o número inteiro de dentro de parênteses, ex: '(3 pts)' -> 3"""
    match = re.search(r'\((\d+)\s*pt', texto)
    return int(match.group(1)) if match else 0

# ==========================================
# INJEÇÃO DE CSS
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1D361F !important; }
    .material-icons, .material-symbols-rounded, [data-testid*="Icon"] { font-family: "Material Symbols Rounded", "Material Icons" !important; }
    .main { background-color: #ECE5DF !important; padding: 2rem !important; }
    [data-testid="stAppViewContainer"] { background-color: #ECE5DF !important; }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #F7F9F7 !important; border-right: 1px solid #E2EBE3 !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .sidebar-logo { padding: 0rem 1.4rem 1.4rem 1.4rem; border-bottom: 1px solid #E2EBE3; margin-bottom: 1.4rem; }
    .sidebar-logo .logo-title { font-size: 1.3rem; font-weight: 700; color: #1D361F; }
    .sidebar-logo .logo-sub { font-size: 0.75rem; color: #5A7260; margin-top: 0.2rem; }
    .nav-group-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; color: #859B48; padding: 0 1.4rem; margin-bottom: 0.4rem; }
    [data-testid="stSidebar"] [data-testid="stPageLink"] a { padding: 0.6rem 0.85rem !important; border-radius: 9px !important; font-size: 0.88rem !important; font-weight: 600 !important; color: #2D5A34 !important; }
    [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background: #E8F0E9 !important; }

    /* ESTILOS DA PÁGINA */
    h1, h2, h3, h4 { color: #1D361F !important; font-weight: 700 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] { background-color: #F7F3F0 !important; border: 1px solid #C4C7B6 !important; border-radius: 10px !important; }
    .stButton button { background-color: #859B48 !important; color: #FFFFFF !important; border: none !important; border-radius: 12px !important; padding: 0.6rem 1.5rem !important; font-weight: 600 !important; width: 100% !important; text-transform: uppercase; }
    .stButton button:hover { background-color: #1D361F !important; }
    
    /* BOXES CDSS */
    .cdss-alerta { padding: 15px 20px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid; font-size: 0.95rem; }
    .cdss-critico { background-color: #FEF2F2; border-color: #DC2626; color: #991B1B; }
    .cdss-atencao { background-color: #FFF9F0; border-color: #D97706; color: #B45309; }
    .cdss-ok { background-color: #F0F6F1; border-color: #859B48; color: #2D5A34; }
    
    .laudo-box { background-color: #FFFFFF; padding: 2rem; border-radius: 16px; border: 1px solid #C4C7B6; border-top: 6px solid #859B48; margin-top: 20px; }
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
    
    # --- CSS EXCLUSIVO E TÍTULO PARA O PRAR ---
    st.markdown("""
        <style>
        /* Caça especificamente o link do PRAR e transforma numa "Box" */
        a[href$="Protocolo_PRAR"] {
            background-color: #F0F6F1 !important; /* Fundo verdinho bem claro */
            border: 1px solid #C4C7B6 !important; /* Bordinha marcando o destaque */
            box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
        }
        a[href$="Protocolo_PRAR"]:hover {
            background-color: #E8F0E9 !important;
            border-color: #859B48 !important;
        }
        </style>
        
        <div class="nav-group-label" style="margin-top: 1.8rem;">Apoio Clínico</div>
    """, unsafe_allow_html=True)

    # O link do PRAR é renderizado aqui embaixo do novo título
    st.page_link("pages/04_📚_Protocolo_PRAR.py",  label="📚  Protocolo PRAR")

    # O Rodapé fica logo abaixo
    st.markdown("""
        <div class="sidebar-footer">
            NutriAPS · v2.0<br>
            Residência Multiprofissional<br>
            Atenção Básica - 2026
        </div>
    """, unsafe_allow_html=True)
    

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
_, main_col, _ = st.columns([0.5, 9, 0.5])

with main_col:
    st.title("⚖️ Sistema de Apoio Clínico: Obesidade (CDSS)")
    st.markdown("<p style='color:#5A7260; font-size:1.1rem; margin-top:-0.5rem;'>Estratificação MACC, Alertas de Conduta e Avaliação Comportamental.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # --- SEÇÃO 1: DADOS BIOMÉTRICOS ---
    st.header("1. Dados Biométricos")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo", placeholder="Ex: Maria da Silva")
            peso = st.number_input("Peso Atual (kg)", min_value=30.0, max_value=300.0, value=95.0, step=0.1)
        with col2:
            altura = st.number_input("Altura (cm)", min_value=100, max_value=250, value=165, step=1)
            idade = st.number_input("Idade (anos)", min_value=0, max_value=120, value=30, step=1)
    
    # Caixa verde do IMC em tempo real
    if altura > 0:
        altura_m = altura / 100.0
        imc = peso / (altura_m ** 2)
        if imc < 25: classif_rt = "Peso Saudável"
        elif imc < 30: classif_rt = "Sobrepeso"
        elif imc < 35: classif_rt = "Obesidade Grau I"
        elif imc < 40: classif_rt = "Obesidade Grau II"
        else: classif_rt = "Obesidade Grau III"

        st.markdown(f"""
            <div style="background-color: #859B48; color: white; padding: 15px; border-radius: 12px; margin-top: 15px; text-align: center;">
                <strong>IMC ATUAL:</strong> {imc:.1f} kg/m² &nbsp; | &nbsp; <strong>Classificação:</strong> {classif_rt}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- SEÇÃO 2: RASTREAMENTO CLÍNICO E PSICOLÓGICO ---
    st.header("2. Rastreamento Clínico e Psicológico")
    st.markdown("#### Comorbidades (Atenção às Condições Crônicas)")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        has = st.checkbox("Hipertensão (Pressão Alta)")
        dm = st.checkbox("Diabetes ou Açúcar Alto")
        cvd = st.checkbox("Problemas do Coração (Infarto, etc)")
    with c_col2:
        aos = st.checkbox("Apneia do Sono (Ronco forte)")
        osteo = st.checkbox("Dores graves nas juntas (Joelho/Coluna)")
        psic = st.checkbox("Depressão ou Ansiedade")

    comorbidades_graves = has or dm or cvd or aos or osteo

    st.markdown("<br>", unsafe_allow_html=True)
    fase_mudanca = st.radio(
        "Como o paciente se sente em relação a mudar os hábitos alimentares hoje?",
        options=[
            "Pré-contemplação (Acha que não precisa mudar / Não quer falar disso)",
            "Contemplação (Sabe que precisa, mas acha muito difícil começar)",
            "Preparação (Quer começar agora, nas próximas semanas)",
            "Ação (Já começou a fazer mudanças recentemente)"
        ]
    )

    st.markdown("---")

    # --- SEÇÃO 3: PRAR ---
    st.header("3. Avaliação de Risco Alimentar (PRAR)")
    st.caption("Protocolo PRAR — Pontuação de Risco Alimentar Rápida | Maior pontuação = maior risco")

    perguntas = [
        ("Frutas ou hortaliças por dia", ["Nenhuma (3 pts)", "Raramente (2 pts)", "1 a 2 porções (1 pt)", "3 ou mais porções (0 pts)"]),
        ("Bebidas adoçadas, sucos industrializados ou doces", ["Todo dia (3 pts)", "3 a 5x na semana (2 pts)", "1 a 2x na semana (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Água ingerida por dia", ["Quase não bebe água (3 pts)", "Menos de 4 copos / 1 litro (2 pts)", "5 a 7 copos (1 pt)", "Mais de 8 copos / 2 litros (0 pts)"]),
        ("Ultraprocessados salgados (embutidos, fast food)", ["Todo dia (3 pts)", "3 a 5x na semana (2 pts)", "1 a 2x na semana (1 pt)", "Raramente ou nunca (0 pts)"]),
        ("Substitui refeições principais por lanches", ["Quase sempre (3 pts)", "Frequentemente (2 pts)", "Às vezes (1 pt)", "Nunca (0 pts)"]),
        ("Come distraído (celular, TV, computador)", ["Sempre (3 pts)", "Frequentemente (2 pts)", "Às vezes (1 pt)", "Nunca (0 pts)"]),
        ("Adiciona sal extra ou usa temperos prontos", ["Sempre (3 pts)", "Frequentemente (2 pts)", "Raramente (1 pt)", "Nunca (0 pts)"]),
        ("Frituras de imersão", ["4x ou mais na semana (3 pts)", "2 a 3x na semana (2 pts)", "1x na semana (1 pt)", "Nunca ou raramente (0 pts)"]),
        ("Velocidade da mastigação", ["Muito rápido, mal mastiga (3 pts)", "Rápido (2 pts)", "Normal (1 pt)", "Devagar, saboreia bem (0 pts)"]),
        ("Organização e planejamento das refeições", ["Péssimo, pula refeições (3 pts)", "Ruim, come o que tem na hora (2 pts)", "Razoável (1 pt)", "Ótimo, tudo planejado (0 pts)"]),
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

    # --- ABAS DE RESULTADO ---
    tab_avaliacao, tab_opcoes = st.tabs(["📋 Avaliação e PDF", "🍽️ Orientações Rápidas"])

    with tab_avaliacao:
        st.write("")
        col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 1.5, 1])
        with col_btn_2:
            gerar_btn = st.button("GERAR AVALIAÇÃO E PDF", use_container_width=True)

        if gerar_btn:
            if not nome:
                st.warning("⚠️ Preencha o nome do paciente antes de gerar a avaliação.")
            else:
                if total_pontos <= 10: risco_prar = "Baixo"
                elif total_pontos <= 20: risco_prar = "Moderado"
                else: risco_prar = "Alto"

                st.header("📋 Resultado da Avaliação (Visão Profissional)")
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("IMC do Paciente", f"{imc:.1f} kg/m²")
                m_col2.metric("Diagnóstico", classif_rt)
                m_col3.metric("Risco PRAR", f"{total_pontos}/30 ({risco_prar})")

                # LÓGICA MACC (Com a sua correção perfeita)
                if imc >= 40 or (imc >= 35 and comorbidades_graves):
                    nivel_macc = "Nível 4 (Alto Risco - Avaliação Cirúrgica)"
                    alert_class = "cdss-critico"
                    cdss_msg = "⚠️ <strong>ALERTA DE SISTEMA:</strong> Paciente atinge critérios do CFM/SUS para Avaliação Bariátrica.<br><strong>Conduta:</strong> Verificar documentação de 2 anos de falha em tratamento clínico prévio. Articular encaminhamento especializado via regulação."
                    cor_laudo = "#DC2626"
                    
                elif imc >= 35 or (imc >= 25 and comorbidades_graves):
                    nivel_macc = "Nível 3 (Risco Moderado - Cuidado Compartilhado)"
                    alert_class = "cdss-atencao"
                    cdss_msg = "⚕️ <strong>ALERTA DE SISTEMA:</strong> Risco clínico elevado exige manejo integrado. <br><strong>Conduta:</strong> Discutir o caso com o Médico da UBS. Solicitar exames laboratoriais de rotina e estruturar plano dietoterápico."
                    cor_laudo = "#D97706"
                    
                else:
                    nivel_macc = "Níveis 1 e 2 (Promoção da Saúde na APS)"
                    alert_class = "cdss-ok"
                    cdss_msg = "✅ <strong>SISTEMA:</strong> Risco metabólico estabilizado. <br><strong>Conduta:</strong> Manejo exclusivo na Atenção Primária focado em Estilo de Vida, reeducação alimentar e monitoramento via PRAR."
                    cor_laudo = "#859B48"

                # LÓGICA DE ALERTA COMPORTAMENTAL
                if "Pré-contemplação" in fase_mudanca:
                    alert_comp = "cdss-critico"
                    msg_comp = "🧠 <strong>ALERTA COMPORTAMENTAL:</strong> Paciente resistente. Não prescreva dietas restritivas hoje, a taxa de falha será quase 100%. Foque na <em>Entrevista Motivacional</em> e no vínculo de confiança."
                    laudo_pac_texto = "Hoje nossa consulta foi para nos conhecermos melhor. Entendo que mudar rotinas é difícil. Vamos focar apenas em cuidar do seu bem-estar geral, sem pressão ou dietas malucas."
                    dicas_lista = [
                        "Apenas observe como seu corpo se sente após as refeições.",
                        "Tente beber um copo de água a mais por dia."
                    ]
                elif "Contemplação" in fase_mudanca:
                    alert_comp = "cdss-atencao"
                    msg_comp = "🧠 <strong>ALERTA COMPORTAMENTAL:</strong> Paciente ambivalente. Trabalhe as barreiras e os benefícios da mudança. Foque em apenas 1 ou 2 metas minúsculas."
                    laudo_pac_texto = "Sabemos que o peso está incomodando, mas não precisamos mudar tudo de uma vez. Vamos dar um passo bem pequeno e seguro de cada vez."
                    dicas_lista = [
                        "Troque um lanche de pacote por uma fruta que você gosta.",
                        "Tente não levar a panela para a mesa na hora do almoço."
                    ]
                else:
                    alert_comp = "cdss-ok"
                    msg_comp = "🧠 <strong>ALERTA COMPORTAMENTAL:</strong> Janela de oportunidade! Paciente engajado. Excelente momento para aplicar o PRAR completo e estruturar um plano de ação claro."
                    laudo_pac_texto = "Que ótimo que você quer cuidar mais de você! O excesso de peso cansa o corpo, mas com as mudanças certas, sua energia vai melhorar muito rápido."
                    dicas_lista = [
                        "Coloque sempre salada no almoço e no jantar.",
                        "Evite frituras e prefira carnes assadas ou cozidas.",
                        "Faça uma caminhada leve no seu ritmo."
                    ]

                st.markdown(f'<div class="{alert_class}"><strong>Estratificação MACC:</strong> {nivel_macc}<br><br>{cdss_msg}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="{alert_comp}">{msg_comp}</div>', unsafe_allow_html=True)

                st.markdown("### 📄 Nosso Combinado (Visão do Paciente)")
                dicas_html = "".join([f"<li>{d}</li>" for d in dicas_lista])
                laudo_html = (
                    f'<div class="laudo-box" style="border-top-color: {cor_laudo};">'
                    f'<h3 style="color: {cor_laudo}; margin-top: 0;">Nosso Combinado — {nome}</h3>'
                    f'<p style="line-height:1.6; font-size: 1.1rem; color: #333;">{laudo_pac_texto}</p>'
                    f'<hr style="margin: 15px 0; border: none; border-top: 1px dashed #C4C7B6;">'
                    f'<h4 style="color: #2D5A34; margin-bottom: 10px;">Metas Combinadas:</h4>'
                    f'<ul style="line-height: 1.8; color: #1D361F; margin-left: 20px;">'
                    f'{dicas_html}'
                    f'</ul>'
                    f'</div>'
                )
                st.markdown(laudo_html, unsafe_allow_html=True)

                # GERAÇÃO DO PDF
                try:
                    from nutri_pdf import gerar_pdf_obesidade
                    pdf_bytes = gerar_pdf_obesidade(
                        nome=nome, peso=peso, altura=altura, imc=imc, classif=classif_rt, 
                        nivel_macc=nivel_macc, fase_mudanca=fase_mudanca, pontos_prar=total_pontos, 
                        risco_prar=risco_prar, texto_paciente=laudo_pac_texto, dicas_lista=dicas_lista, respostas_hab=respostas
                    )
                    st.success("✅ Relatório estruturado com sucesso!")
                    st.download_button(
                        label="📄 Baixar Plano de Cuidado (PDF)",
                        data=pdf_bytes,
                        file_name=f"Plano_Obesidade_{nome.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"Erro ao gerar PDF. Verifique se colou a função no nutri_pdf.py. Detalhe: {e}")