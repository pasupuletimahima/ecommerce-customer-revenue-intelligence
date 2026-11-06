"""
=============================================================================
Project: E-Commerce Customer Lifecycle & Revenue Intelligence System
Script: Interactive Streamlit Web Application
Author: Pasupuleti Mahima
=============================================================================
"""
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration & Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Customer Lifecycle & Revenue Intelligence System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Executive Aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.2rem;
    }
    .kpi-subtitle {
        font-size: 0.8rem;
        color: #10B981;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 18px;
        font-weight: 600;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Cached Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_project_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    proc_dir = os.path.join(base_dir, "data", "processed")
    rep_dir = os.path.join(base_dir, "reports")

    df_customers = pd.read_csv(os.path.join(proc_dir, "dim_customers_cleaned.csv"))
    df_products = pd.read_csv(os.path.join(proc_dir, "dim_products_cleaned.csv"))
    df_orders = pd.read_csv(os.path.join(proc_dir, "fact_orders_cleaned.csv"))
    df_items = pd.read_csv(os.path.join(proc_dir, "fact_order_items_cleaned.csv"))
    df_payments = pd.read_csv(os.path.join(proc_dir, "fact_payments_cleaned.csv"))
    df_reviews = pd.read_csv(os.path.join(proc_dir, "fact_reviews_cleaned.csv"))

    # Load SQL Report precomputations
    df_rfm = pd.read_csv(os.path.join(rep_dir, "rfm_customer_segments.csv"))
    df_cohort = pd.read_csv(os.path.join(rep_dir, "cohort_retention_matrix.csv"))

    # Merge core fact for fast filtering
    df_full = df_items.merge(df_orders, on="order_id", how="inner")
    df_full = df_full.merge(df_products, on="product_id", how="inner")
    df_full = df_full.merge(df_customers, on="customer_id", how="inner")
    df_full["item_profit"] = (df_full["price"] - df_full["unit_cost"]).round(2)

    return df_customers, df_products, df_orders, df_items, df_payments, df_reviews, df_rfm, df_cohort, df_full

df_customers, df_products, df_orders, df_items, df_payments, df_reviews, df_rfm, df_cohort, df_full = load_project_data()

# -----------------------------------------------------------------------------
# 3. Sidebar Interactive Controls
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/100/shopping-cart-loaded.png", width=70)
st.sidebar.title("Analytics Filters")
st.sidebar.markdown("Filter all charts and KPIs across the platform:")

# Filter: Product Category
categories_list = sorted(df_products["category_name"].unique())
selected_categories = st.sidebar.multiselect("Product Category", options=categories_list, default=categories_list)

# Filter: State
states_list = sorted(df_customers["state"].unique())
selected_states = st.sidebar.multiselect("Customer State", options=states_list, default=states_list)

# Apply filters
df_filtered = df_full[
    (df_full["category_name"].isin(selected_categories)) &
    (df_full["state"].isin(selected_states))
]

# Quick metrics
total_gmv = df_filtered["price"].sum()
total_orders = df_filtered["order_id"].nunique()
aov = total_gmv / total_orders if total_orders > 0 else 0
delayed_rate = df_filtered["is_delayed"].mean() * 100 if len(df_filtered) > 0 else 0

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Switch tabs at the top to explore Cohorts, RFM Segments, and What-If Simulations.")

# -----------------------------------------------------------------------------
# 4. Main Executive Header & Top KPI Banner
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">E-Commerce Customer Lifecycle & Revenue Intelligence System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Executive Decision-Support Platform | SQL, Dimensional Modeling & Customer Lifecycle Diagnostics</div>', unsafe_allow_html=True)

# 4 KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Gross Merchandise Value</div>
        <div class="kpi-value">${total_gmv:,.0f}</div>
        <div class="kpi-subtitle">Filtered Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Orders</div>
        <div class="kpi-value">{total_orders:,}</div>
        <div class="kpi-subtitle">Delivered Orders</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Average Order Value (AOV)</div>
        <div class="kpi-value">${aov:,.1f}</div>
        <div class="kpi-subtitle">Basket Efficiency</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    color_status = "#EF4444" if delayed_rate > 10 else "#10B981"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Delayed Delivery Rate</div>
        <div class="kpi-value" style="color: {color_status};">{delayed_rate:.1f}%</div>
        <div class="kpi-subtitle" style="color: {color_status};">Logistics SLA Status</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. Interactive Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Revenue & Category Analytics",
    "👥 Cohort Retention Heatmap",
    "🎯 RFM Customer Intelligence",
    "🚚 Logistics & Satisfaction Impact",
    "💡 What-If Revenue Recovery Simulator"
])

# -----------------------------------------------------------------------------
# TAB 1: Revenue & Category Analytics
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Monthly GMV Growth & Category Distribution")

    col_t1_a, col_t1_b = st.columns([1.6, 1])

    with col_t1_a:
        # Monthly GMV Trend
        monthly_gmv = df_filtered.groupby("order_year_month")["price"].sum().reset_index()
        fig_trend = px.area(
            monthly_gmv,
            x="order_year_month",
            y="price",
            title="Monthly GMV Trend ($)",
            labels={"order_year_month": "Month", "price": "Total GMV ($)"},
            color_discrete_sequence=["#2563EB"]
        )
        fig_trend.update_layout(xaxis_tickangle=-45, height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_t1_b:
        # Payment Method Breakdown
        pmt_summary = df_payments.groupby("payment_type")["payment_value"].sum().reset_index()
        fig_pmt = px.pie(
            pmt_summary,
            names="payment_type",
            values="payment_value",
            hole=0.45,
            title="Payment Method Adoption",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pmt.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pmt, use_container_width=True)

    # Category Bar Chart
    cat_summary = df_filtered.groupby("category_name").agg(
        GMV=("price", "sum"),
        Profit=("item_profit", "sum")
    ).reset_index().sort_values(by="GMV", ascending=True)

    fig_cat = px.bar(
        cat_summary,
        x="GMV",
        y="category_name",
        orientation="h",
        title="Gross Merchandise Value by Product Category ($)",
        text_auto=".2s",
        color="GMV",
        color_continuous_scale="Blues"
    )
    fig_cat.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_cat, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: Cohort Retention Heatmap
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Monthly Customer Cohort Retention Matrix (%)")
    st.markdown("Tracks the percentage of customers who return to place a repeat purchase across Months 1 to 6.")

    # Prepare matrix
    cohort_pivot = df_cohort.set_index("cohort_month")[['M0_Pct', 'M1_Pct', 'M2_Pct', 'M3_Pct', 'M4_Pct', 'M5_Pct', 'M6_Pct']]
    cohort_pivot.columns = ['Month 0 (Base)', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']

    fig_cohort = px.imshow(
        cohort_pivot.head(12),
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Blues",
        labels=dict(x="Months Elapsed Since First Order", y="Cohort Acquisition Month", color="Retention %"),
        zmin=0,
        zmax=100
    )
    fig_cohort.update_layout(height=480, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_cohort, use_container_width=True)

    st.warning("⚠️ **Key Finding:** Retention drops from **100% in Month 0 to ~18% in Month 1**, stabilizing around **4%–5% by Month 6**. Over **81% of buyers never make a second order** without targeted automated retention prompts.")

# -----------------------------------------------------------------------------
# TAB 3: RFM Customer Intelligence & Live Inspector
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Customer Behavioral Segmentation (Pareto 80/20 Distribution)")

    col_t3_a, col_t3_b = st.columns([1.4, 1])

    with col_t3_a:
        # Treemap
        seg_summary = df_rfm.groupby("customer_segment").agg(
            Total_Customers=("customer_id", "count"),
            Total_Revenue=("monetary_value", "sum")
        ).reset_index()

        fig_tree = px.treemap(
            seg_summary,
            path=["customer_segment"],
            values="Total_Revenue",
            color="Total_Revenue",
            color_continuous_scale="Blues",
            title="Revenue Contribution by Customer Segment ($)"
        )
        fig_tree.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_t3_b:
        # Summary Table
        seg_summary["Customer_Share_%"] = (seg_summary["Total_Customers"] / seg_summary["Total_Customers"].sum() * 100).round(1)
        seg_summary["Revenue_Share_%"] = (seg_summary["Total_Revenue"] / seg_summary["Total_Revenue"].sum() * 100).round(1)
        st.markdown("**Segment Concentration Breakdown:**")
        st.dataframe(
            seg_summary[["customer_segment", "Total_Customers", "Customer_Share_%", "Revenue_Share_%"]],
            hide_index=True,
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("🔍 Live Customer Profile Inspector")
    st.markdown("Lookup any individual customer to inspect their RFM scores, spending history, and recommended retention action:")

    cust_search_col1, cust_search_col2 = st.columns([1, 2])
    with cust_search_col1:
        selected_cust = st.selectbox("Select or Type Customer ID:", options=df_rfm["customer_id"].head(200))

    cust_record = df_rfm[df_rfm["customer_id"] == selected_cust].iloc[0]

    with cust_search_col2:
        seg_color = "#10B981" if "Champions" in cust_record["customer_segment"] else ("#EF4444" if "At Risk" in cust_record["customer_segment"] else "#2563EB")
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #0F172A;">Profile: {cust_record['customer_id']} ({cust_record['city']}, {cust_record['state']})</h4>
                <span style="background: {seg_color}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">
                    {cust_record['customer_segment']}
                </span>
            </div>
            <hr style="margin: 0.8rem 0;">
            <div style="display: flex; gap: 2rem;">
                <div><b>Recency:</b> {cust_record['recency_days']:.0f} days inactive (Score: {cust_record['r_score']}/5)</div>
                <div><b>Frequency:</b> {cust_record['frequency']} orders (Score: {cust_record['f_score']}/5)</div>
                <div><b>Lifetime Spend:</b> ${cust_record['monetary_value']:,.2f} (Score: {cust_record['m_score']}/5)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: Logistics & Satisfaction Impact
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Logistics Performance & Customer Review Scores")

    col_t4_a, col_t4_b = st.columns([1.2, 1])

    with col_t4_a:
        # Reviews comparison chart
        df_log = df_orders.merge(df_reviews, on="order_id", how="inner")
        log_grouped = df_log.groupby(["is_delayed", "review_score"])["review_id"].count().reset_index()
        log_grouped["Delivery Status"] = np.where(log_grouped["is_delayed"] == 1, "Delayed Delivery", "On-Time / Early")

        fig_log = px.bar(
            log_grouped,
            x="review_score",
            y="review_id",
            color="Delivery Status",
            barmode="group",
            title="Review Score Distribution (1 to 5 Stars)",
            labels={"review_score": "Review Score (Stars)", "review_id": "Number of Reviews"},
            color_discrete_map={"On-Time / Early": "#10B981", "Delayed Delivery": "#EF4444"}
        )
        fig_log.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_log, use_container_width=True)

    with col_t4_b:
        st.markdown("### The Operational Impact")
        st.markdown("""
        * **On-Time Deliveries:** Average rating is **4.35 / 5.0**, with only **4.7%** negative reviews.
        * **Delayed Deliveries:** Average rating crashes to **2.04 / 5.0**, with **70.2%** receiving 1 or 2 stars.
        
        > **Strategic Takeaway:** Delivery delay is the **#1 predictor of customer churn**. Addressing 3PL fulfillment speed directly recovers customer lifetime value.
        """)

# -----------------------------------------------------------------------------
# TAB 5: What-If Revenue Recovery Simulator
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("🎯 Executive What-If Revenue Simulator")
    st.markdown("Model the financial return of launching an automated win-back campaign for the **'At Risk'** customer segment:")

    sim_col1, sim_col2 = st.columns([1, 1.4])

    at_risk_data = df_rfm[df_rfm["customer_segment"].str.contains("At Risk")]
    total_at_risk_customers = len(at_risk_data)
    total_at_risk_revenue = at_risk_data["monetary_value"].sum()
    avg_at_risk_spend = at_risk_data["monetary_value"].mean()

    with sim_col1:
        st.metric("Total 'At Risk' Customers", f"{total_at_risk_customers:,}")
        st.metric("Historical Revenue at Risk", f"${total_at_risk_revenue:,.0f}")
        reactivation_rate = st.slider("Target Win-Back Reactivation Rate (%):", min_value=5, max_value=50, value=15, step=5)

    with sim_col2:
        recovered_customers = int(total_at_risk_customers * (reactivation_rate / 100))
        recovered_revenue = recovered_customers * avg_at_risk_spend

        st.markdown(f"""
        <div style="background: #F8FAFC; border-left: 5px solid #2563EB; border-radius: 8px; padding: 1.5rem; margin-top: 1rem;">
            <h4 style="margin: 0; color: #0F172A;">Simulated Win-Back Impact ({reactivation_rate}% Conversion):</h4>
            <div style="font-size: 2.2rem; font-weight: 800; color: #2563EB; margin: 0.5rem 0;">
                +${recovered_revenue:,.0f}
            </div>
            <p style="color: #475569; margin: 0;">
                By reactivating <b>{recovered_customers:,}</b> churning customers with an automated 15% personalized discount voucher, the business recovers <b>${recovered_revenue:,.0f}</b> in gross revenue.
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("E-Commerce Customer Lifecycle & Revenue Intelligence System | Designed & Developed by Pasupuleti Mahima")
