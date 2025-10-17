"""
scripts/ingest_all.py
-------------------------------------
Builds a unified Chroma vector database
from all FAQ markdown files in /data.
Handles encoding safely and performs
recursive text chunking for optimal RAG retrieval.
-------------------------------------
Usage:
    python scripts/ingest_all.py
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# -------------------------------------
# CONFIGURATION
# -------------------------------------
DATA_DIR = "data/"
DB_DIR = "chroma_db"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# -------------------------------------
# SAFE FILE LOADER
# -------------------------------------
def load_markdown_files(data_dir: str):
    """Safely read all markdown files (UTF-8 with Latin-1 fallback)."""
    docs = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(data_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    text = f.read()
            docs.append(
                Document(page_content=text, metadata={"source": filename})
            )
            print(f"Loaded: {filename} ({len(text)} chars)")
    return docs

# -------------------------------------
# INGESTION PIPELINE
# -------------------------------------
def build_vector_db():
    print("Starting FAQ ingestion process...")
    docs = load_markdown_files(DATA_DIR)

    if not docs:
        raise ValueError(f"No .md files found in {DATA_DIR}")

    print(f"Loaded {len(docs)} FAQ documents.")
    print("Splitting text into smaller chunks...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    split_docs = splitter.split_documents(docs)
    print(f"Created {len(split_docs)} text chunks.")

    print(f"Generating embeddings using {EMBED_MODEL}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print(f" Creating / Updating Chroma database at '{DB_DIR}'...")
    vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory=DB_DIR
    )

    vectordb.persist()
    print(f"Successfully built Chroma DB with {len(split_docs)} chunks.")
    print(f" Database saved to: {os.path.abspath(DB_DIR)}")


# -------------------------------------
# MAIN EXECUTION
# -------------------------------------
if __name__ == "__main__":
    try:
        build_vector_db()
        print("\n Ingestion complete. Your FAQ vector DB is ready for LangGraph!")
    except Exception as e:
        print(f" Error during ingestion: {e}")
