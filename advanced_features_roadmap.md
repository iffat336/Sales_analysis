# 🚀 Advanced Sales Intelligence Roadmap

We will merge all 3 scenarios into a single **"Super Dashboard"** using Streamlit Tabs. This creates a unified, professional portfolio piece.

## 📱 The Unified App Structure

We will update `streamlit_app.py` to feature **5 Main Tabs**:

1.  **📊 Executive Overview** (Existing)
    *   Current KPIs, Charts, and Dataframes.
2.  **🔮 Forecast Studio** (Scenario 2)
    *   *Goal*: Predict revenue for the next 30-90 days.
    *   *Tech*: Time-Series forecasting (using `prophet` or `statsmodels`).
    *   *Visual*: A historical line chart that extends into the future with a "cone of uncertainty."
3.  **🛍️ Market Basket Analysis** (Scenario 3)
    *   *Goal*: "Customers who bought X also bought Y."
    *   *Tech*: Association Rules (Apriori Algorithm using `mlxtend`).
    *   *Visual*: A network graph or simple "Recommended Products" list based on a selected item.
4.  **🤖 Data Chat Assistant** (Scenario 1)
    *   *Goal*: Natural Language Interface ("Show me sales for France").
    *   *Tech*: Text-to-SQL logic (using basic keyword mapping or `pandas` filtering for the MVP).
    *   *Visual*: Chat-input box and a dynamic result table.
5.  **🧹 AI Data Cleaner** (Existing)
    *   The Regex/AI module we just built.

---

## 🛠️ Implementation Dependencies

To achieve this, we need to install the following Python libraries:

```text
scikit-learn    # For general regression/metrics
statsmodels     # For robust time-series forecasting (ARIMA/Holt-Winters)
mlxtend         # For Market Basket Analysis (Apriori algorithm)
matplotlib      # Helper for some advanced plotting
```

## 📅 Step-by-Step Execution Plan

### Step 1: Forecasting (The "Future Forecaster")
*   Create `forecasting_engine.py`.
*   Aggregate daily sales from the DB.
*   Train a model (Holt-Winters or ARIMA).
*   Add the "Forecast" tab to Streamlit.

### Step 2: Recommendations (The "Smart Engine")
*   Create `recommender_engine.py`.
*   Process the transaction matrix.
*   Generate "Lift" and "Confidence" scores.
*   Add the "Recommendations" tab to Streamlit.

### Step 3: Integration (Merging)
*   Refactor `streamlit_app.py` to handle the new heavy computations efficiently (using `@st.cache_data`).
