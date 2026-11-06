"""
=============================================================================
Project: E-Commerce Customer Lifecycle & Revenue Intelligence System
Script: Executive Visual Assets Generator (Seaborn & Matplotlib)
Author: Pasupuleti Mahima
=============================================================================
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_charts(reports_dir, viz_dir):
    os.makedirs(viz_dir, exist_ok=True)
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 11})

    print("Generating executive visual assets...")

    # 1. Cohort Retention Heatmap
    df_cohort = pd.read_csv(os.path.join(reports_dir, "cohort_retention_matrix.csv"))
    # Clean up matrix for plotting
    heatmap_data = df_cohort.set_index("cohort_month")[['M0_Pct', 'M1_Pct', 'M2_Pct', 'M3_Pct', 'M4_Pct', 'M5_Pct', 'M6_Pct']]
    heatmap_data.columns = ['Month 0', 'Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data.head(12), annot=True, fmt=".1f", cmap="Blues", cbar=True, vmin=0, vmax=100, linewidths=.5)
    plt.title("Monthly Customer Cohort Retention Rate (%)", fontsize=14, weight='bold', pad=15)
    plt.ylabel("Cohort (First Purchase Month)", fontsize=12)
    plt.xlabel("Months Elapsed Since First Purchase", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "01_cohort_retention_heatmap.png"), dpi=300)
    plt.close()
    print(" -> Generated 01_cohort_retention_heatmap.png")

    # 2. RFM Segment Revenue Share vs Customer Share
    df_rfm = pd.read_csv(os.path.join(reports_dir, "rfm_segment_summary.csv"))
    df_rfm_sorted = df_rfm.sort_values(by="Total_Revenue", ascending=False)
    
    fig, ax1 = plt.subplots(figsize=(11, 6))
    colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']
    
    bars = ax1.bar(df_rfm_sorted['customer_segment'], df_rfm_sorted['Total_Revenue'] / 1e3, color='#2b5c8f', width=0.55)
    ax1.set_ylabel("Total Revenue (in Thousands $)", fontsize=12, weight='bold', color='#2b5c8f')
    ax1.set_title("Customer Segments: Revenue Contribution & Volume Disparity", fontsize=14, weight='bold', pad=15)
    plt.xticks(rotation=20, ha='right')

    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 15, f"${yval:,.0f}K", ha='center', va='bottom', fontsize=10, weight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "02_rfm_revenue_distribution.png"), dpi=300)
    plt.close()
    print(" -> Generated 02_rfm_revenue_distribution.png")

    # 3. Delivery Delay vs Customer Reviews
    df_log = pd.read_csv(os.path.join(reports_dir, "logistics_satisfaction_impact.csv"))
    
    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = [0, 1]
    width = 0.35
    
    ax.bar([p - width/2 for p in x_pos], df_log['negative_review_pct'], width=width, label='Negative Reviews (1-2 Stars %)', color='#d9534f')
    ax.bar([p + width/2 for p in x_pos], df_log['five_star_pct'], width=width, label='Top Rating (5 Stars %)', color='#5cb85c')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df_log['delivery_status'], fontsize=12, weight='bold')
    ax.set_ylabel("Share of Total Reviews (%)", fontsize=12)
    ax.set_title("Impact of Delivery Delays on Customer Review Scores", fontsize=14, weight='bold', pad=15)
    ax.legend(frameon=True)
    
    for i in x_pos:
        ax.text(i - width/2, df_log['negative_review_pct'][i] + 1.5, f"{df_log['negative_review_pct'][i]}%", ha='center', weight='bold')
        ax.text(i + width/2, df_log['five_star_pct'][i] + 1.5, f"{df_log['five_star_pct'][i]}%", ha='center', weight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "03_logistics_impact.png"), dpi=300)
    plt.close()
    print(" -> Generated 03_logistics_impact.png")

    # 4. Product Category Profitability
    df_cat = pd.read_csv(os.path.join(reports_dir, "category_profitability.csv"))
    plt.figure(figsize=(10, 6))
    
    plt.barh(df_cat['category_name'][::-1], (df_cat['total_gmv'][::-1] / 1e3), color='#17a2b8', height=0.6)
    plt.title("Gross Merchandise Value (GMV) by Product Category", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Total GMV ($ in Thousands)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, "04_category_performance.png"), dpi=300)
    plt.close()
    print(" -> Generated 04_category_performance.png")
    print("All visual assets created successfully!")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rep_path = os.path.join(BASE_DIR, "reports")
    viz_path = os.path.join(BASE_DIR, "reports", "visualizations")
    create_charts(rep_path, viz_path)
