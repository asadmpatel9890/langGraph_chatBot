# 🛍️ ShopEase AI Assistant

> An **AI-powered e-commerce customer support assistant** built using **LangGraph**, **Groq LLM**, **FastAPI**, **Chroma (RAG)**, and **Streamlit**.  
> It answers FAQs, tracks orders via API, and provides human-like, context-aware assistance.

---

## 🚀 Features

✅ Retrieval-Augmented Generation (**RAG**) with Chroma  
✅ Integration with **FastAPI** (for order tracking via DuckDB)  
✅ **LangGraph multi-node architecture** for conversation flow  
✅ **Short-term memory** for multi-turn chat  
✅ **Streamlit UI** for interactive chat interface  
✅ **Sentiment-aware escalation (optional)**  
✅ Built and maintained by **Team Phoenix** 🔥

---

## 🧠 System Architecture

```mermaid
graph TD
A[Streamlit Chat UI] --> B[LangGraph Engine]
B -->|Intent Detection| C[FAQ / RAG Retrieval]
B -->|Order Query| D[FastAPI Order API]
B -->|General Chat| E[LLM Response Node]
C --> F[Memory Node]
D --> F[Memory Node]
E --> F[Memory Node]
F --> G[End]
