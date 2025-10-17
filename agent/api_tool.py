import requests

def get_order_status(order_id: str):
    """Call external REST API to get order details."""
    url = f"http://localhost:8001/orders/{order_id}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}
