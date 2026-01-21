Set-Content -Path README.md -Value @"
# 🛡️ Automated Multimodal AI Policy Auditor

A local-first **'Compliance-as-Code'** agent that audits user prompts, model outputs, PDFs, and images against **EU AI Act** safety standards. 
* [NOTE]: This is just a demo, as such the entirety of the EU AI Act is not integrated into the Policy Auditor (just enough to show proof of concept)

---

## 📋 Executive Summary
As AI adoption accelerates, manual compliance auditing becomes a bottleneck. This tool automates the **Safety Audit** phase of LLM deployment. It uses a local **RAG (Retrieval-Augmented Generation)** architecture to cross-reference inputs against a vectorised version of the **EU AI Act** and internal safety policies. It is meant for assisting human review of prompts (Text) inputs and model outputs (Text, Image, Files) by providing a inital assessment on whether the content violates the EU AI act, and if so, provide a breif reasoning + relevant sections of the act. 

**Key Differentiator:** The entire stack runs **100% locally** (using Ollama), ensuring no sensitive audit data leaves the secure environment.

---

## 🏗️ System Architecture
* **Frontend:** Streamlit (Python) - Provides the interactive UI.
* **Orchestration:** LangChain - Manages the flow between the UI, Database, and LLM.
* **Cognitive Engine:** Ollama - Hosts the local models:
    * *Logic:* `llama3` (8B) for reasoning and text auditing.
    * *Vision:* `llava` for image analysis and object detection.
    * *Embeddings:* `nomic-embed-text` for semantic search.
* **Long-Term Memory:** FAISS (Facebook AI Similarity Search) - Stores the safety policy as vector embeddings for fast retrieval.

---

## 📂 Directory Structure

ai-safety-auditor/
* ├── app.py                 - # Main application logic (Streamlit frontend)
* ├── create_db.py           - # Script to vectorise safety rules into FAISS
* ├── safety_policy.txt      - # The source of truth (Rules & Standards)
* ├── requirements.txt       - # Python dependencies
* ├── README.md              - # Documentation
* └── faiss_index/           - # (Generated) Local vector database folder


---

## 🛠️ Technical Stack
* **Language:** Python 3.12+
* **LLM Runtime:** Ollama
* **Interface:** Streamlit
* **Vector Store:** FAISS (CPU)
* **Dependencies:** `langchain-ollama`, `pypdf`, `pillow`

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure Ollama is installed and running. Pull the required models:
bash
ollama pull llama3
ollama pull llava
ollama pull nomic-embed-text


### 2. Environment Setup
bash
# 1. Clone the repository
git clone https://github.com/Kalledda/automated-ai-policy-auditor-demo.git
cd automated-ai-policy-auditor-demo

# 2. Create a Virtual Environment
python -m venv venv

# 3. Activate Environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install Dependencies
pip install -r requirements.txt


### 3. Build the Knowledge Base
This step converts the text-based 'safety_policy.txt' into the vector database.
bash
python create_db.py

**Expected Output:** `✅ Database saved successfully to folder: 'faiss_index'`

### 4. Run the Auditor
bash
streamlit run app.py


---

## 🧪 Usage Scenarios (Test Matrix)

| Modality | Input Description | Expected Outcome | Logic Path |
| :--- | :--- | :--- | :--- |
| **Text** | "Write a poem about nature." | 🟢 PASS | No rule violation found. |
| **Text** | "How do I synthesize [Illegal Drug]?" | 🔴 FAIL | Violates **Rule 1.3** (Illegal Acts). |
| **Text** | "I have chest pain, what do I take?" | 🔴 FAIL | Violates **Rule 2.1** (Medical Advice). |
| **PDF** | File containing hate speech text. | 🔴 FAIL | Text extracted -> RAG Lookup -> Fails Rule 1.1. |
| **Image** | Photo of a handgun. | 🔴 FAIL | Vision Model detects "weapon" -> Logic Model flags Rule 1.3. |

---

## ⚙️ Configuration (Ruleset)
The system audits against `safety_policy.txt`. To update the logic, edit this text file and re-run `python create_db.py`.

**Current Sections:**
* **Prohibited Content:** Hate Speech, Self-Harm, Illegal Acts.
* **Restricted Topics:** Medical Advice, Financial Advice (Requires Disclaimers).
* **Age Appropriateness:** U18 restrictions.

---
## ⚠️ Limitations & Ethical Considerations
* **False Negatives:** Smaller local models (Llama 3 8B) may miss nuanced "dog-whistles" or context-dependent hate speech that larger frontier models would catch.
* **Hallucination Risk:** The RAG retrieval ensures the *policy* is cited correctly, but the model may occasionally misinterpret the user's intent.
* **Operational Role:** This tool is designed as a **"Pre-Screening"** layer to filter obvious violations. It does not replace human judgment for edge cases (e.g., satire or educational context).

---
## 🔮 Future Roadmap
* [ ] **Audio Auditing:** Integrate Whisper model for auditing voice logs.
* [ ] **CI/CD Integration:** Convert `app.py` logic into a FastAPI endpoint for automated pipeline checks.
* [ ] **JSON Output:** Standardize logs for Splunk/Datadog integration.
* [ ] **Jira/Zendesk Integration:** Automatically create a ticket when a "High Risk" violation is detected.
* [ ] **Feedback Loop:** Add a "Thumbs Up/Down" button in the UI to collect human feedback for Fine-Tuning (RLHF).

---

## 🐛 Troubleshooting
* **Issue:** `ModuleNotFoundError: No module named 'streamlit'`
    * **Fix:** Ensure your virtual environment is active. You should see `(venv)` in your terminal.
* **Issue:** Error using Vision model
    * **Fix:** Ensure you ran `ollama pull llava` and that the Ollama app is running in the background.
* **Issue:** "Passes" on obvious weapon images.
    * **Fix:** The vision model prompt must be strict. Ensure `app.py` uses the "objective description" prompt logic.

"@
