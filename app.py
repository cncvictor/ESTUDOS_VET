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
    /* Reset e Variáveis */
    :root {
        --primary: #3B82F6;
        --background: #F9FAFB;
        --surface: #FFFFFF;
        --text: #111827;
        --text-secondary: #4B5563;
        --border: #E5E7EB;
    }

    /* Estilos Globais */
    .stApp {
        background: var(--background) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
        -webkit-box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        -moz-box-shadow: 2px 0 5px rgba(0,0,0,0.05);
        box-shadow: 2px 0 5px rgba(0,0,0,0.05);
    }

    /* Header */
    .app-header {
        display: -webkit-flex;
        display: -moz-flex;
        display: -ms-flex;
        display: flex;
        -webkit-align-items: center;
        -moz-align-items: center;
        -ms-align-items: center;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: var(--primary);
        color: white;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    /* Métricas */
    .metrics-grid {
        display: -ms-grid;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
    }

    .metric-card {
        background: var(--surface);
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        -webkit-box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        -moz-box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Navegação */
    .nav-section {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        -webkit-transition: all 0.3s ease;
        -moz-transition: all 0.3s ease;
        transition: all 0.3s ease;
    }

    /* Conteúdo */
    .content-section {
        background: var(--surface);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid var(--border);
        -webkit-box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        -moz-box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Modal */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        -webkit-backdrop-filter: blur(5px);
        backdrop-filter: blur(5px);
    }

    .modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        -webkit-transform: translate(-50%, -50%);
        -moz-transform: translate(-50%, -50%);
        background: var(--surface);
        padding: 2rem;
        border-radius: 12px;
        width: 90%;
        max-width: 800px;
        max-height: 90vh;
        overflow-y: auto;
        z-index: 1001;
        -webkit-box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        -moz-box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Responsividade */
    @media (max-width: 768px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .modal {
            width: 95%;
            padding: 1rem;
        }
    }

    /* Botões */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        -webkit-transition: all 0.2s ease;
        -moz-transition: all 0.2s ease;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        -webkit-transform: translateY(-1px);
        -moz-transform: translateY(-1px);
        transform: translateY(-1px);
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
    "📖 Apostila Completa": {
        "Apostila de Anestesiologia": ["Apostila_Anestesiologia.md"],
    },
    "📚 Material Base": {
        "Anestésicos Gerais": ["Anestesicos_Gerais.md", "Anestesicos_Gerais_IV.md", "Anestesia_Inalatoria.md", "EGG_Anestesico.md"],
        "Anestésicos Locais": ["Anestesicos_Locais.md", "Anestesicos_Locais_Detalhado.md", "Anestesia_Local_Intravenosa.md"],
        "Medicação Pré-Anestésica": ["Medicacao_Pre_Anestesica.md", "MPA_Completo.md", "Hipnoanalgesicos_MPA.md", "MPA_Fenotiazinicos_Benzodiazepinicos.md"],
    },
    "💊 Farmacologia": {
        "Analgésicos": ["Analgesia_Opioides.md", "Opioides.md", "AINES.md", "Analgesia_AINEs.md"],
        "Adjuvantes": ["Adjuvantes_Analgesicos.md", "Alfa2_Agonistas.md", "Gabapentina.md"],
        "Outros Fármacos": ["Anticolinergicos.md", "Bloqueadores_Adrenergicos.md", "Farmacos_Simpaticos.md", "Farmacos_Parassimpaticos.md"],
        "Antibióticos": ["Antibioticos_Veterinaria.md"]
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
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: var(--surface); border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);">
        <h1 style="margin: 0;">📚 Banco de Estudos - Anestesiologia</h1>
        <div style="display: flex; gap: 1rem;">
            <button class="nav-button" onclick="window.history.back()">⬅️ Voltar</button>
            <button class="nav-button" onclick="location.reload()">🔄 Atualizar</button>
        </div>
    </div>
""", unsafe_allow_html=True)

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
                <span class="metric-value">{}</span>
                <span class="metric-label">ESTUDADOS</span>
            </div>
            <div class="metric-card">
                <span class="metric-value">{}</span>
                <span class="metric-label">NOTAS</span>
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

# Função para criar menu expansível com ícones
def create_expandable_menu(title, content_dict, icon):
    with st.expander(f"{icon} {title}", expanded=False):
        for category, files in content_dict.items():
            st.markdown(f"### 📂 {category}")
            for file in files:
                if st.button(
                    f"📄 {file.replace('.md', '').replace('_', ' ')}",
                    key=f"btn_{title}_{category}_{file}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.current_file = file
                    st.session_state.show_modal = True
                    st.session_state.current_section = title
                    st.session_state.current_category = category

# Conteúdo principal
if main_mode == "📚 Material":
    # Criar tabs para as seções principais
    sections = list(CONTENT_STRUCTURE.keys())
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(sections)
    
    # Função para mostrar conteúdo da categoria
    def show_category_content(categories):
        for category, files in categories.items():
            with st.expander(f"📂 {category}", expanded=False):
                for file in files:
                    if st.button(
                        f"📄 {file.replace('.md', '').replace('_', ' ')}",
                        key=f"btn_{category}_{file}",
                        use_container_width=True
                    ):
                        st.session_state.current_file = file
                        st.session_state.show_content = True
                        return True
        return False

    # Mostrar conteúdo em cada tab
    with tab1:
        show_category_content(CONTENT_STRUCTURE[sections[0]])
    with tab2:
        show_category_content(CONTENT_STRUCTURE[sections[1]])
    with tab3:
        show_category_content(CONTENT_STRUCTURE[sections[2]])
    with tab4:
        show_category_content(CONTENT_STRUCTURE[sections[3]])
    with tab5:
        show_category_content(CONTENT_STRUCTURE[sections[4]])
    with tab6:
        show_category_content(CONTENT_STRUCTURE[sections[5]])

    # Exibir conteúdo quando um arquivo é selecionado
    if 'current_file' in st.session_state and st.session_state.get('show_content', False):
        with st.container():
            # Cabeçalho
            st.markdown("---")
            st.markdown(f"## 📄 {st.session_state.current_file.replace('.md', '').replace('_', ' ')}")
            
            # Botões de ação
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📝 Anotações"):
                    st.session_state.show_notes = True
            with col2:
                if st.button("⭐ Favoritar"):
                    user_manager.toggle_favorite(st.session_state.current_file)
            with col3:
                if st.button("🖨️ Imprimir"):
                    st.markdown(f'<script>window.print()</script>', unsafe_allow_html=True)
            with col4:
                if st.button("❌ Fechar"):
                    st.session_state.show_content = False
                    st.experimental_rerun()
            
            # Conteúdo
            content = read_markdown_file(st.session_state.current_file)
            st.markdown(content)
            
            # Área de anotações
            if st.session_state.get('show_notes', False):
                with st.expander("📝 Suas Anotações", expanded=True):
                    note = st.text_area("", key="note_text")
                    if st.button("💾 Salvar"):
                        user_manager.add_note(st.session_state.current_file, note)
                        st.success("✅ Anotação salva com sucesso!")
                        st.session_state.show_notes = False

elif main_mode == "🧠 Flash Cards":
    st.markdown("""
        <div class="content-section">
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
            <div class="content-section" style="display: flex; gap: 1rem; align-items: center; justify-content: space-between;">
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
            <div class="content-section">
                <h3>📝 Questão</h3>
                <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 12px; color: var(--text); margin: 1rem 0;">
                    {}
                </div>
            </div>
        """.format(current_card["question"]), unsafe_allow_html=True)
        
        if st.button("👀 Mostrar Resposta", key=f"show_answer_{st.session_state.current_card_idx}", use_container_width=True):
            st.markdown("""
                <div class="content-section">
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
        <div class="content-section">
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
        <div class="content-section">
            <h3>📚 Material de Estudo</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Conteúdo completo de anestesiologia veterinária
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Criar menus expansíveis para cada seção
    for section, categories in CONTENT_STRUCTURE.items():
        create_expandable_menu(section, categories, "📁")

    # Modal para exibir conteúdo
    if 'show_modal' in st.session_state and st.session_state.show_modal:
        modal_container = st.container()
        with modal_container:
            st.markdown("""
                <div class="modal-overlay"></div>
                <div class="modal">
                    <button class="modal-close" onclick="this.closest('.modal').remove(); this.closest('.modal-overlay').remove();">×</button>
            """, unsafe_allow_html=True)
            
            content = read_markdown_file(st.session_state.current_file)
            st.markdown(f"## {st.session_state.current_file.replace('.md', '').replace('_', ' ')}")
            st.markdown(content)
            
            if st.button("Fechar", key="close_modal"):
                st.session_state.show_modal = False
                st.experimental_rerun()
            
            st.markdown("</div>", unsafe_allow_html=True) 