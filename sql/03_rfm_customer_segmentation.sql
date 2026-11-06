-- =============================================================================
-- E-COMMERCE CUSTOMER LIFECYCLE & REVENUE INTELLIGENCE SYSTEM
-- Script 03: RFM Customer Segmentation (Recency, Frequency, Monetary)
-- Author: Pasupuleti Mahima
-- Business Question: Who are our highest-value customers? Who is at risk of churning?
-- Dialect: MySQL 8.0+ (Using NTILE Window Functions & CTEs)
-- =============================================================================

USE ecommerce_analytics_db;

WITH Reference_Date AS (
    -- Set the snapshot date to 1 day after the latest order in the database
    SELECT DATE_ADD(MAX(order_purchase_timestamp), INTERVAL 1 DAY) AS snapshot_dt
    FROM fact_orders
),

Customer_Raw_RFM AS (
    -- Step 1: Calculate raw Recency, Frequency, and Monetary values per customer
    SELECT 
        o.customer_id,
        c.city,
        c.state,
        DATEDIFF((SELECT snapshot_dt FROM Reference_Date), MAX(o.order_purchase_timestamp)) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.price), 2) AS monetary_value
    FROM fact_orders o
    INNER JOIN dim_customers c ON o.customer_id = c.customer_id
    INNER JOIN fact_order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY o.customer_id, c.city, c.state
),

RFM_Scoring AS (
    -- Step 2: Assign scores 1 to 5 using NTILE() window function
    -- For Recency: Lower days = Higher score (NTILE ordered DESC)
    -- For Frequency & Monetary: Higher value = Higher score (NTILE ordered ASC)
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
    FROM Customer_Raw_RFM
),

RFM_Segmentation AS (
    -- Step 3: Segment customers based on RFM score combinations
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
        ROUND((r_score + f_score + m_score) / 3.0, 2) AS avg_rfm_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '1. Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN '2. Loyal Customers'
            WHEN r_score >= 4 AND f_score < 3 THEN '3. Potential Loyalists (New/Recent)'
            WHEN r_score <= 2 AND f_score >= 3 THEN '4. At Risk (High Value, Churning)'
            WHEN r_score <= 2 AND f_score <= 2 THEN '5. Hibernating / Lost'
            ELSE '6. Need Attention (Mid-Tier)'
        END AS customer_segment
    FROM RFM_Scoring
)

-- View 1: Customer-Level Master Segmentation Table (Export to Power BI)
SELECT * FROM RFM_Segmentation;

-- =============================================================================
-- View 2: Executive Summary - Segment Revenue & Share Analysis
-- Demonstrates the Pareto Principle (80/20 rule) to Executive Leadership
-- =============================================================================
WITH Segment_Aggregates AS (
    SELECT 
        customer_segment,
        COUNT(customer_id) AS total_customers,
        ROUND(SUM(monetary_value), 2) AS segment_revenue,
        ROUND(AVG(monetary_value), 2) AS avg_monetary_per_customer,
        ROUND(AVG(recency_days), 0) AS avg_recency_days,
        ROUND(AVG(frequency), 1) AS avg_orders_per_customer
    FROM (
        SELECT 
            customer_id,
            CASE 
                WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '1. Champions'
                WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN '2. Loyal Customers'
                WHEN r_score >= 4 AND f_score < 3 THEN '3. Potential Loyalists (New/Recent)'
                WHEN r_score <= 2 AND f_score >= 3 THEN '4. At Risk (High Value, Churning)'
                WHEN r_score <= 2 AND f_score <= 2 THEN '5. Hibernating / Lost'
                ELSE '6. Need Attention (Mid-Tier)'
            END AS customer_segment,
            monetary_value,
            recency_days,
            frequency
        FROM (
            SELECT 
                o.customer_id,
                DATEDIFF((SELECT snapshot_dt FROM Reference_Date), MAX(o.order_purchase_timestamp)) AS recency_days,
                COUNT(DISTINCT o.order_id) AS frequency,
                ROUND(SUM(oi.price), 2) AS monetary_value,
                NTILE(5) OVER (ORDER BY DATEDIFF((SELECT snapshot_dt FROM Reference_Date), MAX(o.order_purchase_timestamp)) DESC) AS r_score,
                NTILE(5) OVER (ORDER BY COUNT(DISTINCT o.order_id) ASC) AS f_score,
                NTILE(5) OVER (ORDER BY SUM(oi.price) ASC) AS m_score
            FROM fact_orders o
            INNER JOIN fact_order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY o.customer_id
        ) scored
    ) segmented
    GROUP BY customer_segment
)
SELECT 
    customer_segment,
    total_customers,
    ROUND((total_customers * 100.0) / (SELECT SUM(total_customers) FROM Segment_Aggregates), 2) AS customer_share_pct,
    segment_revenue,
    ROUND((segment_revenue * 100.0) / (SELECT SUM(segment_revenue) FROM Segment_Aggregates), 2) AS revenue_share_pct,
    avg_monetary_per_customer,
    avg_recency_days,
    avg_orders_per_customer,
    CASE 
        WHEN customer_segment LIKE '1%' THEN 'Offer exclusive VIP perks, early product access, zero friction service'
        WHEN customer_segment LIKE '2%' THEN 'Upsell premium categories, loyalty reward points'
        WHEN customer_segment LIKE '3%' THEN 'Nurture with personalized welcome series & 2nd purchase discounts'
        WHEN customer_segment LIKE '4%' THEN 'Urgent win-back campaign: High-value discount code & survey'
        WHEN customer_segment LIKE '5%' THEN 'Re-engagement drip campaign or purge from expensive paid ads'
        ELSE 'Standard promotional calendar'
    END AS strategic_recommendation
FROM Segment_Aggregates
ORDER BY segment_revenue DESC;
