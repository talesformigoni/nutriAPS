import streamlit as st

st.set_page_config(page_title="Fundamentação Técnica | NutriAPS", layout="wide")

# Regra para limpar sessão e evitar bugs
if "current_module" not in st.session_state or st.session_state["current_module"] != "prar":
    st.session_state.clear()
    st.session_state["current_module"] = "prar"

# INJEÇÃO DE CSS COMPLETA E PADRONIZADA
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; color: #1D361F !important; }
    
    .material-icons, .material-symbols-rounded, [data-testid*="Icon"], [data-testid*="Icon"] *, [data-testid="stSidebarCollapseButton"] *, [data-testid="collapsedControl"] *, [class*="icon"] {
        font-family: "Material Symbols Rounded", "Material Icons" !important;
    }
    
    .main { background-color: #ECE5DF !important; padding: 2rem !important; }
    [data-testid="stAppViewContainer"] { background-color: #ECE5DF !important; }

    /* ===================== SIDEBAR ===================== */
    [data-testid="stSidebar"] {
        background-color: #F7F9F7 !important; border-right: 1px solid #E2EBE3 !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }
    [data-testid="stSidebarNav"] { display: none !important; }
    .sidebar-logo { padding: 0rem 1.4rem 1.4rem 1.4rem; border-bottom: 1px solid #E2EBE3; margin-bottom: 1.4rem; }
    .sidebar-logo .logo-title { font-size: 1.3rem; font-weight: 700; color: #1D361F; letter-spacing: -0.02em; }
    .sidebar-logo .logo-sub { font-size: 0.75rem; color: #5A7260; margin-top: 0.2rem; }
    .nav-group-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.10em; text-transform: uppercase; color: #859B48; padding: 0 1.4rem; margin-bottom: 0.4rem; }
    
    [data-testid="stSidebar"] [data-testid="stPageLink"] { margin: 0 0.7rem 0.15rem 0.7rem !important; }
    [data-testid="stSidebar"] [data-testid="stPageLink"] a {
        display: flex !important; align-items: center !important; gap: 0.55rem !important;
        padding: 0.6rem 0.85rem !important; border-radius: 9px !important;
        font-size: 0.88rem !important; font-weight: 600 !important; color: #2D5A34 !important; text-decoration: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background: #E8F0E9 !important; color: #1D361F !important; }

    [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; display: flex !important; flex-direction: column !important; min-height: 92vh !important; }
    .sidebar-footer { margin-top: auto !important; text-align: center !important; font-size: 0.68rem !important; color: #8A9A8E !important; line-height: 1.6 !important; padding-bottom: 1rem !important; }

    /* Estilos Customizados da Página PRAR */
    h1, h2, h3 { color: #1D361F !important; font-weight: 700 !important; }
    h1 { font-size: 2.2rem !important; margin-bottom: 0.5rem !important; }
    h2 { font-size: 1.4rem !important; margin-top: 1.8rem !important; margin-bottom: 1rem !important; border-bottom: 2px solid #C4C7B6; padding-bottom: 8px; }
    
    .card-estudo { background: #FFFFFF; border-radius: 12px; padding: 22px; margin-bottom: 15px; border: 1px solid #C4C7B6; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    .card-estudo h4 { margin-top: 0; color: #2D5A34; font-size: 1.15rem; font-weight: 700; }
    .card-estudo p { line-height: 1.6; font-size: 0.92rem; text-align: justify; }
    
    .risco-box { display: flex; gap: 20px; margin-top: 15px; flex-wrap: wrap; }
    .risco-item { flex: 1; min-width: 250px; padding: 20px; border-radius: 12px; }
    .r-baixo { background: #F0F6F1; border-left: 6px solid #859B48; }
    .r-medio { background: #FFF9F0; border-left: 6px solid #D97706; }
    .r-alto { background: #FEF2F2; border-left: 6px solid #DC2626; }
    
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

    st.markdown("""
        <style>
        a[href$="Protocolo_PRAR"] {
            background-color: #F0F6F1 !important;
            border: 1px solid #C4C7B6 !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
        }
        a[href$="Protocolo_PRAR"]:hover {
            background-color: #E8F0E9 !important;
            border-color: #859B48 !important;
        }
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
# INTERFACE PRINCIPAL
# ==========================================
_, main_col, _ = st.columns([0.5, 9, 0.5])

with main_col:
    st.title("📚 Fundamentação Científica e Justificativa")
    st.markdown("<p style='color:#5A7260; font-size:1.1rem; margin-top:-0.5rem;'>Análise dos critérios clínicos, escolhas de design e automação de protocolos no ecossistema NutriAPS.</p>", unsafe_allow_html=True)
    st.markdown("---")

# --- SEÇÃO 1 - APRESENTAÇÃO E MEMORIAL ---
    st.header("1. Apresentação e Memorial Institucional")
    st.markdown("<p style='font-size:0.95rem; margin-top:-0.5rem; color:#5A7260;'>Histórico de desenvolvimento e propósito técnico-científico da plataforma:</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card-estudo">
    <h4>1.1 Origem e Desenvolvimento do Ecossistema</h4>
    <p>O <strong>NutriAPS</strong> é uma plataforma tecnológica de suporte à decisão clínica (CDSS) idealizada e desenvolvida pelo nutricionista e residente <strong>Benedito Tales Santos Sousa Formigoni</strong>, no ano de 2026. A concepção, estruturação e arquitetura de dados do sistema consolidaram-se como produto técnico durante o período de sua atuação na <strong>Residência Multiprofissional em Atenção Básica / Saúde da Família</strong>, no município de <strong>Buritis - Rondônia (RO)</strong>.</p>
    <p>Desenvolvido de forma independente e com caráter estritamente benemérito, o sistema foi gentilmente cedido para uso dos profissionais de nutrição e equipes de Saúde da Família atuantes na Atenção Primária à Saúde (APS) do estado de Rondônia, permanecendo como uma ferramenta de utilidade pública com acesso totalmente gratuito, livre e desprovido de fins comerciais.</p>
    </div>
    
    <div class="card-estudo">
    <h4>1.2 Propósito Assistencial e Governança Clínica</h4>
    <p>O ecossistema foi projetado com o objetivo estratégico de mitigar os gargalos operacionais do cotidiano assistencial do Sistema Único de Saúde (SUS), otimizando o tempo físico de consulta na unidade sem prejuízo ao rigor metodológico. A ferramenta atua como um guia dinâmico orientador, auxiliando o profissional na condução dietoterápica e na tomada de decisões clínicas seguras, observando e integrando de forma estrita os regulamentos e protocolos vigentes, tais como:</p>
    <ul style="line-height: 1.6; margin-left: 20px;">
        <li>As diretrizes de triagem epidemiológica da Classificação NOVA e do <strong>Guia Alimentar para a População Brasileira (2014)</strong> do Ministério da Saúde.</li>
        <li>Os parâmetros de diagnóstico antropométrico e pontos de corte oficiais estabelecidos pelo <strong>Sistema de Vigilância Alimentar e Nutricional (SISVAN / VAN)</strong>.</li>
        <li>Os fluxos de triagem e arranjos assistenciais preconizados pela recente <strong>Linha de Cuidado do Sobrepeso e da Obesidade do Estado de Rondônia (2024)</strong>.</li>
    </ul>
    <p style="margin-top: 15px;">Ao transpor as evidências dos manuais técnicos para um ecossistema digital interativo, o NutriAPS qualifica o registro de dados na Atenção Básica, promove a padronização das condutas baseadas em evidências e fortalece a atuação do nutricionista como agente estratégico na prevenção de agravos metabólicos crônicos na população rondoniense.</p>
    </div>
                
    <div class="card-estudo">
    <h4>1.3 Arquitetura de Software e Stack Tecnológico</h4>
    <p>Para os profissionais de Tecnologia da Informação (TI) e Informática em Saúde que auditam ou interagem com o NutriAPS, o sistema foi construído sob uma arquitetura ágil, responsiva e de fácil manutenção, utilizando o seguinte ecossistema tecnológico:</p>
    <ul style="line-height: 1.6; margin-left: 20px;">
        <li><strong>Linguagem Core (Python):</strong> Toda a inteligência matemática, regras de negócio, cruzamento de dados de comorbidades e os algoritmos do Suporte à Decisão Clínica (CDSS) foram desenvolvidos em Python. A escolha garante precisão absoluta no processamento das equações e viabiliza futuras integrações com bancos de dados relacionais e prontuários eletrônicos.</li>
        <li><strong>Framework Web (Streamlit):</strong> A interface gráfica (front-end) foi inteiramente orquestrada via Streamlit. Isso permite que a aplicação rode como uma interface fluida e reativa, adaptando-se perfeitamente aos monitores das Unidades Básicas de Saúde ou dispositivos móveis, processando gatilhos e alertas visuais em tempo real.</li>
        <li><strong>Ambiente de Desenvolvimento:</strong> A engenharia de software, codificação, componentização visual e depuração do código-fonte foram realizadas integralmente no ambiente do Visual Studio Code (VS Code).</li>
        <li><strong>Segurança e Estado de Sessão:</strong> A aplicação emprega a gestão de estados (<code>session_state</code>) para garantir o isolamento da memória. Isso assegura que os dados de triagem de um paciente não sofram vazamento ou sobreposição ao alternar entre as abas e módulos clínicos (Geral, Gestantes, Idosos e Obesidade), preservando a confiabilidade do atendimento no SUS.</li>
    </ul>
    </div>
        """, unsafe_allow_html=True)

    # --- SEÇÃO 2 ---
    st.header("2. Racional da Interface e Linguagem Acessível")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        <div class="card-estudo">
            <h4>Democratização do Entendimento</h4>
            <p>O NutriAPS foi projetado sob a premissa de que <strong>comunicação clara gera adesão clínica</strong>. Na Atenção Primária, os pacientes frequentemente apresentam variados níveis de alfabetismo em saúde. O uso de jargões técnicos ou diagnósticos complexos atua como uma barreira de compreensão, distanciando o usuário de seu próprio plano de cuidado.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="card-estudo">
            <h4>Laudos Clínicos Descomplicados</h4>
            <p>Os laudos gerados pelo sistema traduzem conceitos densos para termos diretos (ex: em vez de citar 'risco de sarcopenia' ou 'inadequação de micronutrientes', o texto adverte sobre 'evitar perder a força nos músculos' ou 'garantir o funcionamento estável do corpo'). Essa estratégia apoia as diretrizes de humanização do SUS, assegurando autonomia ao paciente e ao cuidador.</p>
        </div>
        """, unsafe_allow_html=True)

# --- SEÇÃO 3 ---
    st.header("3. Arquitetura de Seleção Automática de Diretrizes")
    st.markdown("<p style='font-size:0.95rem; margin-top:-0.5rem; color:#5A7260;'>A inteligência do sistema chaveia os algoritmos e protocolos automaticamente baseando-se no ciclo de vida e estado nutricional avaliado no momento:</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="card-estudo" style="height: 100%;">
            <h4>População Geral (Adultos)</h4>
            <p>O algoritmo executa uma triagem baseada no IMC para o cálculo da Taxa Metabólica Basal (TMB):</p>
            <ul style="font-size:0.85rem; padding-left:15px; margin-top:-5px;">
                <li><strong>IMC &lt; 25 kg/m²:</strong> Aplica a equação de <em>Harris-Benedict revisada (1984)</em>, eficaz na preservação ponderal de indivíduos eutróficos ou em déficit.</li>
                <li><strong>IMC ≥ 25 kg/m²:</strong> Chaveia automaticamente para <em>Mifflin-St Jeor</em>, clinicamente validada como mais precisa para populações com excesso de peso, evitando superestimar as metas calóricas.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card-estudo" style="height: 100%;">
            <h4>Acompanhamento Obstétrico</h4>
            <p>O módulo de gestantes processa o IMC de forma dinâmica cruzando as semanas de gestação com a <strong>Curva de Atalah (1997)</strong>.</p>
            <p>O cálculo de ganho de peso e as recomendações seguem de forma estrita o padrão técnico institucionalizado pela <strong>Caderneta Brasileira da Gestante (Versão MS 2026)</strong>, protegendo a díade contra desfechos adversos como DMG e Síndromes Hipertensivas.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card-estudo" style="height: 100%;">
            <h4>Avaliação Geriátrica</h4>
            <p>A classificação do IMC na pessoa idosa ignora os limites rígidos do adulto jovem e adota os pontos de corte da <strong>Vigilância Alimentar e Nutricional (VAN/MS)</strong>:</p>
            <ul style="font-size:0.85rem; padding-left:15px; margin-top:-5px;">
                <li><strong>IMC ≤ 22 kg/m²:</strong> Baixo Peso</li>
                <li><strong>IMC 22 a 27 kg/m²:</strong> Eutrofia</li>
                <li><strong>IMC ≥ 27 kg/m²:</strong> Sobrepeso</li>
            </ul>
            <p>O plano foca na estabilidade de peso e adaptações de textura frente a barreiras de mastigação/deglutição.</p>
        </div>
        """, unsafe_allow_html=True)

    with col4: # <-- NOVO CARD DA INTELIGÊNCIA DE OBESIDADE
        st.markdown("""
        <div class="card-estudo" style="height: 100%;">
            <h4>Linha de Obesidade (CDSS)</h4>
            <p>O sistema ativa um Sistema de Suporte à Decisão Clínica cruzando dados antropométricos, patológicos e comportamentais:</p>
            <ul style="font-size:0.85rem; padding-left:15px; margin-top:-5px;">
                <li><strong>Estratificação MACC:</strong> Classifica o nível de complexidade com base no protocolo do Estado de Rondônia, gerando alertas de segurança para regulação de cirurgia bariátrica.</li>
                <li><strong>Modelo Transteórico:</strong> Intercepta o estágio de prontidão psicológica do paciente para adaptar automaticamente a linguagem do laudo e a rigidez das metas.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# --- SEÇÃO 4 ---
    st.header("4. O Protocolo PRAR — Fundamentação e Estrutura Clínica")
    st.markdown("<p style='font-size:0.95rem; margin-top:-0.5rem; color:#5A7260;'>Memorial descritivo dos pilares metodológicos aplicados no desenvolvimento do score de rastreamento:</p>", unsafe_allow_html=True)

    st.markdown("""
<div class="card-estudo">
    <h4>4.1 Justificativa de Desenvolvimento no Cenário da APS</h4>
    <p>O ambiente de consultas na Atenção Primária à Saúde (APS) exige ferramentas de triagem diagnóstica que conciliem alta sensibilidade com viabilidade operacional. Ferramentas tradicionais de anamnese dietética, como o Recordatório de 24 horas ou o Questionário de Frequência Alimentar (QFA) extenso, demandam tempo clínico escasso e dependem excessivamente da memória de longo prazo do paciente. O <strong>PRAR (Pontuação de Risco Alimentar Rápida)</strong> soluciona esse gargalo operacional ao sintetizar indicadores críticos de consumo em um screening de 10 perguntas objetivas, permitindo uma estratificação de risco imediata à beira do leito ou no consultório.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="card-estudo">
    <h4>4.2 O Paradigma da Classificação NOVA</h4>
    <p>O referencial teórico do PRAR rompe com o modelo clássico focado estritamente na contagem isolada de calorias e macronutrientes, adotando a <strong>Classificação NOVA</strong> — o sistema epidemiológico reconhecido internacionalmente e desenvolvido pelo Núcleo de Pesquisas Epidemiológicas em Nutrição e Saúde (NUPENS/USP), que embasa o Guia Alimentar para a População Brasileira (2014).</p>
    <p>A Classificação NOVA categoriza os alimentos não pela sua composição biológica, mas pela <strong>extensão e propósito do processamento industrial</strong> a que são submetidos antes de chegarem à mesa, dividindo-os em quatro grupos fundamentais:</p>
    <ul style="line-height: 1.6; margin-bottom: 15px; margin-left: 20px;">
        <li><strong>1. In natura ou Minimamente Processados:</strong> Obtidos diretamente de plantas ou animais, sem sofrerem alterações, ou que passaram por processos simples (limpeza, moagem, pasteurização) que não envolvem adição de substâncias. São a base ideal da alimentação (ex: frutas, hortaliças, carnes frescas, feijão, arroz).</li>
        <li><strong>2. Ingredientes Culinários Processados:</strong> Produtos extraídos de alimentos in natura ou da natureza, usados nas cozinhas para temperar e cozinhar preparações culinárias (ex: óleos, gorduras, sal e açúcar).</li>
        <li><strong>3. Alimentos Processados:</strong> Produtos fabricados essencialmente com a adição de sal ou açúcar a um alimento in natura para aumentar sua durabilidade e torná-lo mais agradável ao paladar (ex: conservas, queijos, pães artesanais). Devem ter consumo limitado.</li>
        <li><strong>4. Alimentos Ultraprocessados:</strong> Formulações industriais sintetizadas a partir de frações de alimentos e diversas substâncias químicas (corantes, aromatizantes, emulsificantes, realçadores de sabor), com pouco ou nenhum alimento inteiro em sua composição. São desenhados para serem hiperpalatáveis (ex: refrigerantes, salgadinhos de pacote, macarrão instantâneo, embutidos). Seu consumo deve ser evitado.</li>
    </ul>
    <p style="margin-top: 15px;">Através dessa lente metodológica, o PRAR monitora ativamente duas frentes metabólicas no rastreio do paciente:</p>
    <ul style="line-height: 1.6; margin-left: 20px;">
        <li><strong>Marcadores Alimentares Protetores:</strong> Avalia a ingestão do Grupo 1 (a base protetora da saúde metabólica).</li>
        <li><strong>Marcadores de Exposição a Riscos:</strong> Rastreia o consumo diário ou semanal do Grupo 4 (ultraprocessados), cujo consumo crônico está diretamente associado a obesidade, dislipidemias e inflamação subclínica sistêmica.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="card-estudo">
    <h4>4.3 Integração de Dimensões Comportamentais e Comensalidade</h4>
    <p>Inovando em relação aos rastreios convencionais, o PRAR operacionaliza as recomendações do Capítulo 4 do Guia Alimentar, consolidando a premissa de que <em>o modo de comer e os aspectos sociais do consumo são indissociáveis da saúde metabólica</em>. O sistema pontua desvios em dois eixos comportamentais:</p>
    <ul style="line-height: 1.6; margin-left: 20px;">
        <li><strong>Regularidade Cronobiológica:</strong> A desorganização dos horários e a substituição sistemática de refeições estruturadas por beliscos ou lanches rápidos desregulam os eixos hormonais da fome/saciedade (grelina e leptina), induzindo ao balanço energético positivo compensatório.</li>
        <li><strong>Comensalidade Distraída:</strong> O hábito de alimentar-se exposto a telas (smartphones, televisores ou computadores) bloqueia a percepção neurosensorial e os estímulos cognitivos da mastigação. Isso retarda a sinalização de saciedade no hipotálamo, gerando hiperfagia involuntária e menor prazer gastronômico.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="card-estudo">
    <h4>4.4 Lógica de Pontuação Crescente e Termômetro Metabólico</h4>
    <p>A arquitetura matemática do PRAR adota uma escala linear crescente (0 a 3 pontos por resposta). Ao contrário de índices que pontuam virtudes dietéticas, o PRAR intencionalmente atribui os maiores pesos numéricos às condutas de maior agravo à saúde. Essa engenharia de dados gera um score centralizado (0 a 30 pontos) que atua como um verdadeiro termômetro de risco para Doenças Crônicas Não Transmissíveis (DANTs). Pontuações progressivamente mais altas mapeiam um gradiente de suscetibilidade individual para o desenvolvimento de obesidade, hipertensão arterial sistêmica e resistência à insulina.</p>
</div>
""", unsafe_allow_html=True)

    # Caixas de Risco
    st.markdown("""
    <div class="risco-box">
        <div class="risco-item r-baixo">
            <h3 style="color: #2D5A34; margin-top: 0; font-size:1.2rem;">🟢 0 a 10 Pontos (Baixo Risco)</h3>
            <p style="margin-top: 5px; font-size: 0.9rem;">Prevalência expressiva de hábitos protetores e alimentos in natura. Alinhado com as recomendações essenciais do Guia Alimentar.</p>
            <p style="font-size: 0.8rem; color: #5A7260; margin-bottom:0;"><em>Conduta: Reforço positivo da rotina atual.</em></p>
        </div>
        <div class="risco-item r-medio">
            <h3 style="color: #B45309; margin-top: 0; font-size:1.2rem;">🟠 11 a 20 Pontos (Médio Risco)</h3>
            <p style="margin-top: 5px; font-size: 0.9rem;">Consumo regular de ultraprocessados salgados ou bebidas adoçadas. Quebras frequentes na comensalidade estável e hidratação.</p>
            <p style="font-size: 0.8rem; color: #5A7260; margin-bottom:0;"><em>Conduta: Metas graduais de substituição de alimentos de pacote por opções caseiras.</em></p>
        </div>
        <div class="risco-item r-alto">
            <h3 style="color: #991B1B; margin-top: 0; font-size:1.2rem;">🔴 21 a 30 Pontos (Alto Risco)</h3>
            <p style="margin-top: 5px; font-size: 0.9rem;">Exposição severa a alimentos ultraprocessados, ausência rotineira de hortaliças/frutas e desorganização crônica de horários.</p>
            <p style="font-size: 0.8rem; color: #5A7260; margin-bottom:0;"><em>Conduta: Intervenção dietoterápica prioritária direcionada à prevenção de DANTs (Diabetes e Hipertensão).</em></p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SEÇÃO 5 — LINHA DE CUIDADO DA OBESIDADE (CDSS) ---
    st.header("5. Incorporação da Linha de Cuidado da Obesidade e Modelos Avançados")
    st.markdown("<p style='font-size:0.95rem; margin-top:-0.5rem; color:#5A7260;'>Análise metodológica do cruzamento de dados antropométricos, comorbidades estaduais e psicologia comportamental:</p>", unsafe_allow_html=True)

    st.markdown("""
<div class="card-estudo">
    <h4>5.1 Estratificação pelo Modelo de Atenção às Condições Crônicas (MACC)</h4>
    <p>O ecossistema NutriAPS incorpora as diretrizes operacionais da <strong>Linha de Cuidado do Sobrepeso e da Obesidade do Estado de Rondônia (2024)</strong>, estruturada a partir do Modelo de Atenção às Condições Crônicas (MACC). O algoritmo de suporte à decisão clínica (CDSS) realiza o cruzamento automatizado do Índice de Massa Corporal (IMC) com o mapeamento de comorbidades crônicas e sistêmicas (HAS, DM, apneia obstrutiva do sono, doenças cardiovasculares e osteoartropatias por carga). Essa engenharia distribui o paciente em níveis de complexidade assistencial assistidos por um semáforo visual:</p>
    <ul>
        <li><strong>Níveis 1 e 2 (Baixo Risco):</strong> Manejo e acompanhamento longitudinal focados estritamente no âmbito da Atenção Primária, centralizados na mudança de estilo de vida e monitoramento via PRAR.</li>
        <li><strong>Nível 3 (Risco Moderado):</strong> Ativação de protocolo de Cuidado Compartilhado obrigatório na APS, exigindo co-manejo entre nutricionista e corpo médico para controle laboratorial de risco metabólico.</li>
        <li><strong>Nível 4 (Alto Risco):</strong> Critério de elegibilidade para encaminhamento a serviços de Alta Complexidade e avaliação de Cirurgia Bariátrica. O sistema atua como barreira de segurança ao disparar o alerta de auditoria clínica, relembrando a obrigatoriedade regulatória de <strong>no mínimo 2 anos de tratamento clínico prévio documentado e sem sucesso na APS</strong>, conforme preconizado pelo Ministério da Saúde e pelas normativas do Estado.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="card-estudo">
    <h4>5.2 Interface Psicológica e Modelo Transteórico de Mudança</h4>
    <p>Reconhecendo que o manejo da obesidade perpassa a complexidade psicossocial do indivíduo, o sistema operacionaliza o <strong>Modelo Transteórico de Prochaska e DiClemente</strong>. O CDSS intercepta a classificação antropométrica e submete a conduta médica à fase comportamental identificada no momento da consulta:</p>
    <ul>
        <li><strong>Fases Passivas (Pré-contemplação e Contemplação):</strong> O sistema gera alertas restritivos ao profissional, contraindicando planos alimentares rígidos ou metas calóricas severas, cuja probabilidade de abandono terapêutico beira a totalidade. O laudo é programado para adotar uma abordagem de redução de danos, focando em aconselhamento motivacional e metas comportamentais mínimas.</li>
        <li><strong>Fases Ativas (Preparação e Ação):</strong> O aplicativo abre a janela de oportunidade clínica, liberando a aplicação integral do protocolo dietoterápico estruturado, estabelecimento de metas dinâmicas e engajamento ativo em intervenções de estilo de vida.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    # --- REFERÊNCIAS ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📚 Referências Bibliográficas")
    st.markdown("<p style='color:#5A7260; font-size:0.95rem; margin-top:-0.5rem;'>Base regulatória, técnica e literária que sustenta as diretrizes do NutriAPS:</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card-estudo" style="font-size: 0.85rem; line-height: 1.8; color: #1D361F;">
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            BRASIL. Ministério da Saúde. Secretaria de Atenção à Saúde. Departamento de Atenção Básica. Alimentação saudável para a pessoa idosa: um manual para profissionais de saúde. Brasília: Ministério da Saúde, 2009.
        </p>
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            BRASIL. Ministério da Saúde. Secretaria de Atenção Primária à Saúde. Departamento de Gestão do Cuidado Integral. Caderneta brasileira da gestante. Brasília: Ministério da Saúde, 2026.
        </p>
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            BRASIL. Ministério da Saúde. Secretaria de Atenção à Saúde. Departamento de Atenção Básica. Guia alimentar para a população brasileira. 2. ed. Brasília: Ministério da Saúde, 2014.
        </p>
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            BRASIL. Ministério da Saúde; UNIVERSIDADE FEDERAL DE SERGIPE. Guia para a organização da vigilância alimentar e nutricional na atenção primária à saúde. Brasília: Ministério da Saúde, 2022.
        </p>
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            BRASIL. Ministério da Saúde. Secretaria de Atenção à Saúde. Departamento de Atenção Básica. Política Nacional de Alimentação e Nutrição. 1. ed. 1. reimpr. Brasília: Ministério da Saúde, 2013.
        </p>
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            KAC, G. et al. Gestational weight gain and adverse maternal outcomes in Brazil. American Journal of Clinical Nutrition, [S. l.], v. 113, n. 5, p. 1351–1360, 2021.
        </p>
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            MONTEIRO, C. A. et al. Classificação NOVA: o sistema epidemiológico reconhecido internacionalmente. Desenvolvido pelo Núcleo de Pesquisas Epidemiológicas em Nutrição e Saúde (NUPENS/USP). Disponível em: https://nupens.fsp.usp.br/a-classificacao-nova/. Acesso em: 18 jun. 2026.
        </p>
        <p style="margin-bottom: 12px; text-indent: -1.5rem; padding-left: 1.5rem;">
            RONDÔNIA. Secretaria de Estado da Saúde. Subdiretoria Técnica em Saúde. Coordenadoria de Doenças e Condições Crônicas. Núcleo de Sobrepeso e Obesidade. Linha de Cuidado à Pessoa com Sobrepeso e Obesidade no Estado de Rondônia. Porto Velho: SESAU-RO, 2024.
        </p>
    </div>
    """, unsafe_allow_html=True)