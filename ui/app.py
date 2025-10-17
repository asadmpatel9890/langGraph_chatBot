import streamlit as st
import time
from agent.ecommerce_graph import create_ecom_graph, memory

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="🛍️ ShopEase AI Assistant", page_icon="🤖", layout="wide")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("ShopEase Support 🤖")
    st.markdown("""
    Your AI assistant for:
    - 🧾 Orders
    - 🔄 Returns & Refunds
    - 💳 Payments
    - 🧰 Product Info
    """)
    st.divider()
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        memory.buf.clear()
        st.success("Chat cleared successfully!")

# ---------------- INITIAL SETUP ----------------
if "graph" not in st.session_state:
    st.session_state.graph = create_ecom_graph()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

graph = st.session_state.graph

# ---------------- PROCESS INPUT FIRST ----------------
user_input = st.chat_input("Ask about orders, returns, or policies...")

# If user entered something, process first (before rendering)
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append(("user", user_input))

    # Generate AI response
    with st.spinner("Thinking..."):
        state = {
            "user_input": user_input,
            "memory_text": memory.as_text(),
            "llm_response": "",
            "intent": "",
        }

        result = graph.invoke(state)
        response = result["llm_response"]

    # Add both messages ONCE
    st.session_state.chat_history.append(("assistant", response))

    # Update memory context
    memory.add("user", user_input)
    memory.add("assistant", response)

# ---------------- RENDER CHAT HISTORY ----------------
st.title("🛍️ ShopEase E-Commerce AI Assistant")
st.caption("Powered by LangGraph + REST API + RAG")

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)
