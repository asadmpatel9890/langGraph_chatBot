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


⚙️ Installation
1️⃣ Clone the repository
git clone https://github.com/<your-username>/ShopEase-AI.git
cd ShopEase-AI

2️⃣ Create a virtual environment
python -m venv langapi
source langapi/bin/activate  # (Linux/Mac)
langapi\Scripts\activate     # (Windows)

3️⃣ Install dependencies
pip install -r requirements.txt

🔑 Environment Variables

Create a .env file in the root directory:

GROQ_API_KEY=your_groq_api_key
# or use Azure OpenAI (optional)
# AZURE_OPENAI_API_KEY=your_azure_key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

🧰 Build the Vector Database (RAG Setup)

Run the ingestion script to embed FAQ markdown files into a Chroma DB.

python scripts/ingest_all.py


✅ Output example:

Loaded: faqs_orders.md (14500 chars)

Successfully built Chroma DB with 52 chunks.

🌐 Start the FastAPI Backend

This API provides order data for order-tracking queries.

cd api
uvicorn main:app --reload --port 8001


Example endpoint:

GET http://127.0.0.1:8001/orders/P1060


Response:

{
  "order_id": "P1060",
  "Product_Name": "Blender",
  "Category": "Home Appliances",
  "Price": 1873.52,
  "Shipping_Method": "Standard",
  "Status": "In Godown"
}

💬 Run the Chat Interface

Launch the Streamlit app:

streamlit run streamlit_app.py


🪄 Features:

Persistent conversation memory

API-connected responses

Polite, concise tone

Clear Chat button

Minimalist UI

“Created by Team Phoenix” footer

🧠 Example Conversation

User:

Where is my order P1060?

Assistant:

Here are the details for order P1060:

Field	Details
Product	Blender
Category	Home Appliances
Price	₹1873.52
Shipping Method	Standard
Status	In Godown
🧩 How LangGraph Works
Node	Function
Intent	Detects query type (FAQ / Order / General)
FAQ / RAG	Answers from vector DB (Chroma)
API Node	Calls FastAPI for live order data
General Node	Handles general or fallback chat
Memory Node	Updates context history
🧱 Tech Stack
Layer	Technology
Frontend	Streamlit
LLM Engine	Groq LLM (or Azure OpenAI)
Retrieval DB	Chroma + HuggingFace Embeddings
Backend API	FastAPI + DuckDB
Framework	LangGraph + LangChain
Storage	.env, chroma_db/, data/
