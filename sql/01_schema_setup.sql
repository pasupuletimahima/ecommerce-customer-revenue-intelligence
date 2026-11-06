-- =============================================================================
-- E-COMMERCE CUSTOMER LIFECYCLE & REVENUE INTELLIGENCE SYSTEM
-- Script 01: Relational Schema Definition (Star Schema Architecture)
-- Author: Pasupuleti Mahima
-- Dialect: MySQL 8.0+
-- =============================================================================

DROP DATABASE IF EXISTS ecommerce_analytics_db;
CREATE DATABASE ecommerce_analytics_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE ecommerce_analytics_db;

-- -----------------------------------------------------------------------------
-- 1. Dimension Table: Customers
-- -----------------------------------------------------------------------------
CREATE TABLE dim_customers (
    customer_id         VARCHAR(32) PRIMARY KEY,
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(50) NOT NULL,
    signup_date         DATE NOT NULL,
    signup_year_month   VARCHAR(7) NOT NULL,
    INDEX idx_cust_state (state),
    INDEX idx_cust_signup (signup_date)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. Dimension Table: Products
-- -----------------------------------------------------------------------------
CREATE TABLE dim_products (
    product_id          VARCHAR(32) PRIMARY KEY,
    category_name       VARCHAR(100) NOT NULL,
    unit_price          DECIMAL(10, 2) NOT NULL,
    unit_cost           DECIMAL(10, 2) NOT NULL,
    weight_g            INT NOT NULL,
    profit_margin       DECIMAL(10, 2) NOT NULL,
    profit_margin_pct   DECIMAL(5, 2) NOT NULL,
    INDEX idx_prod_category (category_name),
    INDEX idx_prod_price (unit_price)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. Fact Table: Orders
-- -----------------------------------------------------------------------------
CREATE TABLE fact_orders (
    order_id                    VARCHAR(32) PRIMARY KEY,
    customer_id                 VARCHAR(32) NOT NULL,
    order_status                VARCHAR(20) NOT NULL,
    order_purchase_timestamp    DATETIME NOT NULL,
    order_delivered_date        DATETIME NULL,
    order_estimated_delivery_date DATETIME NOT NULL,
    actual_delivery_days        DECIMAL(5, 1) NULL,
    delivery_delay_days         DECIMAL(5, 1) NULL,
    is_delayed                  TINYINT(1) DEFAULT 0,
    order_year_month            VARCHAR(7) NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES dim_customers(customer_id) ON DELETE RESTRICT,
    INDEX idx_orders_purchase (order_purchase_timestamp),
    INDEX idx_orders_status (order_status),
    INDEX idx_orders_delay (is_delayed)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. Fact Table: Order Items (Granular Line-Item Level)
-- -----------------------------------------------------------------------------
CREATE TABLE fact_order_items (
    order_item_id           VARCHAR(32) PRIMARY KEY,
    order_id                VARCHAR(32) NOT NULL,
    order_item_sequence     INT NOT NULL,
    product_id              VARCHAR(32) NOT NULL,
    price                   DECIMAL(10, 2) NOT NULL,
    freight_value           DECIMAL(10, 2) NOT NULL,
    total_item_value        DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) 
        REFERENCES dim_products(product_id) ON DELETE RESTRICT,
    INDEX idx_items_product (product_id),
    INDEX idx_items_order (order_id)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. Fact Table: Payments
-- -----------------------------------------------------------------------------
CREATE TABLE fact_payments (
    order_id                VARCHAR(32) NOT NULL,
    payment_type            VARCHAR(30) NOT NULL,
    payment_installments    INT NOT NULL,
    payment_value           DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    INDEX idx_payments_type (payment_type)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. Fact Table: Reviews
-- -----------------------------------------------------------------------------
CREATE TABLE fact_reviews (
    review_id               VARCHAR(32) PRIMARY KEY,
    order_id                VARCHAR(32) NOT NULL,
    review_score            INT NOT NULL,
    review_creation_date    DATE NOT NULL,
    CONSTRAINT fk_reviews_order FOREIGN KEY (order_id) 
        REFERENCES fact_orders(order_id) ON DELETE CASCADE,
    INDEX idx_reviews_score (review_score)
) ENGINE=InnoDB;
