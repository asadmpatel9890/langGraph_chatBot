## 🧠 FAQ Vector Database Builder (`scripts/ingest_all.py`)

This script builds a **unified Chroma vector database** from all FAQ markdown files in the `/data` directory.  
It powers the **Retrieval-Augmented Generation (RAG)** system used by the **ShopEase AI Assistant** for answering FAQ and policy-related queries.

---

### 🧩 Purpose

The goal of this script is to:
- Preprocess all Markdown (`.md`) FAQ and policy files  
- Chunk them into smaller text segments for better semantic retrieval  
- Generate embeddings using a sentence-transformer model  
- Store them efficiently inside a **Chroma vector store**

These embeddings are later used by your chatbot’s RAG pipeline for accurate, context-aware answers.

---

### 🗂️ Directory Structure

