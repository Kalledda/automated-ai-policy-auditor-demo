import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import ollama
import PyPDF2
from PIL import Image
import io

# --- CONFIGURATION ---
EMBEDDING_MODEL = "nomic-embed-text"
TEXT_MODEL = "llama3"
VISION_MODEL = "llava"  # Make sure you ran: ollama pull llava
VECTOR_DB_PATH = "faiss_index"

# --- PAGE SETUP ---
st.set_page_config(page_title="AI Safety Auditor V2", page_icon="🛡️", layout="wide")
st.title("🛡️ Multimodal AI Policy Auditor")
st.markdown("Audit **User Prompts**, **Model Outputs**, **PDFs**, or **Images** against the Safety Policy.")

# --- LOAD DATABASE ---
@st.cache_resource
def load_knowledge_base():
    try:
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        db = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        return None

knowledge_base = load_knowledge_base()

if not knowledge_base:
    st.error("❌ Database not found. Please run 'create_db.py' first.")
    st.stop()
else:
    with st.sidebar:
        st.success("✅ Policy Database Active")
        st.info("Current Policy: EU AI Act / Internal Rules")

# --- HELPER FUNCTIONS ---
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def analyze_image(image_bytes):
    """Sends image to Llava to check for visual safety violations"""
    try:
        response = ollama.chat(model=VISION_MODEL, messages=[
            {
                'role': 'user',
                'content': 'Describe the physical objects and actions in this image in strict detail. Be objective and factual. Do not minimize or soften the description. If there is a weapon, state clearly what kind of weapon it is.',                'images': [image_bytes]
            }
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error using Vision model: {str(e)}. (Did you run 'ollama pull llava'?)"

def run_audit(content_to_audit, context_label="Content"):
    with st.spinner(f"Auditing {context_label}..."):
        # 1. Retrieve Rules
        retrieved_docs = knowledge_base.similarity_search(content_to_audit, k=3)
        rules_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # 2. System Prompt (The "Judge")
        system_prompt = f"""
        You are an AI Safety Compliance Officer.
        Audit the following CONTENT against the SAFETY RULES.
        
        SAFETY RULES:
        {rules_text}
        
        INSTRUCTIONS:
        - Determine if the CONTENT violates the rules.
        - If text is safe, start with "🟢 PASS".
        - If unsafe, start with "🔴 FAIL".
        - Cite specific rule numbers.
        """
        
        # 3. Call Llama 3
        response = ollama.chat(model=TEXT_MODEL, messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"CONTENT TO AUDIT: {content_to_audit}"}
        ])
        
        return response['message']['content'], rules_text

# --- UI TABS ---
tab1, tab2, tab3 = st.tabs(["📝 Text Audit", "📄 Document Audit (PDF)", "🖼️ Image Audit"])

# TAB 1: TEXT (Prompts OR Outputs)
with tab1:
    audit_mode = st.radio("What are we auditing?", ["User Prompt", "Model Output"])
    
    col1, col2 = st.columns(2)
    with col1:
        text_input = st.text_area(f"Enter {audit_mode}:", height=200)
    
    with col2:
        if st.button("Run Text Audit", use_container_width=True):
            if text_input:
                result, context = run_audit(text_input, audit_mode)
                if "FAIL" in result:
                    st.error(result)
                else:
                    st.success(result)
                with st.expander("View Retrieved Rules"):
                    st.write(context)
            else:
                st.warning("Please enter text.")

# TAB 2: PDF
with tab2:
    uploaded_pdf = st.file_uploader("Upload Policy or Chat Log (PDF)", type="pdf")
    if uploaded_pdf and st.button("Audit PDF"):
        # 1. Extract Text
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        st.info(f"Extracted {len(pdf_text)} characters from PDF.")
        
        # 2. Audit
        result, context = run_audit(pdf_text, "PDF Content")
        
        if "FAIL" in result:
            st.error(result)
        else:
            st.success(result)

# TAB 3: IMAGE
with tab3:
    st.write("Uses **Llava** (Vision Model) to scan images for prohibited symbols/actions.")
    uploaded_img = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_img and st.button("Audit Image"):
        # Convert to bytes for Ollama
        img_bytes = uploaded_img.getvalue()
        
        # 1. Vision Analysis
        with st.spinner("👀 Vision Model analyzing image content..."):
            visual_description = analyze_image(img_bytes)
            st.text_area("Vision Model Description:", visual_description, height=100)
        
        # 2. Safety Audit on the Description
        # We audit the *description* of the image against the text policy
        result, context = run_audit(visual_description, "Image Description")
        
        if "FAIL" in result:
            st.error(result)
        else:
            st.success(result)