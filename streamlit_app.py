import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import subprocess
import re

# --- Custom Modules ---
# Import the engines we just created.
# Note: In a deployed environment, ensure these files are in the same directory.
try:
    import forecasting_engine
    import recommender_engine
    import chat_engine
except ImportError:
    st.error("Modules not found. Please ensure 'forecasting_engine.py', 'recommender_engine.py', and 'chat_engine.py' are present.")

# --- Config ---
st.set_page_config(
    page_title="Retail Intelligence Super-App", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #4B90F9;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_analysis.db")

# --- Helper Functions ---
@st.cache_data(ttl=3600)  # Cache data for 1 hour to improve performance
def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# Reuse the existing cleanup logic
def clean_product_text_ai(text):
    brand = "Generic"
    common_brands = ["Nike", "Adidas", "Puma", "Apple", "Samsung", "Sony", "LG"]
    for b in common_brands:
        if b.lower() in text.lower(): brand = b
    color = "Unknown"
    common_colors = ["Red", "Blue", "Black", "White", "Green", "Silver", "Gold", "Pink"]
    for c in common_colors:
        if c.lower() in text.lower(): color = c
    size = None
    size_match = re.search(r"(?:Size|Sz)[:\s]*(\d+\.?\d*)", text, re.IGNORECASE)
    if size_match: size = size_match.group(1)
    category = "Other"
    if any(x in text.lower() for x in ["shoe", "sneaker", "boot"]): category = "Footwear"
    elif any(x in text.lower() for x in ["shirt", "pant", "jacket", "dress"]): category = "Apparel"
    elif any(x in text.lower() for x in ["phone", "laptop", "watch", "camera"]): category = "Electronics"
    return {"Brand": brand, "Color": color, "Size": size, "Category": category, "Original": text}

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3094/3094918.png", width=80)
st.sidebar.markdown("## 🚀 Retail Intelligence")
st.sidebar.markdown("---")
st.sidebar.info("Features:\n- 📊 KPI Dashboard\n- 🔮 Sales Forecast\n- 🛍️ Product Recommender\n- 🤖 Data Assistant")

if st.sidebar.button("🔄 Rebuild Database"):
    with st.spinner("Rebuilding..."):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "create_database.py")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            st.sidebar.success("Done!")
            st.cache_data.clear()
        else:
            st.sidebar.error(f"Error: {result.stderr}")

# --- Main App Layout ---

# Create 5 Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Overview", 
    "🔮 Forecast Studio", 
    "🛍️ Recommendations", 
    "💬 AI Chat", 
    "🧹 Product Microservice"
])

# --- TAB 1: EXECUTIVE OVERVIEW ---
with tab1:
    st.markdown("<h2 class='main-header'>Real-Time Sales Performance</h2>", unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    revenue_df = run_query("SELECT SUM(quantity * price) as revenue FROM invoice_items")
    total_rev = revenue_df['revenue'].iloc[0] or 0
    col1.metric("Total Revenue", f"${total_rev:,.0f}")
    
    tx_df = run_query("SELECT COUNT(*) as cnt FROM invoices")
    col2.metric("Total Invoices", f"{tx_df['cnt'].iloc[0]:,}")
    
    cust_df = run_query("SELECT COUNT(DISTINCT customer_id) as cnt FROM invoices WHERE customer_id IS NOT NULL")
    col3.metric("Active Customers", f"{cust_df['cnt'].iloc[0]:,}")
    
    avg_df = run_query("SELECT AVG(quantity * price) as val FROM invoice_items")
    col4.metric("Avg Ticket Size", f"${avg_df['val'].iloc[0]:,.2f}")
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue by Country")
        country_df = run_query("""
            SELECT country, SUM(ii.quantity * ii.price) as revenue 
            FROM invoice_items ii JOIN invoices i ON ii.invoice_id = i.invoice_id 
            GROUP BY country ORDER BY revenue DESC LIMIT 10
        """)
        fig_map = px.bar(country_df, x='country', y='revenue', color='revenue', title="Top Markets")
        st.plotly_chart(fig_map, use_container_width=True)
        
    with c2:
        st.subheader("Top Products")
        prod_df = run_query("""
            SELECT description, SUM(quantity * price) as val 
            FROM invoice_items GROUP BY description ORDER BY val DESC LIMIT 10
        """)
        fig_prod = px.pie(prod_df, values='val', names='description', title="Detailed Mix", hole=0.4)
        st.plotly_chart(fig_prod, use_container_width=True)

# --- TAB 2: FORECAST STUDIO ---
with tab2:
    st.title("🔮 Predictive Analytics Engine")
    st.markdown("Uses **Holt-Winters Exponential Smoothing** to project future revenue.")
    
    days = st.slider("Forecast Days", 7, 90, 30)
    
    if st.button("Generate Forecast", key="btn_forecast"):
        with st.spinner("Training models on historical data..."):
            try:
                forecast_df = forecasting_engine.generate_forecast(days)
                
                # Plot
                fig = go.Figure()
                # Historical
                fig.add_trace(go.Scatter(
                    x=forecast_df.index, 
                    y=forecast_df['revenue'], 
                    mode='lines', 
                    name='Historical',
                    line=dict(color='cyan')
                ))
                # Forecast
                fig.add_trace(go.Scatter(
                    x=forecast_df.index, 
                    y=forecast_df['Forecast'], 
                    mode='lines+markers', 
                    name='Forecast',
                    line=dict(color='orange', dash='dash')
                ))
                fig.update_layout(title="Revenue Forecast", xaxis_title="Date", yaxis_title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)
                
                # Show Data
                with st.expander("View Raw Forecast Data"):
                    st.dataframe(forecast_df.tail(days))
            
            except Exception as e:
                st.error(f"Forecasting Error: {e}")

# --- TAB 3: RECOMMENDATIONS ---
with tab3:
    st.title("🛍️ Market Basket Analysis")
    st.markdown("Discover products often bought together (Association Rule Learning).")
    
    if st.button("Train Recommendation Engine"):
        with st.spinner("Analyzing transaction patterns (Apriori Algorithm)..."):
            rules = recommender_engine.generate_recommendations(min_support=0.01)
            st.session_state['rules'] = rules
            st.success(f"Found {len(rules)} association rules!")
    
    if 'rules' in st.session_state and not st.session_state['rules'].empty:
        rules = st.session_state['rules']
        
        # Filter UI
        target_product = st.selectbox("Select a Product to see recommendations:", rules['antecedents'].unique())
        
        recs = rules[rules['antecedents'] == target_product]
        
        if not recs.empty:
            st.subheader(f"Customers who buy '{target_product}' also buy:")
            for _, row in recs.head(5).iterrows():
                conf = row['confidence'] * 100
                st.info(f"👉 **{row['consequents']}** (Confidence: {conf:.1f}%)")
        else:
            st.warning("No strong associations found for this product yet.")
    else:
        st.info("Click 'Train Recommendation Engine' to start.")

# --- TAB 4: AI CHAT ---
with tab4:
    st.title("💬 Talk to Your Data")
    st.markdown("Ask questions in plain English. Example: *'What is total revenue?'* or *'Show top 5 customers'*.")
    
    user_query = st.text_input("Ask a question:")
    if user_query:
        agent = chat_engine.DataChatAgent()
        response = agent.ask(user_query)
        
        st.markdown(f"**Interpretation**: {response.get('interpretation', '')}")
        st.markdown(f"**Answer**: {response['answer']}")
        
        if response.get('dataframe') is not None:
            st.dataframe(response['dataframe'])
            
        with st.expander("View Generated SQL"):
            st.code(response.get('sql', 'No SQL generated'), language='sql')

# --- TAB 5: MICROSERVICE ---
with tab5:
    st.title("🧹 AI Product Cleaner")
    
    col_in, col_out = st.columns(2)
    with col_in:
        raw = st.text_area("Messy Input", "Nike Air Max 90 -- Sz 10 (Red)!", height=150)
        if st.button("Clean"):
            res = clean_product_text_ai(raw)
            st.session_state['clean_res'] = res
            
    with col_out:
        st.json(st.session_state.get('clean_res', {}))
