from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# 1. Setup the Embedding Model
embeddings = OllamaEmbeddings(model="nomic-embed-text")

def create_vector_db():
    print("⏳ Loading safety policy...")
    loader = TextLoader("safety_policy.txt")
    documents = loader.load()

    # 2. Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"📄 Split policy into {len(chunks)} chunks.")

    # 3. Create the FAISS Vector Database
    print("💾 Creating FAISS Vector Database...")
    vector_db = FAISS.from_documents(chunks, embeddings)
    
    # 4. Save it locally
    vector_db.save_local("faiss_index")
    print("✅ Database saved successfully to folder: 'faiss_index'")

if __name__ == "__main__":
    create_vector_db()