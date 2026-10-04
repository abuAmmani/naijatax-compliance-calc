import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from process_tax_doc import process_tax_document

def create_tax_vector_database():
    # 1. Fetch your 278 split tax chunks from our processor script
    chunks = process_tax_document()
    if not chunks:
        print("❌ Database creation aborted: Tax document chunks missing.")
        return

    persist_directory = "tax_vector_db"
    
    # 2. Use our free, local Hugging Face embedding model
    print("⏳ Step 3: Initializing free local HuggingFace Embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 3. Generate vectors and index them into ChromaDB locally
    print(f"⏳ Step 4: Storing {len(chunks)} tax clauses inside ChromaDB at '{persist_directory}'...")
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("✅ Local tax database created successfully! Your new RAG memory is locked in.")
    return vector_db

if __name__ == "__main__":
    create_tax_vector_database()
