import duckdb
import pandas as pd
import os

DB_FILE = "ecommerce.duckdb"
DATA_FILE = "sample.xlsx"  # or "data/products.csv"

# Connect to DuckDB
con = duckdb.connect(DB_FILE)
print(f"✅ Connected to {DB_FILE}")

# Create table
con.execute("""
CREATE TABLE IF NOT EXISTS products (
    order_id VARCHAR,
    product_name VARCHAR,
    category VARCHAR,
    price DOUBLE,
    discount DOUBLE,
    tax_rate DOUBLE,
    stock_level INTEGER,
    supplier_id VARCHAR,
    customer_age_group VARCHAR,
    customer_location VARCHAR,
    customer_gender VARCHAR,
    shipping_cost DOUBLE,
    shipping_method VARCHAR,
    return_rate DOUBLE,
    seasonality VARCHAR,
    popularity_index DOUBLE,
    status VARCHAR
)
""")

# Load data (either Excel or CSV)
if os.path.exists(DATA_FILE):
    if DATA_FILE.endswith(".xlsx"):
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.read_csv(DATA_FILE)

    # Load into DuckDB
    con.execute("DELETE FROM products")  # optional: clear old data
    con.register("df_view", df)
    con.execute("INSERT INTO products SELECT * FROM df_view")
    print(f"✅ Loaded {len(df)} products from {DATA_FILE}")
else:
    print(f"⚠️ Data file not found: {DATA_FILE}")

# Preview
print("📦 Sample rows:")
print(con.execute("SELECT * FROM products LIMIT 5").fetchdf())

con.close()
print("🎉 Done!")
