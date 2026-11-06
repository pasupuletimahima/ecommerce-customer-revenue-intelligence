-- =============================================================================
-- E-COMMERCE CUSTOMER LIFECYCLE & REVENUE INTELLIGENCE SYSTEM
-- Script 04: Delivery Logistics & Customer Satisfaction Diagnostics
-- Author: Pasupuleti Mahima
-- Business Question: What is the financial and reputational cost of delivery delays?
-- Dialect: MySQL 8.0+
-- =============================================================================

USE ecommerce_analytics_db;

-- -----------------------------------------------------------------------------
-- Query 1: The Direct Impact of Delivery Delay on Customer Reviews
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN o.is_delayed = 1 THEN 'Delayed Delivery'
        ELSE 'On-Time / Early Delivery'
    END AS delivery_performance,
    COUNT(r.review_id) AS total_reviews,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    ROUND(SUM(CASE WHEN r.review_score IN (1, 2) THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id), 2) AS bad_review_rate_pct,
    ROUND(SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(r.review_id), 2) AS five_star_rate_pct
FROM fact_orders o
INNER JOIN fact_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY delivery_performance;

-- -----------------------------------------------------------------------------
-- Query 2: Category Profitability, Volume & Freight Cost Burden
-- Identifies categories where shipping costs eat into customer perceived value
-- -----------------------------------------------------------------------------
SELECT 
    p.category_name,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS total_units_sold,
    ROUND(SUM(oi.price), 2) AS gross_merchandise_value,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_charged,
    ROUND(SUM(oi.price - (p.unit_cost)), 2) AS total_gross_profit,
    ROUND((SUM(oi.price - (p.unit_cost)) / SUM(oi.price)) * 100, 2) AS gross_profit_margin_pct,
    ROUND((SUM(oi.freight_value) / (SUM(oi.price) + SUM(oi.freight_value))) * 100, 2) AS freight_share_pct
FROM fact_order_items oi
INNER JOIN dim_products p ON oi.product_id = p.product_id
GROUP BY p.category_name
ORDER BY gross_merchandise_value DESC;

-- -----------------------------------------------------------------------------
-- Query 3: Payment Method Adoption & Average Basket Size
-- -----------------------------------------------------------------------------
SELECT 
    payment_type,
    COUNT(order_id) AS total_transactions,
    ROUND(SUM(payment_value), 2) AS total_volume,
    ROUND(AVG(payment_value), 2) AS avg_transaction_value,
    ROUND(AVG(payment_installments), 1) AS avg_installments
FROM fact_payments
GROUP BY payment_type
ORDER BY total_volume DESC;
