"""
=============================================================================
Project: E-Commerce Customer Lifecycle & Revenue Intelligence System
Script: Data Cleaning, Integrity Checks & Star Schema Validation
Author: Pasupuleti Mahima
=============================================================================
"""
import os
import pandas as pd
import numpy as np

def clean_and_validate_data(raw_dir, processed_dir):
    os.makedirs(processed_dir, exist_ok=True)
    print("=" * 60)
    print(" PHASE 2: DATA CLEANING & VALIDATION PIPELINE")
    print("=" * 60)

    # 1. Load Products
    df_products = pd.read_csv(os.path.join(raw_dir, "dim_products.csv"))
    print(f"\n[1] Processing Products (Rows: {len(df_products)})...")
    # Check nulls and price validity
    assert df_products['unit_price'].min() > 0, "Error: Product price <= 0 found!"
    assert df_products['product_id'].is_unique, "Error: Duplicate product IDs found!"
    # Add Profit Margin column
    df_products['profit_margin'] = round(df_products['unit_price'] - df_products['unit_cost'], 2)
    df_products['profit_margin_pct'] = round((df_products['profit_margin'] / df_products['unit_price']) * 100, 2)
    df_products.to_csv(os.path.join(processed_dir, "dim_products_cleaned.csv"), index=False)
    print(" -> Saved: dim_products_cleaned.csv (Added profit_margin & profit_margin_pct)")

    # 2. Load Customers
    df_customers = pd.read_csv(os.path.join(raw_dir, "dim_customers.csv"))
    print(f"\n[2] Processing Customers (Rows: {len(df_customers)})...")
    assert df_customers['customer_id'].is_unique, "Error: Duplicate customer IDs found!"
    df_customers['signup_date'] = pd.to_datetime(df_customers['signup_date'])
    df_customers['signup_year_month'] = df_customers['signup_date'].dt.to_period('M').astype(str)
    df_customers.to_csv(os.path.join(processed_dir, "dim_customers_cleaned.csv"), index=False)
    print(" -> Saved: dim_customers_cleaned.csv (Normalized dates and added signup cohort month)")

    # 3. Load Orders
    df_orders = pd.read_csv(os.path.join(raw_dir, "fact_orders.csv"))
    print(f"\n[3] Processing Orders (Rows: {len(df_orders)})...")
    df_orders['order_purchase_timestamp'] = pd.to_datetime(df_orders['order_purchase_timestamp'])
    df_orders['order_delivered_date'] = pd.to_datetime(df_orders['order_delivered_date'])
    df_orders['order_estimated_delivery_date'] = pd.to_datetime(df_orders['order_estimated_delivery_date'])

    # Delivery performance calculation
    # Delivery duration in days (delivered date - purchase date)
    df_orders['actual_delivery_days'] = (df_orders['order_delivered_date'] - df_orders['order_purchase_timestamp']).dt.total_seconds() / (24 * 3600)
    df_orders['actual_delivery_days'] = df_orders['actual_delivery_days'].round(1)

    # Delivery delay: positive = late, negative/0 = on-time/early
    df_orders['delivery_delay_days'] = (df_orders['order_delivered_date'] - df_orders['order_estimated_delivery_date']).dt.total_seconds() / (24 * 3600)
    df_orders['delivery_delay_days'] = df_orders['delivery_delay_days'].round(1)
    df_orders['is_delayed'] = np.where(df_orders['delivery_delay_days'] > 0, 1, 0)

    # Order purchase year-month
    df_orders['order_year_month'] = df_orders['order_purchase_timestamp'].dt.to_period('M').astype(str)

    df_orders.to_csv(os.path.join(processed_dir, "fact_orders_cleaned.csv"), index=False)
    print(f" -> Saved: fact_orders_cleaned.csv (Calculated actual_delivery_days, delay_days, is_delayed)")

    # 4. Load Order Items
    df_items = pd.read_csv(os.path.join(raw_dir, "fact_order_items.csv"))
    print(f"\n[4] Processing Order Items (Rows: {len(df_items)})...")
    # Referential integrity check
    valid_orders = set(df_orders['order_id'])
    valid_prods = set(df_products['product_id'])
    assert df_items['order_id'].isin(valid_orders).all(), "Orphan order items detected!"
    assert df_items['product_id'].isin(valid_prods).all(), "Invalid product foreign keys detected!"

    df_items['total_item_value'] = round(df_items['price'] + df_items['freight_value'], 2)
    df_items.to_csv(os.path.join(processed_dir, "fact_order_items_cleaned.csv"), index=False)
    print(" -> Saved: fact_order_items_cleaned.csv (Verified foreign keys, added total_item_value)")

    # 5. Load Payments & Reviews
    df_payments = pd.read_csv(os.path.join(raw_dir, "fact_payments.csv"))
    df_reviews = pd.read_csv(os.path.join(raw_dir, "fact_reviews.csv"))
    df_payments.to_csv(os.path.join(processed_dir, "fact_payments_cleaned.csv"), index=False)
    df_reviews.to_csv(os.path.join(processed_dir, "fact_reviews_cleaned.csv"), index=False)
    print(f"\n[5] Saved: fact_payments_cleaned.csv ({len(df_payments)} rows) & fact_reviews_cleaned.csv ({len(df_reviews)} rows)")

    print("\n" + "=" * 60)
    print(" DATA VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Unique Customers:       {df_customers['customer_id'].nunique():,}")
    print(f"Total Orders:                 {df_orders['order_id'].nunique():,}")
    print(f"Total Order Items Sold:       {len(df_items):,}")
    print(f"Total Gross Merchandise Value: ${df_items['price'].sum():,.2f}")
    print(f"Total Freight Fees:           ${df_items['freight_value'].sum():,.2f}")
    print(f"Overall Delayed Order Rate:   {df_orders['is_delayed'].mean() * 100:.2f}%")
    print(f"Average Review Score:         {df_reviews['review_score'].mean():.2f} / 5.0")
    print("=" * 60)

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(BASE_DIR, "data", "raw")
    proc_path = os.path.join(BASE_DIR, "data", "processed")
    clean_and_validate_data(raw_path, proc_path)
