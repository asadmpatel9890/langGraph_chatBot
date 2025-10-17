from fastapi import FastAPI, HTTPException
import duckdb

app = FastAPI()

DB_FILE = "ecommerce.duckdb"
con = duckdb.connect(DB_FILE)

@app.get("/")
def root():
    return {"message": "ShopEase Mock API is running!"}

@app.get("/orders")
def get_all_orders():
    """Fetch all orders."""
    results = con.execute("SELECT * FROM products").fetchall()
    return [
        {"order_id": r[0], "customer_name": r[1], "product": r[2],
         "status": r[3], "amount": r[4], "city": r[5]}
        for r in results
    ]

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    """Fetch a single order by ID."""
    result = con.execute(
        "SELECT * FROM products WHERE order_id = ?", [order_id]
    ).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_id": result[0],
        "Product Name": result[1],
        "Category": result[2],
        "Price": result[3],
        "Shipping Method": result[-5],
        "Status": result[-1]
    }
