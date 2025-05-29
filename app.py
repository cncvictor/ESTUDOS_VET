import streamlit as st
import os
import markdown
from pathlib import Path
import random

# Configuração da página
st.set_page_config(
    page_title="Resumos de Anestesiologia",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMarkdown {
        text-align: justify;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    h1 {
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
    }
    h2 {
        color: #2563EB;
        margin-top: 1.5rem;
        padding: 0.5rem;
        background: #F0F7FF;
        border-radius: 5px;
    }
    h3 {
        color: #3B82F6;
        margin-top: 1rem;
    }
    .stButton button {
        width: 100%;
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #1E40AF;
    }
    .css-1d391kg {
        padding: 1rem;
    }
    .block-container {
        padding: 2rem;
    }
    .card {
        padding: 2rem;
        border-radius: 10px;
        background: #F8FAFC;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .case-study {
        background: #EFF6FF;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #2563EB;
    }
    </style>
    """, unsafe_allow_html=True)

def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

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
    st.title("Navegação")
    
    # Modos principais
    main_mode = st.radio(
        "Modo de Estudo:",
        ["📖 Leitura Normal", "🎴 Flash Cards", "🏥 Casos Clínicos"],
        key="main_mode"
    )
    
    if main_mode == "🎴 Flash Cards":
        st.markdown("### Opções de Flash Cards")
        card_mode = st.radio(
            "Tipo de Estudo:",
            ["Sequencial", "Aleatório"],
            key="card_mode"
        )
        show_answer = st.checkbox("Mostrar Resposta", key="show_answer_sidebar")
    
    elif main_mode == "🏥 Casos Clínicos":
        st.markdown("### Opções de Casos")
        case_mode = st.radio(
            "Visualização:",
            ["Lista Completa", "Caso por Caso"],
            key="case_mode"
        )
    
    # Campo de busca
    search = st.text_input("🔍 Buscar...", key="search_input")

# Conteúdo principal
if main_mode == "🎴 Flash Cards":
    st.markdown("## 🎴 Modo Flash Cards")
    
    # Carregar flash cards
    all_cards = []
    flash_card_files = ["FlashCards_Anestesiologia.md"]
    
    for file in flash_card_files:
        if os.path.exists(file):
            content = read_markdown_file(file)
            cards = extract_flash_cards(content)
            all_cards.extend(cards)
    
    if all_cards:
        # Inicializar o índice do card na primeira vez
        if "current_card_idx" not in st.session_state:
            st.session_state.current_card_idx = 0
        
        # Controles de navegação
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if st.button("⬅️ Anterior", key="btn_anterior"):
                st.session_state.current_card_idx = max(0, st.session_state.current_card_idx - 1)
        
        with col2:
            if st.button("➡️ Próximo", key="btn_proximo"):
                st.session_state.current_card_idx = min(len(all_cards) - 1, st.session_state.current_card_idx + 1)
        
        with col3:
            if st.button("🔄 Aleatório", key="btn_aleatorio"):
                st.session_state.current_card_idx = random.randint(0, len(all_cards) - 1)
        
        # Mostrar progresso
        st.progress((st.session_state.current_card_idx + 1) / len(all_cards))
        st.markdown(f"Card {st.session_state.current_card_idx + 1} de {len(all_cards)}")
        
        # Exibir card atual
        current_card = all_cards[st.session_state.current_card_idx]
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Questão:")
        st.info(current_card["question"])
        
        # Botão para mostrar/ocultar resposta
        if st.button("👀 Mostrar Resposta", key=f"show_answer_{st.session_state.current_card_idx}"):
            st.markdown("### ✅ Resposta:")
            st.success(current_card["answer"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Nenhum flash card encontrado. Verifique o arquivo FlashCards_Anestesiologia.md")

elif main_mode == "🏥 Casos Clínicos":
    st.markdown("## 🏥 Casos Clínicos")
    
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
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Nenhum caso clínico encontrado. Verifique o arquivo Casos_Clinicos_ENADE.md")

else:  # Modo Leitura Normal
    for section_idx, (section, categories) in enumerate(CONTENT_STRUCTURE.items()):
        st.markdown(f"## {section}")
        
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
                        if st.button(f"📄 {title}", key=f"btn_{section_idx}_{tab_idx}_{idx}"):
                            st.session_state.current_file = file
                            st.session_state.show_content = True
                
                if 'current_file' in st.session_state and st.session_state.get('show_content', False):
                    st.markdown("---")
                    content = read_markdown_file(st.session_state.current_file)
                    st.markdown(content)

# Rodapé com estatísticas
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estatísticas")
total_files = sum(len(files) for categories in CONTENT_STRUCTURE.values() for files in categories.values())
total_categories = sum(len(categories) for categories in CONTENT_STRUCTURE.values())
st.sidebar.markdown(f"- Arquivos: **{total_files}**")
st.sidebar.markdown(f"- Categorias: **{total_categories}**")
st.sidebar.markdown(f"- Seções: **{len(CONTENT_STRUCTURE)}**") 