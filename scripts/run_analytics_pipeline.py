"""
=============================================================================
Project: E-Commerce Customer Lifecycle & Revenue Intelligence System
Script: End-to-End SQL Analytics Pipeline Execution
Author: Pasupuleti Mahima
=============================================================================
"""
import os
import sqlite3
import pandas as pd

def run_sql_analytics(proc_dir, reports_dir):
    os.makedirs(reports_dir, exist_ok=True)
    print("=" * 60)
    print(" PHASE 3: EXECUTING SQL ANALYTICS ENGINE")
    print("=" * 60)

    # Connect to SQLite database
    conn = sqlite3.connect(":memory:")
    
    # Load cleaned tables into SQL engine
    df_customers = pd.read_csv(os.path.join(proc_dir, "dim_customers_cleaned.csv"))
    df_products = pd.read_csv(os.path.join(proc_dir, "dim_products_cleaned.csv"))
    df_orders = pd.read_csv(os.path.join(proc_dir, "fact_orders_cleaned.csv"))
    df_items = pd.read_csv(os.path.join(proc_dir, "fact_order_items_cleaned.csv"))
    df_payments = pd.read_csv(os.path.join(proc_dir, "fact_payments_cleaned.csv"))
    df_reviews = pd.read_csv(os.path.join(proc_dir, "fact_reviews_cleaned.csv"))

    df_customers.to_sql("dim_customers", conn, index=False)
    df_products.to_sql("dim_products", conn, index=False)
    df_orders.to_sql("fact_orders", conn, index=False)
    df_items.to_sql("fact_order_items", conn, index=False)
    df_payments.to_sql("fact_payments", conn, index=False)
    df_reviews.to_sql("fact_reviews", conn, index=False)
    print("-> All relational tables loaded into SQL engine successfully.")

    # 1. Cohort Retention Query
    cohort_sql = """
    WITH Customer_First_Purchase AS (
        SELECT 
            customer_id,
            SUBSTR(MIN(order_purchase_timestamp), 1, 7) AS cohort_month
        FROM fact_orders
        WHERE order_status = 'delivered'
        GROUP BY customer_id
    ),
    Customer_Orders AS (
        SELECT 
            o.customer_id,
            c.cohort_month,
            SUBSTR(o.order_purchase_timestamp, 1, 7) AS order_month
        FROM fact_orders o
        JOIN Customer_First_Purchase c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
    ),
    Cohort_Index_Calc AS (
        SELECT 
            customer_id,
            cohort_month,
            order_month,
            (CAST(SUBSTR(order_month, 1, 4) AS INT) - CAST(SUBSTR(cohort_month, 1, 4) AS INT)) * 12 +
            (CAST(SUBSTR(order_month, 6, 2) AS INT) - CAST(SUBSTR(cohort_month, 6, 2) AS INT)) AS cohort_index
        FROM Customer_Orders
    ),
    Cohort_Size AS (
        SELECT cohort_month, COUNT(DISTINCT customer_id) AS total_cohort_customers
        FROM Customer_First_Purchase
        GROUP BY cohort_month
    ),
    Retention_Counts AS (
        SELECT 
            cic.cohort_month,
            cs.total_cohort_customers,
            cic.cohort_index,
            COUNT(DISTINCT cic.customer_id) AS active_customers
        FROM Cohort_Index_Calc cic
        JOIN Cohort_Size cs ON cic.cohort_month = cs.cohort_month
        GROUP BY cic.cohort_month, cs.total_cohort_customers, cic.cohort_index
    )
    SELECT 
        cohort_month,
        total_cohort_customers AS M0_Base,
        ROUND(MAX(CASE WHEN cohort_index = 0 THEN (active_customers * 100.0) / total_cohort_customers END), 1) AS M0_Pct,
        ROUND(MAX(CASE WHEN cohort_index = 1 THEN (active_customers * 100.0) / total_cohort_customers END), 1) AS M1_Pct,
        ROUND(MAX(CASE WHEN cohort_index = 2 THEN (active_customers * 100.0) / total_cohort_customers END), 1) AS M2_Pct,
        ROUND(MAX(CASE WHEN cohort_index = 3 THEN (active_customers * 100.0) / total_cohort_customers END), 1) AS M3_Pct,
        ROUND(MAX(CASE WHEN cohort_index = 4 THEN (active_customers * 100.0) / total_cohort_customers END), 1) AS M4_Pct,
        ROUND(MAX(CASE WHEN cohort_index = 5 THEN (active_customers * 100.0) / total_cohort_customers END), 1) AS M5_Pct,
        ROUND(MAX(CASE WHEN cohort_index = 6 THEN (active_customers * 100.0) / total_cohort_customers END), 1) AS M6_Pct
    FROM Retention_Counts
    GROUP BY cohort_month, total_cohort_customers
    ORDER BY cohort_month;
    """
    df_cohort = pd.read_sql_query(cohort_sql, conn)
    df_cohort.to_csv(os.path.join(reports_dir, "cohort_retention_matrix.csv"), index=False)
    print("\n-> Cohort Retention Analysis Generated (Top 5 Cohorts):")
    print(df_cohort.head().to_string(index=False))

    # 2. RFM Segmentation Query
    rfm_sql = """
    WITH Snapshot AS (
        SELECT DATETIME(MAX(order_purchase_timestamp), '+1 day') AS snapshot_dt FROM fact_orders
    ),
    Customer_RFM_Raw AS (
        SELECT 
            o.customer_id,
            c.city,
            c.state,
            ROUND(JULIANDAY((SELECT snapshot_dt FROM Snapshot)) - JULIANDAY(MAX(o.order_purchase_timestamp))) AS recency_days,
            COUNT(DISTINCT o.order_id) AS frequency,
            ROUND(SUM(oi.price), 2) AS monetary_value
        FROM fact_orders o
        JOIN dim_customers c ON o.customer_id = c.customer_id
        JOIN fact_order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY o.customer_id, c.city, c.state
    ),
    Scored AS (
        SELECT 
            customer_id,
            city,
            state,
            recency_days,
            frequency,
            monetary_value,
            NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
            NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
        FROM Customer_RFM_Raw
    ),
    Segmented AS (
        SELECT 
            customer_id,
            city,
            state,
            recency_days,
            frequency,
            monetary_value,
            r_score,
            f_score,
            m_score,
            CASE 
                WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '1. Champions'
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN '2. Loyal Customers'
                WHEN r_score >= 4 AND f_score < 3 THEN '3. Potential Loyalists (New/Recent)'
                WHEN r_score <= 2 AND f_score >= 3 THEN '4. At Risk (High Value, Churning)'
                WHEN r_score <= 2 AND f_score <= 2 THEN '5. Hibernating / Lost'
                ELSE '6. Need Attention (Mid-Tier)'
            END AS customer_segment
        FROM Scored
    )
    SELECT * FROM Segmented;
    """
    df_rfm = pd.read_sql_query(rfm_sql, conn)
    df_rfm.to_csv(os.path.join(reports_dir, "rfm_customer_segments.csv"), index=False)
    
    # Segment summary
    seg_summary = df_rfm.groupby('customer_segment').agg(
        Total_Customers=('customer_id', 'count'),
        Total_Revenue=('monetary_value', 'sum'),
        Avg_Order_Value=('monetary_value', 'mean'),
        Avg_Orders=('frequency', 'mean'),
        Avg_Recency_Days=('recency_days', 'mean')
    ).reset_index()
    seg_summary['Total_Revenue'] = seg_summary['Total_Revenue'].round(2)
    seg_summary['Avg_Order_Value'] = seg_summary['Avg_Order_Value'].round(2)
    seg_summary['Avg_Orders'] = seg_summary['Avg_Orders'].round(1)
    seg_summary['Avg_Recency_Days'] = seg_summary['Avg_Recency_Days'].round(0).astype(int)
    seg_summary['Customer_Share_Pct'] = round(seg_summary['Total_Customers'] * 100 / seg_summary['Total_Customers'].sum(), 1)
    seg_summary['Revenue_Share_Pct'] = round(seg_summary['Total_Revenue'] * 100 / seg_summary['Total_Revenue'].sum(), 1)
    seg_summary.to_csv(os.path.join(reports_dir, "rfm_segment_summary.csv"), index=False)
    print("\n-> RFM Customer Segmentation Summary:")
    print(seg_summary[['customer_segment', 'Total_Customers', 'Customer_Share_Pct', 'Total_Revenue', 'Revenue_Share_Pct', 'Avg_Recency_Days']].to_string(index=False))

    # 3. Logistics and Delivery Delay vs Satisfaction
    logistics_sql = """
    SELECT 
        CASE WHEN o.is_delayed = 1 THEN 'Delayed Delivery' ELSE 'On-Time / Early' END AS delivery_status,
        COUNT(r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        ROUND(SUM(CASE WHEN r.review_score IN (1, 2) THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id), 1) AS negative_review_pct,
        ROUND(SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id), 1) AS five_star_pct
    FROM fact_orders o
    JOIN fact_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY delivery_status;
    """
    df_logistics = pd.read_sql_query(logistics_sql, conn)
    df_logistics.to_csv(os.path.join(reports_dir, "logistics_satisfaction_impact.csv"), index=False)
    print("\n-> Logistics Delay vs Review Score:")
    print(df_logistics.to_string(index=False))

    # 4. Product Category Profitability
    category_sql = """
    SELECT 
        p.category_name,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS total_items_sold,
        ROUND(SUM(oi.price), 2) AS total_gmv,
        ROUND(SUM(oi.freight_value), 2) AS total_freight,
        ROUND(SUM(oi.price - p.unit_cost), 2) AS gross_profit,
        ROUND((SUM(oi.price - p.unit_cost) * 100.0) / SUM(oi.price), 1) AS profit_margin_pct,
        ROUND((SUM(oi.freight_value) * 100.0) / (SUM(oi.price) + SUM(oi.freight_value)), 1) AS freight_burden_pct
    FROM fact_order_items oi
    JOIN dim_products p ON oi.product_id = p.product_id
    GROUP BY p.category_name
    ORDER BY total_gmv DESC;
    """
    df_category = pd.read_sql_query(category_sql, conn)
    df_category.to_csv(os.path.join(reports_dir, "category_profitability.csv"), index=False)
    print("\n-> Product Category Performance:")
    print(df_category.to_string(index=False))

    conn.close()
    print("\n" + "=" * 60)
    print(" ALL SQL ANALYTICS EXECUTED & REPORT CSVs EXPORTED!")
    print("=" * 60)

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_path = os.path.join(BASE_DIR, "data", "processed")
    rep_path = os.path.join(BASE_DIR, "reports")
    run_sql_analytics(proc_path, rep_path)
