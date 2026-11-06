"""
=============================================================================
Project: E-Commerce Customer Lifecycle & Revenue Intelligence System
Script: Synthetic Relational Dataset Generator
Author: Pasupuleti Mahima
=============================================================================
"""
import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_ecommerce_data(output_dir):
    np.random.seed(42)
    random.seed(42)

    os.makedirs(output_dir, exist_ok=True)
    print("Generating E-Commerce Relational Dataset...")

    # 1. Categories and Products
    categories = [
        {"name": "Computers & Laptops", "base_price": 650.0, "weight": 2200},
        {"name": "Smartphones & Accessories", "base_price": 280.0, "weight": 350},
        {"name": "Home & Kitchen", "base_price": 85.0, "weight": 1800},
        {"name": "Fashion & Apparel", "base_price": 45.0, "weight": 400},
        {"name": "Beauty & Personal Care", "base_price": 32.0, "weight": 250},
        {"name": "Sports & Fitness", "base_price": 75.0, "weight": 1500},
        {"name": "Books & Stationery", "base_price": 22.0, "weight": 500},
        {"name": "Automotive & Tools", "base_price": 110.0, "weight": 2800}
    ]

    products = []
    num_products = 250
    for i in range(1, num_products + 1):
        cat = random.choice(categories)
        price_multiplier = np.random.uniform(0.6, 2.2)
        price = round(cat["base_price"] * price_multiplier, 2)
        cost = round(price * np.random.uniform(0.45, 0.70), 2)  # 30-55% margin
        weight = int(cat["weight"] * np.random.uniform(0.7, 1.4))
        products.append({
            "product_id": f"PROD_{i:04d}",
            "category_name": cat["name"],
            "unit_price": price,
            "unit_cost": cost,
            "weight_g": weight
        })
    df_products = pd.DataFrame(products)
    df_products.to_csv(os.path.join(output_dir, "dim_products.csv"), index=False)
    print(f" Saved {len(df_products)} products -> dim_products.csv")

    # 2. Customers
    num_customers = 6000
    cities_states = [
        ("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"), ("Nagpur", "Maharashtra"),
        ("Bengaluru", "Karnataka"), ("Mysuru", "Karnataka"),
        ("Hyderabad", "Telangana"),
        ("Chennai", "Tamil Nadu"), ("Coimbatore", "Tamil Nadu"),
        ("Delhi", "Delhi"), ("Noida", "Uttar Pradesh"), ("Gurugram", "Haryana"),
        ("Kolkata", "West Bengal"), ("Ahmedabad", "Gujarat"), ("Jaipur", "Rajasthan"),
        ("Kochi", "Kerala"), ("Indore", "Madhya Pradesh")
    ]
    city_weights = [0.18, 0.08, 0.04, 0.16, 0.03, 0.10, 0.09, 0.04, 0.12, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.02]
    city_weights = [w / sum(city_weights) for w in city_weights]

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_days = (end_date - start_date).days

    customers = []
    for i in range(1, num_customers + 1):
        city, state = random.choices(cities_states, weights=city_weights)[0]
        signup_offset = random.randint(0, total_days - 60)
        signup_dt = start_date + timedelta(days=signup_offset)
        customers.append({
            "customer_id": f"CUST_{i:05d}",
            "city": city,
            "state": state,
            "signup_date": signup_dt.strftime("%Y-%m-%d")
        })
    df_customers = pd.DataFrame(customers)
    df_customers.to_csv(os.path.join(output_dir, "dim_customers.csv"), index=False)
    print(f" Saved {len(df_customers)} customers -> dim_customers.csv")

    # 3. Orders and Order Items
    # We want realistic repeat purchases:
    # 65% purchase once, 20% purchase twice, 10% purchase 3-5 times, 5% purchase 6-10 times (Champions)
    orders = []
    order_items = []
    payments = []
    reviews = []

    order_id_counter = 1
    item_id_counter = 1

    payment_types = ["Credit Card", "UPI", "Debit Card", "Voucher"]
    payment_weights = [0.55, 0.30, 0.10, 0.05]

    for cust in customers:
        cust_id = cust["customer_id"]
        c_signup = datetime.strptime(cust["signup_date"], "%Y-%m-%d")

        # Determine purchase frequency profile
        rand_val = random.random()
        if rand_val < 0.65:
            num_orders = 1
        elif rand_val < 0.85:
            num_orders = 2
        elif rand_val < 0.95:
            num_orders = random.randint(3, 5)
        else:
            num_orders = random.randint(6, 10)  # Top champions

        prev_order_date = c_signup
        for o_idx in range(num_orders):
            # Days between repeat orders
            if o_idx == 0:
                gap = random.randint(0, 15)
            else:
                gap = int(np.random.exponential(scale=45)) + 5

            order_date = prev_order_date + timedelta(days=gap)
            if order_date > end_date:
                break
            prev_order_date = order_date

            order_id = f"ORD_{order_id_counter:06d}"
            order_id_counter += 1

            # Estimated delivery is 4-10 days
            est_delivery_days = random.randint(4, 10)
            est_delivery_date = order_date + timedelta(days=est_delivery_days)

            # Realistic delivery status & actual delivery
            status_prob = random.random()
            if status_prob < 0.02:
                status = "canceled"
                delivered_date = None
            elif status_prob < 0.03:
                status = "shipped"
                delivered_date = None
            else:
                status = "delivered"
                # 85% on time or early, 15% delayed
                if random.random() < 0.15:
                    delay_days = random.randint(1, 8)
                    delivered_date = est_delivery_date + timedelta(days=delay_days)
                else:
                    early_days = random.randint(0, 3)
                    delivered_date = est_delivery_date - timedelta(days=early_days)

            orders.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_status": status,
                "order_purchase_timestamp": order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "order_delivered_date": delivered_date.strftime("%Y-%m-%d %H:%M:%S") if delivered_date else None,
                "order_estimated_delivery_date": est_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
            })

            # Items for this order (1 to 4 items)
            num_items = random.choices([1, 2, 3, 4], weights=[0.70, 0.20, 0.07, 0.03])[0]
            total_order_amount = 0.0

            for seq in range(1, num_items + 1):
                prod = df_products.sample(1).iloc[0]
                freight = round(5.0 + (prod["weight_g"] / 1000.0) * 2.5 + random.uniform(1.0, 4.0), 2)
                item_price = prod["unit_price"]
                total_order_amount += (item_price + freight)

                order_items.append({
                    "order_item_id": f"ITEM_{item_id_counter:07d}",
                    "order_id": order_id,
                    "order_item_sequence": seq,
                    "product_id": prod["product_id"],
                    "price": item_price,
                    "freight_value": freight
                })
                item_id_counter += 1

            # Payment record
            ptype = random.choices(payment_types, weights=payment_weights)[0]
            installments = 1
            if ptype == "Credit Card" and total_order_amount > 150:
                installments = random.choice([1, 2, 3, 6, 10, 12])

            payments.append({
                "order_id": order_id,
                "payment_type": ptype,
                "payment_installments": installments,
                "payment_value": round(total_order_amount, 2)
            })

            # Review record
            if status == "delivered":
                # Strong correlation: delayed delivery gets lower scores
                is_delayed = delivered_date > est_delivery_date
                if is_delayed:
                    score = random.choices([1, 2, 3, 4, 5], weights=[0.45, 0.25, 0.15, 0.10, 0.05])[0]
                else:
                    score = random.choices([1, 2, 3, 4, 5], weights=[0.02, 0.03, 0.08, 0.32, 0.55])[0]

                reviews.append({
                    "review_id": f"REV_{len(reviews)+1:06d}",
                    "order_id": order_id,
                    "review_score": score,
                    "review_creation_date": (delivered_date + timedelta(days=random.randint(1, 4))).strftime("%Y-%m-%d")
                })

    df_orders = pd.DataFrame(orders)
    df_order_items = pd.DataFrame(order_items)
    df_payments = pd.DataFrame(payments)
    df_reviews = pd.DataFrame(reviews)

    df_orders.to_csv(os.path.join(output_dir, "fact_orders.csv"), index=False)
    df_order_items.to_csv(os.path.join(output_dir, "fact_order_items.csv"), index=False)
    df_payments.to_csv(os.path.join(output_dir, "fact_payments.csv"), index=False)
    df_reviews.to_csv(os.path.join(output_dir, "fact_reviews.csv"), index=False)

    print(f" Saved {len(df_orders)} orders -> fact_orders.csv")
    print(f" Saved {len(df_order_items)} line items -> fact_order_items.csv")
    print(f" Saved {len(df_payments)} payments -> fact_payments.csv")
    print(f" Saved {len(df_reviews)} reviews -> fact_reviews.csv")
    print("\nDataset generation completed successfully!")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(BASE_DIR, "data", "raw")
    generate_ecommerce_data(target_path)
