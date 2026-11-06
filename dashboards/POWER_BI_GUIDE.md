# Power BI Implementation Guide: E-Commerce Customer Lifecycle & Revenue Intelligence System
**Author:** Pasupuleti Mahima

This guide walks you through importing the project data into **Power BI Desktop**, establishing the relational **Star Schema**, creating calculated **DAX Measures**, and designing an executive-grade dashboard.

---

## 1. Importing Cleaned Data into Power BI

1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Navigate to:  
   `ecommerce_analytics_project\data\processed\`
4. Import these 6 cleaned CSV files:
   * `dim_customers_cleaned.csv`
   * `dim_products_cleaned.csv`
   * `fact_orders_cleaned.csv`
   * `fact_order_items_cleaned.csv`
   * `fact_payments_cleaned.csv`
   * `fact_reviews_cleaned.csv`
5. In the preview window, click **Load**.

---

## 2. Modeling the Star Schema (Model View)

Switch to the **Model View** (icon on the left navigation bar). Ensure the following relationships are established (Single direction: `1` to `*`):

* `dim_customers[customer_id]` (1) ───> `fact_orders[customer_id]` (*)
* `fact_orders[order_id]` (1) ────────> `fact_order_items[order_id]` (*)
* `dim_products[product_id]` (1) ─────> `fact_order_items[product_id]` (*)
* `fact_orders[order_id]` (1) ────────> `fact_payments[order_id]` (*)
* `fact_orders[order_id]` (1) ────────> `fact_reviews[order_id]` (*)

---

## 3. Essential DAX Measures

Create a dedicated table for measures:
* Click **Home** -> **Enter Data** -> Name the table `_All_Measures`.
* Right-click `_All_Measures` -> **New Measure**, and enter the following formulas:

### A. Core Financials
```dax
Total GMV = SUM(fact_order_items_cleaned[price])
```
```dax
Total Freight = SUM(fact_order_items_cleaned[freight_value])
```
```dax
Total Orders = DISTINCTCOUNT(fact_orders_cleaned[order_id])
```
```dax
Total Unique Customers = DISTINCTCOUNT(dim_customers_cleaned[customer_id])
```
```dax
Average Order Value (AOV) = DIVIDE([Total GMV], [Total Orders], 0)
```
```dax
Gross Profit = SUMX(
    fact_order_items_cleaned, 
    fact_order_items_cleaned[price] - RELATED(dim_products_cleaned[unit_cost])
)
```
```dax
Gross Margin % = DIVIDE([Gross Profit], [Total GMV], 0)
```

### B. Logistics & Service Quality
```dax
Delayed Orders Count = CALCULATE(COUNTROWS(fact_orders_cleaned), fact_orders_cleaned[is_delayed] = 1)
```
```dax
Delayed Order Rate % = DIVIDE([Delayed Orders Count], [Total Orders], 0)
```
```dax
Average Review Score = AVERAGE(fact_reviews_cleaned[review_score])
```

### C. Customer Repeat & Churn
```dax
Repeat Customers = 
CALCULATE(
    DISTINCTCOUNT(fact_orders_cleaned[customer_id]),
    FILTER(
        VALUES(fact_orders_cleaned[customer_id]),
        CALCULATE(DISTINCTCOUNT(fact_orders_cleaned[order_id])) > 1
    )
)
```
```dax
Repeat Purchase Rate % = DIVIDE([Repeat Customers], [Total Unique Customers], 0)
```

---

## 4. Suggested Dashboard Layout (3 Pages)

### Page 1: Executive KPI & Revenue Performance
* **Top KPI Banner Cards:** Total GMV (\$3.51M), Total Orders (10,408), Average Order Value (\$337), Gross Margin % (42.4%).
* **Line Chart:** Monthly GMV Trend over time (X-axis: `order_year_month`, Y-axis: `Total GMV`).
* **Bar Chart (Horizontal):** GMV & Gross Profit by Product Category.
* **Donut Chart:** Share of Payment Methods (Credit Card, UPI, Debit Card, Voucher).
* **Slicers:** Date Range, State, Category Name.

### Page 2: Customer Retention & RFM Segmentation
* **Import File:** Also load `reports\rfm_customer_segments.csv` and `reports\cohort_retention_matrix.csv`.
* **Tree Map / Stacked Bar:** Customer Count vs. Revenue by `customer_segment` (Highlights the 80/20 rule: Champions generating 35.7% of revenue).
* **Matrix Visual (Cohort Heatmap):**
  * Rows: `cohort_month`
  * Values: `M0_Pct`, `M1_Pct`, `M2_Pct`, `M3_Pct`, `M4_Pct`, `M5_Pct`, `M6_Pct`
  * Conditional Formatting: Background color gradient (Dark Blue = High, White = Low).
* **Scatter Plot:** Recency Days (X-axis) vs. Monetary Value (Y-axis), colored by `customer_segment`.

### Page 3: Logistics & Customer Satisfaction Diagnostics
* **KPI Cards:** Average Delivery Days (8.2 days), Delayed Order Rate % (14.2%), Average Review Score (4.01 / 5.0).
* **Clustered Column Chart:** Review Score Distribution (1 to 5 stars) split by `is_delayed` (shows 70.2% negative reviews when delayed vs 4.7% when on-time).
* **Category Freight Burden Table:** Product Category, GMV, Total Freight, and Freight Share % (highlighting high-freight categories like Books & Beauty).
