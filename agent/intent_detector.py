def detect_intent(user_message: str) -> str:
    msg = user_message.lower()
    if any(k in msg for k in ["order", "status", "track", "shipment", "delivery"]):
        return "order_query"
    if any(k in msg for k in ["policy", "return", "refund"]):
        return "faq"
    return "general"