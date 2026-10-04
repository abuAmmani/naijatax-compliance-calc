import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_tax_document():
    pdf_path = "finance_act.pdf"
    
    # 1. Gracefully check if the user placed the file in the workspace directory
    if not os.path.exists(pdf_path):
        print(f"❌ Error: Please download the Nigerian Finance Act PDF and save it as '{pdf_path}' in this folder.")
        return None

    print(f"⏳ Step 1: Loading official {pdf_path} text lines...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} pages from the tax document.")

    # 2. Split the tax law document into highly precise, clause-sized chunks
    print("⏳ Step 2: Splitting tax text into precise compliance sub-sections...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,       # Smaller chunk size to avoid blending distinct tax rules together
        chunk_overlap=120,     # Overlap to maintain contextual continuity across legal sentences
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Successfully generated {len(chunks)} searchable tax text chunks.")
    return chunks

if __name__ == "__main__":
    process_tax_document()
