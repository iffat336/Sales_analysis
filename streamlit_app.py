import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys
import subprocess

# Config
st.set_page_config(page_title="Sales Dashboard", layout="wide")

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

# Sidebar
st.sidebar.title("Admin")
if st.sidebar.button("Rebuild Database"):
    with st.spinner("Rebuilding Database... This may take a minute."):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_database.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            st.sidebar.success("Database Rebuilt Successfully!")
            st.cache_data.clear() # Clear cache to refresh data
        else:
            st.sidebar.error(f"Error: {result.stderr}")

# Main Layout
st.title("Sales Analytics Dashboard")
st.markdown("Real-time view of `sales_analysis.db`")

# Top Metrics
col1, col2, col3 = st.columns(3)

# 1. Total Revenue
revenue_df = run_query("""
    SELECT SUM(quantity * price) as revenue FROM invoice_items
""")
total_revenue = revenue_df['revenue'].iloc[0] if not revenue_df.empty else 0

with col1:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

# 2. Total Transactions
tx_df = run_query("SELECT COUNT(*) as count FROM invoices")
tx_count = tx_df['count'].iloc[0]

with col2:
    st.metric("Total Invoices", f"{tx_count:,}")

# 3. Top Country
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

# Monthly Sales
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

# Top Customers
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

# Raw Data
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
