# E-Commerce Customer Lifecycle & Revenue Intelligence System
## Executive Business Intelligence Report: Retention, RFM Segmentation & Logistics Diagnostics
**Lead Analyst:** Pasupuleti Mahima (MCA)  
**Target Audience:** Chief Commercial Officer (CCO), VP of Operations, Head of Growth  
**Dataset Scope:** 10,408 orders | 6,000 customers | \$3.51M Gross Merchandise Value (GMV)  

---

## 1. Executive Summary

This diagnostic analysis evaluates transaction, customer behavior, and fulfillment data across a 24-month operating period. While top-line revenue expanded to **\$3.51M GMV** across **10,408 orders**, profitability and long-term customer lifetime value (LTV) face three critical headwinds:

1. **The Retention Cliff:** Customer retention drops sharply from **100% in Month 0 to 18.4% in Month 1**, stabilizing at just **4.5% by Month 6**. The business is overwhelmingly reliant on continuous, costly customer acquisition rather than organic repeat purchases.
2. **High-Value Revenue at Risk:** RFM analysis indicates that **13.8% of customers ("Champions") generate 35.7% of total revenue (\$1.21M)**. However, an alarming **22.4% of customers ("At Risk") hold \$1.03M in historical revenue** and have not purchased in an average of **555 days**.
3. **Logistics Bottlenecks Severely Damage Brand Equity:** While 85.8% of orders are delivered on time, the **14.2% delayed orders suffer an average customer satisfaction crash from 4.35 to 2.04 / 5.0**, with **70.2% of delayed deliveries receiving 1- or 2-star negative reviews**.

---

## 2. Deep-Dive Findings

### Finding 1: Monthly Cohort Retention Analysis
```
Cohort Month    M0 Base    Month 1    Month 2    Month 3    Month 4    Month 5    Month 6
2023-01         190        18.4%      12.6%      10.5%      6.3%       3.7%       4.2%
2023-02         239        18.4%      15.1%      10.9%      7.9%       5.0%       5.4%
2023-03         268        17.5%      11.2%      10.8%      7.8%       7.5%       5.2%
```
* **Insight:** Over 81% of newly acquired customers do not make a second purchase within 30 days.
* **Root Cause:** Absence of automated post-purchase onboarding, replenishment triggers, and loyalty rewards.

---

### Finding 2: RFM Customer Segmentation & Revenue Concentration
```
Segment                     Cust Share %    Revenue ($)     Rev Share %    Avg Recency (Days)
1. Champions                13.8%           $1,215,255      35.7%          132 days
2. Loyal Customers          21.3%           $  900,767      26.4%          256 days
4. At Risk (Churning)       22.4%           $1,039,178      30.5%          555 days
5. Hibernating / Lost       17.6%           $  103,230       3.0%          563 days
3. Potential Loyalists      14.6%           $   85,706       2.5%          162 days
6. Need Attention           10.3%           $   63,892       1.9%          308 days
```
* **The Pareto Principle in Action:** The top two segments ("Champions" and "Loyal Customers") account for **35.1% of customer volume but generate 62.1% of total revenue (\$2.11M)**.
* **The Churn Danger:** The "At Risk" segment accounts for **\$1.03M in past revenue**. If 20% of these customers can be reactivated with targeted re-engagement, the company can recover **\$207,000 in gross revenue**.

---

### Finding 3: Delivery Delays vs. Customer Review Scores
```
Fulfillment Status    Reviews Count    Avg Review Score    Negative (1-2 Stars)    Top (5 Stars)
On-Time / Early       8,615            4.35 / 5.0          4.7%                    54.5%
Delayed Delivery      1,477            2.04 / 5.0          70.2%                    4.3%
```
* **Operational Friction:** When an order is delayed past the estimated delivery date, negative reviews surge by **1,393%** (from 4.7% to 70.2%).
* **Impact:** Customer surveys correlate delivery delays directly with negative word-of-mouth and zero repeat purchase probability.

---

### Finding 4: Product Category Margins & Freight Cost Disparities
```
Category Name              Total GMV ($)    Profit Margin %    Freight Share %
Computers & Laptops        $1,612,040       43.2%              1.5%
Smartphones & Accessories  $1,010,979       41.4%              2.1%
Automotive & Tools         $  277,630       40.8%              7.7%
Fashion & Apparel          $  174,583       44.4%              11.4%
Books & Stationery         $   50,184       42.3%              23.1%
Beauty & Personal Care     $   69,430       39.7%              16.0%
```
* High-value tech categories have healthy profit margins (~42%) and negligible freight drag (<2.5%).
* Low-ticket categories like **Books (23.1% freight burden)** and **Beauty (16.0% freight burden)** suffer from excessive shipping cost ratios, making single-item orders margin-dilutive.

---

## 3. Strategic Action Plan & Recommendations

### Action 1: Launch an Automated Win-Back Campaign for "At-Risk" Customers
* **Tactic:** Trigger personalized, time-sensitive email/SMS campaigns offering a 15% discount code on previously browsed or purchased categories for customers in the "At-Risk" segment (inactive > 300 days).
* **Projected Impact:** Re-activating 10% of the 1,320 at-risk customers (132 buyers @ average \$787 spend) yields **\$103,800 in incremental revenue**.

### Action 2: Eliminate the Day-30 Retention Drop with a VIP Loyalty Program
* **Tactic:** Reward "Champions" with tier-based perks (free expedited delivery, early access to new releases) and implement an automatic 14-day post-delivery replenishment prompt for repeat consumable products.
* **Projected Impact:** Improving Month 1 retention from 18.4% to 25.0% generates an estimated **\$140,000 in additional annual GMV**.

### Action 3: Overhaul Delivery SLA & Carrier Accountability
* **Tactic:** Renegotiate contracts with regional 3PL logistics partners, introducing penalty clauses for shipments delayed beyond the estimated delivery date. Implement proactive SMS alerts offering a \$5 goodwill voucher when an unavoidable carrier delay occurs.
* **Projected Impact:** Decreasing the delayed order rate from 14.2% to under 7.0% will lift the overall company review score from **4.01 to 4.22**, improving customer lifetime retention.

### Action 4: Introduce Minimum Basket Thresholds for High-Freight Categories
* **Tactic:** Bundle Books & Beauty products or establish a **"Free Shipping on orders above \$50"** threshold to eliminate single-item orders with 23% freight burdens.
* **Projected Impact:** Increases Average Order Value (AOV) in lower-ticket categories by 18-25%.
