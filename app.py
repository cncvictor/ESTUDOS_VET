import streamlit as st
import os
import markdown
from pathlib import Path
import random
from user_management import UserManager
from calculators import render_calculator_interface
from access_log import AccessLogger

# Configuração da página
st.set_page_config(
    page_title="Anestesiologia Veterinária",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para ler arquivos markdown
def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Erro ao ler arquivo {file_path}: {str(e)}")
        return ""

# Inicializar logger e gerenciador de usuário
logger = AccessLogger()
user_manager = UserManager()

# Registrar acesso
if "logged_access" not in st.session_state:
    try:
        ip = st.query_params.get("client_ip", ["não identificado"])[0]
    except:
        ip = "não identificado"
    
    logger.log_access(
        ip=ip,
        page=st.query_params.get("page", ["principal"])[0]
    )
    st.session_state.logged_access = True

# Estilo personalizado
st.markdown("""
    <style>
    /* Cores e Variáveis */
    :root {
        --primary: #3B82F6;
        --primary-dark: #1E40AF;
        --secondary: #10B981;
        --accent: #8B5CF6;
        --background: #F9FAFB;
        --surface: #FFFFFF;
        --text: #111827;
        --text-secondary: #4B5563;
        --border: #E5E7EB;
    }

    /* Reset e Estilos Gerais */
    .stApp {
        background: var(--background);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 2rem;
    }

    /* Header */
    .app-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        margin: -2rem -2rem 2rem -2rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: white;
    }

    .app-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        margin: 0;
        line-height: 1.2;
    }

    .app-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.875rem;
    }

    /* Métricas */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -1px rgba(0, 0, 0, 0.15);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Navegação */
    .nav-section {
        background: #F3F4F6;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }

    .nav-section h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-secondary);
        margin-bottom: 1rem;
        font-weight: 600;
    }

    /* Radio Buttons */
    .stRadio > div {
        background: transparent;
    }

    .stRadio [role="radio"] {
        padding: 1rem 1.25rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stRadio [role="radio"]:hover {
        border-color: var(--primary);
        background: #F8FAFC;
    }

    .stRadio [aria-checked="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        border: none;
        color: white;
        font-weight: 500;
    }

    /* Botões */
    .stButton button {
        width: 100%;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        color: var(--text);
        font-size: 0.875rem;
        padding: 1rem 1.25rem;
        transition: all 0.2s ease;
        margin: 0.25rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stButton button:hover {
        border-color: var(--primary);
        background: #F8FAFC;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .stButton button[kind="secondary"] {
        background: var(--surface);
        text-align: left;
        justify-content: flex-start;
    }

    .stButton button[kind="secondary"]:hover {
        border-color: var(--primary);
        background: #F8FAFC;
    }

    /* Cards */
    .content-card {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }

    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .content-card h3 {
        color: var(--text);
        font-size: 1.25rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .stTabs [role="tab"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text);
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
    }

    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        border: none;
        color: white;
    }

    /* Campo de Busca */
    .stTextInput input {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        font-size: 0.875rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stTextInput input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    }
    </style>
""", unsafe_allow_html=True)

def extract_flash_cards(content):
    lines = content.split('\n')
    cards = []
    current_question = ""
    current_answer = ""
    reading_answer = False
    
    for line in lines:
        if line.startswith('### '):
            # Novo card, salvar o anterior se existir
            if current_question and current_answer:
                cards.append({"question": current_question, "answer": current_answer})
            current_question = ""
            current_answer = ""
            reading_answer = False
        elif line.startswith('**Pergunta:**'):
            current_question = line.replace('**Pergunta:**', '').strip()
            reading_answer = False
        elif line.startswith('**Resposta:**'):
            reading_answer = True
            current_answer = line.replace('**Resposta:**', '').strip()
        elif reading_answer and line.strip():
            current_answer += " " + line.strip()
    
    # Adicionar o último card
    if current_question and current_answer:
        cards.append({"question": current_question, "answer": current_answer})
    
    return cards

def extract_clinical_cases(content):
    lines = content.split('\n')
    cases = []
    current_case = {
        "title": "",
        "patient_info": [],
        "question": "",
        "alternatives": [],
        "correct_answer": "",
        "justification": []
    }
    section = None
    
    for line in lines:
        if line.startswith('### Caso'):
            if current_case["title"]:
                cases.append(current_case.copy())
            current_case = {
                "title": line.strip(),
                "patient_info": [],
                "question": "",
                "alternatives": [],
                "correct_answer": "",
                "justification": []
            }
            section = "patient_info"
        elif line.startswith('**Questão:**'):
            section = "question"
            current_case["question"] = line.replace('**Questão:**', '').strip()
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            section = "alternatives"
            current_case["alternatives"].append(line.strip())
        elif line.startswith('**Resposta:**'):
            section = "correct_answer"
            current_case["correct_answer"] = line.replace('**Resposta:**', '').strip()
        elif line.startswith('**Justificativa:**'):
            section = "justification"
        elif line.strip() and section == "patient_info" and not line.startswith('#'):
            if line.startswith('**Paciente:**') or line.startswith('**Procedimento:**') or line.startswith('**Classificação:**'):
                current_case["patient_info"].append(line.strip())
        elif line.strip() and section == "justification":
            if line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.') or line.strip().startswith('4.') or line.strip().startswith('5.'):
                current_case["justification"].append(line.strip())
    
    if current_case["title"]:
        cases.append(current_case)
    
    return cases

# Estrutura do conteúdo
CONTENT_STRUCTURE = {
    "📚 Material Base": {
        "Anestésicos Gerais": ["Anestesicos_Gerais.md", "Anestesicos_Gerais_IV.md", "Anestesia_Inalatoria.md"],
        "Anestésicos Locais": ["Anestesicos_Locais.md", "Anestesicos_Locais_Detalhado.md", "Anestesia_Local_Intravenosa.md"],
        "Medicação Pré-Anestésica": ["Medicacao_Pre_Anestesica.md", "MPA_Completo.md", "Hipnoanalgesicos_MPA.md", "MPA_Fenotiazinicos_Benzodiazepinicos.md"],
    },
    "💊 Farmacologia": {
        "Analgésicos": ["Analgesia_Opioides.md", "Opioides.md", "AINES.md", "Analgesia_AINEs.md"],
        "Adjuvantes": ["Adjuvantes_Analgesicos.md", "Alfa2_Agonistas.md", "Gabapentina.md"],
        "Outros Fármacos": ["Anticolinergicos.md", "Bloqueadores_Adrenergicos.md", "Farmacos_Simpaticos.md", "Farmacos_Parassimpaticos.md"]
    },
    "🔬 Procedimentos": {
        "Técnicas Anestésicas": ["Tecnicas_Protocolos_Anestesicos.md", "Anestesia_Dissociativa.md", "TIVA.md"],
        "Monitoração": ["Monitoracao_Anestesica.md", "ECG_Anestesia.md", "Fichas_Anestesicas.md"],
        "Cirurgia": ["Tecnicas_Suturas_Principios_Cirurgicos.md", "Assepsia_Antissepsia.md"]
    },
    "🏥 Casos e Situações Especiais": {
        "Casos Clínicos": ["Casos_Clinicos_ENADE.md"],
        "Pacientes Especiais": ["Anestesia_Pacientes_Especiais.md"],
        "Emergências": ["RCP_Legislacao.md"]
    },
    "🎯 Material de Estudo": {
        "Flash Cards": ["FlashCards_Anestesiologia.md"],
        "Conceitos Fundamentais": ["Fisiopatologia_Dor.md", "Classificacao_Cirurgica.md"],
        "Períodos Cirúrgicos": ["Pre_Peri_Pos_Operatorio.md"]
    }
}

# Título principal
st.title("📚 Banco de Estudos - Anestesiologia")

# Barra lateral
with st.sidebar:
    # Logo e título
    st.markdown("""
        <div class="app-header">
            <span style="font-size: 28px;">🐾</span>
            <div>
                <h1 class="app-title">Anestesiologia</h1>
                <span class="app-subtitle">Medicina Veterinária</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas
    stats = user_manager.get_statistics()
    st.markdown("""
        <div class="metrics-grid">
            <div class="metric-card">
                <p class="metric-value">{}</p>
                <p class="metric-label">Estudados</p>
            </div>
            <div class="metric-card">
                <p class="metric-value">{}</p>
                <p class="metric-label">Notas</p>
            </div>
        </div>
    """.format(stats['items_studied'], stats['notes_count']), unsafe_allow_html=True)
    
    # Navegação
    st.markdown('<div class="nav-section">', unsafe_allow_html=True)
    st.markdown("### MODO DE ESTUDO")
    main_mode = st.radio(
        "",
        ["📚 Material", "🧠 Flash Cards", "🏥 Casos", "💊 Calculadoras"],
        key="main_mode",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Campo de busca
    st.markdown('<div class="nav-section">', unsafe_allow_html=True)
    st.markdown("### PESQUISAR")
    search = st.text_input("", placeholder="Buscar conteúdo...", key="search_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Estatísticas de Acesso
    st.markdown('<div class="nav-section">', unsafe_allow_html=True)
    st.markdown("### ESTATÍSTICAS DE ACESSO")
    
    stats = logger.get_access_stats()
    
    # Informações gerais
    st.markdown(f"""
        <div style='font-size: 0.9em; color: var(--text-secondary);'>
            <p>👥 Visitantes únicos: {stats['ips_unicos']}</p>
            <p>📊 Total de acessos: {stats['total_acessos']}</p>
            <p>📅 Acessos hoje: {stats['acessos_hoje']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Último acesso
    if stats['ultimo_acesso']:
        st.markdown("#### Último Acesso")
        st.markdown(f"""
            <div style='font-size: 0.9em; color: var(--text-secondary); background: var(--surface); padding: 0.8rem; border-radius: 8px; margin-top: 0.5rem;'>
                <p>🌐 IP: {stats['ultimo_acesso']['ip']}</p>
                <p>🕒 Horário: {stats['ultimo_acesso']['horario']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Conteúdo principal
if main_mode == "💊 Calculadoras":
    st.markdown("""
        <div class="content-card">
            <h3>💊 Calculadoras Anestésicas</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Ferramentas essenciais para cálculos precisos em anestesiologia veterinária
            </p>
        </div>
    """, unsafe_allow_html=True)
    render_calculator_interface()

elif main_mode == "🧠 Flash Cards":
    st.markdown("""
        <div class="content-card">
            <h3>🧠 Flash Cards</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Revise conceitos importantes de anestesiologia veterinária
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Carregar flash cards
    all_cards = []
    flash_card_files = ["FlashCards_Anestesiologia.md"]
    
    for file in flash_card_files:
        if os.path.exists(file):
            content = read_markdown_file(file)
            cards = extract_flash_cards(content)
            all_cards.extend(cards)
    
    if all_cards:
        # Inicializar o índice do card
        if "current_card_idx" not in st.session_state:
            st.session_state.current_card_idx = 0
        
        # Controles de navegação em container estilizado
        st.markdown("""
            <div class="content-card" style="display: flex; gap: 1rem; align-items: center; justify-content: space-between;">
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 1, 1, 2])
        with cols[0]:
            if st.button("⬅️", key="btn_anterior", help="Anterior", use_container_width=True):
                st.session_state.current_card_idx = max(0, st.session_state.current_card_idx - 1)
        with cols[1]:
            if st.button("➡️", key="btn_proximo", help="Próximo", use_container_width=True):
                st.session_state.current_card_idx = min(len(all_cards) - 1, st.session_state.current_card_idx + 1)
        with cols[2]:
            if st.button("🔄", key="btn_aleatorio", help="Aleatório", use_container_width=True):
                st.session_state.current_card_idx = random.randint(0, len(all_cards) - 1)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Progresso
        st.progress((st.session_state.current_card_idx + 1) / len(all_cards))
        st.markdown(f"""
            <p style="color: var(--text-secondary); font-size: 0.875rem; text-align: center; margin: 1rem 0;">
                Card {st.session_state.current_card_idx + 1} de {len(all_cards)}
            </p>
        """, unsafe_allow_html=True)
        
        # Card atual
        current_card = all_cards[st.session_state.current_card_idx]
        st.markdown("""
            <div class="content-card">
                <h3>📝 Questão</h3>
                <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 12px; color: var(--text); margin: 1rem 0;">
                    {}
                </div>
            </div>
        """.format(current_card["question"]), unsafe_allow_html=True)
        
        if st.button("👀 Mostrar Resposta", key=f"show_answer_{st.session_state.current_card_idx}", use_container_width=True):
            st.markdown("""
                <div class="content-card">
                    <h3>✅ Resposta</h3>
                    <div style="background: #ECFDF5; padding: 1.5rem; border-radius: 12px; color: var(--text); margin: 1rem 0;">
                        {}
                    </div>
                </div>
            """.format(current_card["answer"]), unsafe_allow_html=True)
            user_manager.track_progress(f"card_{st.session_state.current_card_idx}")
    else:
        st.warning("Nenhum flash card encontrado.")

elif main_mode == "🏥 Casos":
    st.markdown("""
        <div class="content-card">
            <h3>🏥 Casos Clínicos</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Estude casos reais de anestesiologia veterinária
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Carregar casos clínicos
    all_cases = []
    case_files = ["Casos_Clinicos_ENADE.md"]
    
    for file in case_files:
        if os.path.exists(file):
            content = read_markdown_file(file)
            cases = extract_clinical_cases(content)
            all_cases.extend(cases)
    
    if all_cases:
        # Inicializar o índice do caso na primeira vez
        if "current_case_idx" not in st.session_state:
            st.session_state.current_case_idx = 0
        
        # Controles de navegação
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if st.button("⬅️ Anterior", key="btn_anterior_case"):
                st.session_state.current_case_idx = max(0, st.session_state.current_case_idx - 1)
        
        with col2:
            if st.button("➡️ Próximo", key="btn_proximo_case"):
                st.session_state.current_case_idx = min(len(all_cases) - 1, st.session_state.current_case_idx + 1)
        
        with col3:
            if st.button("🔄 Aleatório", key="btn_aleatorio_case"):
                st.session_state.current_case_idx = random.randint(0, len(all_cases) - 1)
        
        # Mostrar progresso
        st.progress((st.session_state.current_case_idx + 1) / len(all_cases))
        st.markdown(f"Caso {st.session_state.current_case_idx + 1} de {len(all_cases)}")
        
        # Exibir caso atual
        current_case = all_cases[st.session_state.current_case_idx]
        
        st.markdown('<div class="case-study">', unsafe_allow_html=True)
        
        # Título e informações do paciente
        st.markdown(f"### 📋 {current_case['title']}")
        for info in current_case["patient_info"]:
            st.markdown(f"**{info}**")
        
        # Questão
        st.markdown("### ❓ Questão:")
        st.info(current_case["question"])
        
        # Alternativas
        for alt in current_case["alternatives"]:
            st.markdown(alt)
        
        # Botão para mostrar resposta e justificativa
        if st.button("👀 Ver Resposta", key=f"show_answer_case_{st.session_state.current_case_idx}"):
            st.markdown("### ✅ Resposta Correta:")
            st.success(f"**{current_case['correct_answer']}**")
            
            st.markdown("### 📝 Justificativa:")
            for item in current_case["justification"]:
                st.markdown(f"- {item}")
        
        # Adicionar opção de fazer anotações
        if st.button("📝 Adicionar Nota", key=f"add_note_{st.session_state.current_case_idx}"):
            note = st.text_area("Sua anotação:")
            if note:
                user_manager.add_note(f"case_{st.session_state.current_case_idx}", note)
                st.success("Nota adicionada com sucesso!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Nenhum caso clínico encontrado. Verifique o arquivo Casos_Clinicos_ENADE.md")

else:  # Material de Estudo
    st.markdown("""
        <div class="content-card">
            <h3>📚 Material de Estudo</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Conteúdo completo de anestesiologia veterinária
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    for section_idx, (section, categories) in enumerate(CONTENT_STRUCTURE.items()):
        st.markdown(f"""
            <div class="content-card">
                <h3>{section}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        tabs = st.tabs([cat for cat in categories.keys()])
        
        for tab_idx, (tab, (category, files)) in enumerate(zip(tabs, categories.items())):
            with tab:
                if search:
                    files = [f for f in files if search.lower() in f.lower() or 
                            search.lower() in read_markdown_file(f).lower()]
                
                if not files:
                    st.info(f"Nenhum conteúdo encontrado em {category}")
                    continue
                
                cols = st.columns(2)
                for idx, file in enumerate(files):
                    with cols[idx % 2]:
                        title = file.replace('.md', '').replace('_', ' ')
                        if st.button(
                            f"📄 {title}",
                            key=f"btn_{section_idx}_{tab_idx}_{idx}",
                            use_container_width=True,
                            type="secondary"
                        ):
                            st.session_state.current_file = file
                            st.session_state.show_content = True
                
                if 'current_file' in st.session_state and st.session_state.get('show_content', False):
                    content = read_markdown_file(st.session_state.current_file)
                    st.markdown("""
                        <div class="content-card">
                            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                <button class="favorite-btn">⭐</button>
                                <h3 style="margin: 0;">{}</h3>
                            </div>
                            <div style="color: var(--text);">
                                {}
                            </div>
                        </div>
                    """.format(
                        st.session_state.current_file.replace('.md', '').replace('_', ' '),
                        content
                    ), unsafe_allow_html=True)
                    
                    if st.button("⭐", key=f"fav_{section_idx}_{tab_idx}", help="Favoritar"):
                        user_manager.toggle_favorite(f"section_{section_idx}_{tab_idx}")
                        st.success("Status de favorito atualizado!") 