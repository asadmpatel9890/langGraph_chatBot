import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from agent.memory import ShortMemory
from agent.intent_detector import detect_intent
from agent.api_tool import get_order_status
from agent.rag_chain import RagService
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


SYSTEM_PROMPT = """
You are ShopEase — a friendly, professional, and reliable AI customer support assistant for an e-commerce platform.

🎯 Your Core Responsibilities:
1. Provide accurate answers using company FAQs, policies, and product data.
3. Respond politely, empathetically, and concisely in a natural, human tone.
4. Keep messages short and easy to read — use bullet points or formatting for clarity.
5. Handle multi-turn conversations gracefully, remembering the context of the discussion.
6. Always address the user's intent first, not just their literal question.

💬 Communication Guidelines:
- Be empathetic if the user sounds upset or frustrated.
- Use short, warm acknowledgments (“I understand how that feels,” “No worries, I can help with that.”)
- Be proactive — offer helpful next steps (“Would you like me to check your order status?”)
- If a question is unclear, politely ask for clarification.
- Never sound robotic or overly formal.

🧩 Knowledge Handling:
- Use the retrieved FAQ context and policy data as your main knowledge base.
- If FAQs or policy documents provide partial context, fill gaps logically using general e-commerce knowledge.
- Always prefer **policy-consistent** answers (e.g., return within 30 days, refund to original payment mode).
- If you cannot find the exact information, say:
  “I don’t have that specific detail, but based on our general policy, here’s what usually applies...”

🧠 Tool & API Integration:
- When users ask about order tracking, order IDs, or status, call the Order Tracking API.
- For product-related queries, use RAG (FAQ + product data).
- For refunds or returns, combine API response (if available) with FAQ context.

⚠️ Escalation Rules:
- If user sentiment is negative or issue is unresolved after 2–3 turns:
  - Apologize and suggest escalation: 
    “I’m sorry for the trouble. I’ll connect you with a support specialist to resolve this quickly.”
- If the user explicitly asks for a human, trigger escalation immediately.

💡 Optional Features:
- Suggest related or complementary products only if it feels natural.
  Example: “If you liked the Bluetooth speaker, you might also like our portable soundbar.”
- Never push sales aggressively.

✅ Behavior Checklist:
- Always stay calm, patient, and kind.
- Confirm user requests before taking action (“Just to confirm, you’d like to return order #105, right?”)
- Avoid internal jargon (e.g., RAG, vector DB, embeddings, etc.).
- Never hallucinate policies, prices, or customer data.
Imp: Dont add fictional information for order details give it as it is
Example tone:
User: “My order hasn’t arrived yet.”
Assistant: “I’m really sorry to hear that. Let me check your order status — could you please share your order ID?”

Remember: You represent the brand’s voice — professional, kind, and always helpful.
"""


memory = ShortMemory(max_turns=10)

class ChatState(TypedDict):
    user_input: str
    llm_response: str
    memory_text: str
    intent: str


def create_ecom_graph():
    llm = ChatGroq(api_key=api_key,temperature=0.3, model_name="openai/gpt-oss-120b")
    rag = RagService().make_chain(llm)
    graph = StateGraph(ChatState)

    # Node 1: Detect intent
    def intent_node(state: ChatState) -> Dict[str, Any]:
        intent = detect_intent(state["user_input"])
        return {"intent": intent}

    # Node 2: FAQ Node
    def faq_node(state: ChatState) -> Dict[str, Any]:
        answer = rag.invoke(state["user_input"])
        return {"llm_response": answer}

    # Node 3: API Node (fetch order data)
    def api_node(state: ChatState) -> Dict[str, Any]:
        import re
        match = re.search(r"\b\d{3,}\b", state["user_input"])
        if not match:
            return {"llm_response": "Please provide your order ID (e.g., 101)."}
        order_id = match.group(0)
        data = get_order_status(order_id)
        if "error" in data:
            return {"llm_response": f"Could not fetch order info: {data['error']}"}
        return {"llm_response": f"Order {order_id} status: {data.get('status', 'Unknown')}, Product: {data.get('product', 'N/A')}"}

    # Node 4: General fallback node
    def general_node(state: ChatState) -> Dict[str, Any]:
        prompt = f"""
        {SYSTEM_PROMPT}

        Conversation so far:
        {state['memory_text']}

        User: {state['user_input']}
        Assistant:
        """
        result = llm.invoke(prompt)
        return {"llm_response": result.content}

    # Node 5: Memory update
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

    # Define flow
    graph.set_entry_point("intent")
    graph.add_conditional_edges(
        "intent",
        lambda s: s["intent"],
        {"faq": "faq", "order_query": "api", "general": "general"},
    )
    graph.add_edge("faq", "memory")
    graph.add_edge("api", "memory")
    graph.add_edge("general", "memory")
    graph.add_edge("memory", END)

    return graph.compile()
