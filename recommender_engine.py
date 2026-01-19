import pandas as pd
import sqlite3
import os
from mlxtend.frequent_patterns import apriori, association_rules
import warnings

warnings.filterwarnings("ignore")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_analysis.db")

def get_transaction_matrix():
    """
    Creates a basket matrix: Rows=Invoices, Cols=Products, Value=1 if present.
    To save memory/time, we might filter for top products or a decent sample.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        # Get data: Invoice vs Description
        # We limit to top 200 products by volume to keep Apriori fast for this demo
        query_top_products = """
            SELECT description 
            FROM invoice_items 
            GROUP BY description 
            ORDER BY count(*) DESC 
            LIMIT 200
        """
        try:
            top_products = pd.read_sql(query_top_products, conn)['description'].tolist()
        except:
            print("Warning: Could not fetch top products (Table might be missing)")
            return pd.DataFrame(), []
            
        # Proper escaping for SQL IN clause isn't trivial with pandas read_sql params for list,
        # so we fetch all relevant items and pivot in pandas.
        
        # Proper escaping for SQL IN clause isn't trivial with pandas read_sql params for list,
        # so we fetch all relevant items and pivot in pandas.
        query = """
            SELECT i.invoice_id, ii.description, ii.quantity
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.invoice_id
            WHERE ii.quantity > 0
        """
        df = pd.read_sql(query, conn)
        
        # Filter for top products only
        df = df[df['description'].isin(top_products)]
        
        # Pivot: Invoice x Product
        basket = (df.groupby(['invoice_id', 'description'])['quantity']
                  .sum().unstack().reset_index().fillna(0)
                  .set_index('invoice_id'))
        
        # Encode: >0 to 1, else 0
        def encode_units(x):
            if x <= 0: return 0
            if x >= 1: return 1
            
        basket_encoded = basket.applymap(encode_units)
        return basket_encoded, top_products
    finally:
        conn.close()

def generate_recommendations(min_support=0.02, min_lift=1.0):
    """
    Runs Market Basket Analysis.
    Returns: DataFrame rules
    """
    print("Building transaction matrix...")
    basket, _ = get_transaction_matrix()
    
    if basket.empty:
        return pd.DataFrame()

    print(f"Matrix shape: {basket.shape}. Running Apriori...")
    # 1. Frequent Itemsets
    frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)
    
    if frequent_itemsets.empty:
        print("No frequent itemsets found. Try lowering min_support.")
        return pd.DataFrame()

    # 2. Association Rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)
    
    # Clean up output
    rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x)[0])
    rules['consequents'] = rules['consequents'].apply(lambda x: list(x)[0])
    
    # Sort by Confidence (Strength of prediction)
    rules = rules.sort_values('confidence', ascending=False)
    
    return rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]

if __name__ == "__main__":
    print("Testing Recommender Engine...")
    try:
        rules = generate_recommendations(min_support=0.01) # Low support for demo data
        print(f"Success! Found {len(rules)} association rules.")
        if not rules.empty:
            print(rules.head(5))
    except Exception as e:
        print(f"Error: {e}")
