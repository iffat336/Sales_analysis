import pandas as pd
import sqlite3
import os

# Configuration
EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "online_retail_II.xlsx")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_analysis.db")

def create_connection(db_file):
    """create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """create tables in the SQLite database"""
    try:
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Customers Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id REAL PRIMARY KEY
            );
        """)

        # Products Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                stock_code TEXT PRIMARY KEY,
                description TEXT
            );
        """)

        # Invoices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                customer_id REAL,
                invoice_date TIMESTAMP,
                country TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            );
        """)

        # Invoice Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT,
                stock_code TEXT,
                quantity INTEGER,
                price REAL,
                FOREIGN KEY (invoice_id) REFERENCES invoices (invoice_id),
                FOREIGN KEY (stock_code) REFERENCES products (stock_code)
            );
        """)
        
        # Create a View for easier querying (replicates the flat file structure)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS transactions_view AS
            SELECT 
                i.invoice_id,
                ii.stock_code,
                p.description,
                ii.quantity,
                i.invoice_date,
                ii.price,
                i.customer_id,
                i.country
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.invoice_id
            JOIN products p ON ii.stock_code = p.stock_code;
        """)

        print("Tables and Views created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

def load_data_to_db(conn, excel_path):
    print(f"Loading data from {excel_path}...")
    try:
        # Load data
        df = pd.read_excel(excel_path)
        
        # Data Cleaning as per notebook
        print("Cleaning data...")
        df = df.dropna(subset=["Customer ID"])
        df = df[~df['Invoice'].astype(str).str.startswith('C')] # Remove cancelled
        df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
        
        # 1. Populate Customers
        print("Populating Customers...")
        customers = df[['Customer ID']].drop_duplicates()
        customers.columns = ['customer_id']
        customers.to_sql('customers', conn, if_exists='append', index=False, method='multi', chunksize=500)
        
        # 2. Populate Products
        # Note: Descriptions might vary for the same StockCode; taking the first one found or most frequent is a choice.
        # Here we drop duplicates on StockCode to have a unique list.
        print("Populating Products...")
        products = df[['StockCode', 'Description']].drop_duplicates(subset=['StockCode'])
        products.columns = ['stock_code', 'description']
        # Convert StockCode to string to ensure consistency (sometimes pandas infers weird types)
        products['stock_code'] = products['stock_code'].astype(str)
        products.to_sql('products', conn, if_exists='append', index=False, method='multi', chunksize=500)

        # 3. Populate Invoices
        print("Populating Invoices...")
        invoices = df[['Invoice', 'Customer ID', 'InvoiceDate', 'Country']].drop_duplicates(subset=['Invoice'])
        invoices.columns = ['invoice_id', 'customer_id', 'invoice_date', 'country']
        invoices['invoice_id'] = invoices['invoice_id'].astype(str)
        invoices.to_sql('invoices', conn, if_exists='append', index=False, method='multi', chunksize=500)
        
        # 4. Populate Invoice Items
        print("Populating Invoice Items...")
        items = df[['Invoice', 'StockCode', 'Quantity', 'Price']]
        items.columns = ['invoice_id', 'stock_code', 'quantity', 'price']
        items['invoice_id'] = items['invoice_id'].astype(str)
        items['stock_code'] = items['stock_code'].astype(str)
        items.to_sql('invoice_items', conn, if_exists='append', index=False, method='multi', chunksize=500)
        
        print("Data insertion complete.")
        
    except Exception as e:
        print(f"Error loading data: {e}")

def main():
    if os.path.exists(DB_PATH):
        print(f"Database already exists at {DB_PATH}. Deleting for fresh start...")
        os.remove(DB_PATH)

    conn = create_connection(DB_PATH)
    if conn is not None:
        create_tables(conn)
        load_data_to_db(conn, EXCEL_PATH)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
