import sqlite3
import pandas as pd
import os

DB_PATH = r"D:\data_science_main_folder\projects made by me\Sales_analysis\sales_analysis.db"

def verify_db():
    if not os.path.exists(DB_PATH):
        print(f"FAILED: Database file not found at {DB_PATH}")
        return

    print(f"Database found at {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Check Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        expected_tables = ['customers', 'products', 'invoices', 'invoice_items']
        
        print(f"Tables found: {table_names}")
        
        missing = [t for t in expected_tables if t not in table_names]
        if missing:
            print(f"FAILED: Missing tables: {missing}")
        else:
            print("SUCCESS: All expected tables exist.")
            
        # 2. Check Row Counts
        for table in expected_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table '{table}' has {count} rows.")
            if count == 0:
                print(f"WARNING: Table '{table}' is empty!")
                
        # 3. Check View
        cursor.execute("SELECT COUNT(*) FROM transactions_view")
        view_count = cursor.fetchone()[0]
        print(f"View 'transactions_view' has {view_count} rows.")
        
        # 4. Sample Query
        print("\nSample Data (Top 5 from View):")
        df = pd.read_sql_query("SELECT * FROM transactions_view LIMIT 5", conn)
        print(df)
        
        conn.close()
        
    except Exception as e:
        print(f"FAILED: Error verifying database: {e}")

if __name__ == "__main__":
    verify_db()
