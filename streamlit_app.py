import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys
import subprocess
import re

# Config
st.set_page_config(page_title="Sales Dashboard + AI Demo", layout="wide")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_analysis.db")

# Helper Functions
def get_connection():
    return sqlite3.connect(DB_PATH)

def run_query(query):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# AI Cleaning Logic (Embedded Microservice)
def clean_product_text_ai(text):
    """
    Simulates AI Cleaning Logic using Rules/Regex.
    In production, this would call OpenAI API or spaCy.
    """
    brand = "Generic"
    common_brands = ["Nike", "Adidas", "Puma", "Apple", "Samsung", "Sony", "LG"]
    for b in common_brands:
        if b.lower() in text.lower():
            brand = b
            
    color = "Unknown"
    common_colors = ["Red", "Blue", "Black", "White", "Green", "Silver", "Gold", "Pink"]
    for c in common_colors:
        if c.lower() in text.lower():
            color = c

    size = None
    size_match = re.search(r"(?:Size|Sz)[:\s]*(\d+\.?\d*)", text, re.IGNORECASE)
    if size_match:
        size = size_match.group(1)

    category = "Other"
    if any(x in text.lower() for x in ["shoe", "sneaker", "boot"]):
        category = "Footwear"
    elif any(x in text.lower() for x in ["shirt", "pant", "jacket", "dress"]):
        category = "Apparel"
    elif any(x in text.lower() for x in ["phone", "laptop", "watch", "camera"]):
        category = "Electronics"

    return {
        "Brand": brand,
        "Color": color,
        "Size": size,
        "Category": category,
        "Original": text
    }

# Sidebar
st.sidebar.title("Control Panel")
if st.sidebar.button("Rebuild Database"):
    with st.spinner("Rebuilding Database... This may take a minute."):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_database.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            st.sidebar.success("Database Rebuilt Successfully!")
            st.cache_data.clear() # Clear cache to refresh data
        else:
            st.sidebar.error(f"Error: {result.stderr}")

# --- Main App with Tabs ---

tab1, tab2 = st.tabs(["📊 Sales Dashboard", "🤖 AI Product Cleaner"])

with tab1:
    st.title("Sales Analytics Dashboard")
    st.markdown("Real-time view of `sales_analysis.db`")
    
    # Top Metrics
    col1, col2, col3 = st.columns(3)
    
    revenue_df = run_query("SELECT SUM(quantity * price) as revenue FROM invoice_items")
    total_revenue = revenue_df['revenue'].iloc[0] if not revenue_df.empty else 0
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    tx_df = run_query("SELECT COUNT(*) as count FROM invoices")
    tx_count = tx_df['count'].iloc[0]
    with col2:
        st.metric("Total Invoices", f"{tx_count:,}")
    
    country_df = run_query("""
        SELECT country, SUM(ii.quantity * ii.price) as revenue
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.invoice_id
        GROUP BY country
        ORDER BY revenue DESC
        LIMIT 1
    """)
    top_country = country_df['country'].iloc[0] if not country_df.empty else "N/A"
    with col3:
        st.metric("Top Market", top_country)
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Monthly Sales Trend")
        monthly_df = run_query("""
            SELECT strftime('%Y-%m', i.invoice_date) as month, SUM(ii.quantity * ii.price) as revenue
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.invoice_id
            GROUP BY month
            ORDER BY month
        """)
        if not monthly_df.empty:
            fig_monthly = px.line(monthly_df, x='month', y='revenue', markers=True)
            st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.info("No data available.")
    
    with col_chart2:
        st.subheader("Top 10 Customers (CLV)")
        customer_df = run_query("""
            SELECT i.customer_id, SUM(ii.quantity * ii.price) as total_spend
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.invoice_id
            GROUP BY i.customer_id
            ORDER BY total_spend DESC
            LIMIT 10
        """)
        if not customer_df.empty:
            customer_df['customer_id'] = customer_df['customer_id'].astype(str)
            fig_cust = px.bar(customer_df, x='total_spend', y='customer_id', orientation='h')
            fig_cust.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_cust, use_container_width=True)
        else:
            st.info("No data available.")
    
    st.subheader("Recent Transactions")
    recent_df = run_query("""
        SELECT i.invoice_id, i.invoice_date, i.country, COUNT(ii.id) as items_count, SUM(ii.quantity * ii.price) as total
        FROM invoices i
        JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
        GROUP BY i.invoice_id
        ORDER BY i.invoice_date DESC
        LIMIT 100
    """)
    st.dataframe(recent_df)

with tab2:
    st.title("🤖 AI Product Data Cleaner")
    st.markdown("""
    **The Problem**: E-commerce data is often messy (e.g., `Nike Air Max -- Size 10 (Red)!!`).  
    **The Solution**: This AI Microservice extracts structured data automatically.
    """)
    
    col_input, col_output = st.columns(2)
    
    with col_input:
        raw_text = st.text_area("Enter Messy Product Title", value="Nike Air Max 90 -- Size 10 (Red)!!", height=150)
        clean_btn = st.button("✨ Clean Data with AI")
    
    with col_output:
        st.subheader("Structured Output (JSON)")
        if clean_btn:
            result = clean_product_text_ai(raw_text)
            st.json(result)
            st.success("Extraction Complete!")
