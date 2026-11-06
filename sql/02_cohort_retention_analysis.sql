-- =============================================================================
-- E-COMMERCE CUSTOMER LIFECYCLE & REVENUE INTELLIGENCE SYSTEM
-- Script 02: Monthly Cohort Retention Analysis
-- Author: Pasupuleti Mahima
-- Business Question: When customers make their first purchase, what % return 
-- in month 1, 2, 3, etc.? Where is the steep drop-off?
-- Dialect: MySQL 8.0+
-- =============================================================================

USE ecommerce_analytics_db;

WITH Customer_First_Purchase AS (
    -- Step 1: Identify the very first order date for every customer (The Cohort)
    SELECT 
        customer_id,
        MIN(DATE_FORMAT(order_purchase_timestamp, '%Y-%m-01')) AS cohort_month
    FROM fact_orders
    WHERE order_status = 'delivered'
    GROUP BY customer_id
),

Customer_Orders AS (
    -- Step 2: Extract all valid purchase dates for each customer
    SELECT 
        o.customer_id,
        c.cohort_month,
        DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m-01') AS order_month
    FROM fact_orders o
    INNER JOIN Customer_First_Purchase c 
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),

Cohort_Index_Calculation AS (
    -- Step 3: Compute Cohort Index (Months elapsed since first purchase)
    -- Formula: (Order Year - Cohort Year) * 12 + (Order Month - Cohort Month)
    SELECT 
        customer_id,
        cohort_month,
        order_month,
        (
            (YEAR(STR_TO_DATE(order_month, '%Y-%m-%d')) - YEAR(STR_TO_DATE(cohort_month, '%Y-%m-%d'))) * 12 +
            (MONTH(STR_TO_DATE(order_month, '%Y-%m-%d')) - MONTH(STR_TO_DATE(cohort_month, '%Y-%m-%d')))
        ) AS cohort_index
    FROM Customer_Orders
),

Cohort_Size AS (
    -- Step 4: Total number of unique customers who joined in each cohort (Month 0 base)
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_customers
    FROM Customer_First_Purchase
    GROUP BY cohort_month
),

Retention_Counts AS (
    -- Step 5: Count of active repeat customers for each cohort index
    SELECT 
        cic.cohort_month,
        cs.total_cohort_customers,
        cic.cohort_index,
        COUNT(DISTINCT cic.customer_id) AS active_customers
    FROM Cohort_Index_Calculation cic
    INNER JOIN Cohort_Size cs 
        ON cic.cohort_month = cs.cohort_month
    GROUP BY cic.cohort_month, cs.total_cohort_customers, cic.cohort_index
)

-- Step 6: Final Presentation with Retention Rates & Pivot Matrix
SELECT 
    cohort_month,
    total_cohort_customers,
    cohort_index,
    active_customers,
    ROUND((active_customers * 100.0) / total_cohort_customers, 2) AS retention_rate_pct
FROM Retention_Counts
ORDER BY cohort_month, cohort_index;

-- =============================================================================
-- Pivot View of Retention Matrix (Months 0 through 6)
-- Ideal for heatmaps in Power BI / Tableau
-- =============================================================================
SELECT 
    cohort_month,
    total_cohort_customers AS M0_Customers,
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
