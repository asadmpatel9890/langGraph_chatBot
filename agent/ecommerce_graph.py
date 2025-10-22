import os
import re
import requests
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from agent.memory import ShortMemory
from agent.intent_detector import detect_intent
#from agent.api_tool import get_order_status
from agent.rag_chain import RagService
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json
from typing import Dict, Any, List


load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = """
You are a polite and helpful customer support assistant for an e-commerce company.
You can answer questions using FAQs or API data.
Be concise, empathetic, and accurate.
When answering order-related questions,  never hallucinate and give the ouyput using api data only
Give api output as it is
.
"""

memory = ShortMemory(max_turns=10)

class ChatState(TypedDict):
    user_input: str
    llm_response: str
    memory_text: str
    intent: str


def create_ecom_graph():
    llm = ChatGroq(
        groq_api_key=api_key,
        temperature=0.3,
        model_name="openai/gpt-oss-120b"
    )

    rag = RagService().make_chain(llm)
    graph = StateGraph(ChatState)

    # --- Node 1: Intent detection ---
    def intent_node(state: ChatState) -> Dict[str, Any]:
        intent = detect_intent(state["user_input"])
        if intent not in ["faq", "order_query", "general"]:
            intent = "general"
        return {"intent": intent}

    # --- Node 2: FAQ / RAG Node ---
    def faq_node(state: ChatState) -> Dict[str, Any]:
        answer = rag.invoke(state["user_input"])
        return {"llm_response": answer}
    

    # def get_order_status(order_id: str):
    #     """Call external REST API to get order details."""
    #     url = f"http://127.0.0.1:8001/orders/{order_id}"
    #     try:
    #         res = requests.get(url)
    #         res.raise_for_status()
    #         return res.json()
    #     except Exception as e:
    #         return {"error": str(e)}


    # --- Node 3: API Node ---
    def api_node(state: Dict[str, Any]) -> Dict[str, Any]:
        print(f"DEBUG: User input: {state['user_input']}")

        def get_order_status(order_id: str):
            """Call external REST API to get order details."""
            url = f"http://127.0.0.1:8001/orders/{order_id}"
            try:
                res = requests.get(url, timeout=5)
                res.raise_for_status()
                return res.json()
            except Exception as e:
                return {"error": str(e), "order_id": order_id}

        # 1) Extract ALL order IDs (e.g., P2941, 101, AB123)
        # Pattern: optional leading letters + digits, separated by space/comma/and
        order_ids: List[str] = re.findall(r"\b[A-Z]*\d+\b", state["user_input"].upper())

        if not order_ids:
            return {"llm_response": "Please provide one or more order IDs (e.g., P2941, 101)."}

        print(f"DEBUG: Extracted order_ids: {order_ids}")

    # 2) Query each order and build per-order summaries
        summaries = []
        for oid in order_ids:
            data = get_order_status(oid)
            print(f"DEBUG: API response for {oid}: {data}")

            if "error" in data:
                summaries.append(f"- {oid}: Could not fetch info ({data['error']})")
                continue

            # Adapt keys to your API response
            api_order_id = data.get("order_id", oid)
            product_name = data.get("Product_Name", "Unknown")
            category = data.get("Category", "N/A")
            price = data.get("Price", "N/A")
            shipping_method = data.get("Shipping_Method", "Unknown")
            status = data.get("Status", "Unknown")

            summaries.append(
                f"- Order {api_order_id}: {status.title()} | {product_name} ({category}) | "
                f"Price: ${price} | Shipping: {shipping_method}"
            )

        # 3) Aggregate response
        header = "Here are the details for your orders:\n"
        response = header + "\n".join(summaries)
        result1 = llm.invoke(f"Transform the following {response} into Table  format,Add little formality befor and after representing data")
        return {"llm_response": result1.content}

    # --- Node 4: General / fallback ---
    def general_node(state: ChatState) -> Dict[str, Any]:
        prompt = f"""
        {SYSTEM_PROMPT}

        Conversation so far:
        {state.get('memory_text', '')}

        User: {state['user_input']}
        Assistant:
        """
        result = llm.invoke(prompt)
        return {"llm_response": result.content}

    # --- Node 5: Memory update ---
    def memory_node(state: ChatState) -> Dict[str, Any]:
        memory.add("user", state["user_input"])
        memory.add("assistant", state["llm_response"])
        return {"memory_text": memory.as_text()}

    # Register nodes
    graph.add_node("intent", intent_node)
    graph.add_node("faq", faq_node)
    graph.add_node("api", api_node)
    graph.add_node("general", general_node)
    graph.add_node("memory", memory_node)

    # Flow
    graph.set_entry_point("intent")
    graph.add_conditional_edges(
        "intent",
        lambda s: s["intent"],
        {
            "faq": "faq",
            "order_query": "api",
            "general": "general",
        },
    )

    graph.add_edge("faq", "memory")
    graph.add_edge("api", "memory")
    graph.add_edge("general", "memory")
    graph.add_edge("memory", END)

    return graph.compile()
