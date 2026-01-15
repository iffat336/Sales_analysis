# Sales Analysis Database Documentation

This document describes the structure and usage of the `sales_analysis.db` SQLite database.

## Database Overview
- **File**: `sales_analysis.db`
- **Type**: SQLite 3
- **Source Data**: `online_retail_II.xlsx`

## Schema
The database consists of 4 main tables and 1 view.

### 1. `customers`
Stores unique customer identifiers.
- `customer_id` (REAL, PK): Unique ID of the customer.

### 2. `products`
Stores unique products.
- `stock_code` (TEXT, PK): Unique code for the product.
- `description` (TEXT): Description of the product.

### 3. `invoices`
Stores invoice headers.
- `invoice_id` (TEXT, PK): Unique invoice number.
- `customer_id` (REAL, FK): References `customers(customer_id)`.
- `invoice_date` (TIMESTAMP): Date and time of the invoice.
- `country` (TEXT): Country of the customer.

### 4. `invoice_items`
Stores individual line items for each invoice.
- `id` (INTEGER, PK): Auto-incrementing primary key.
- `invoice_id` (TEXT, FK): References `invoices(invoice_id)`.
- `stock_code` (TEXT, FK): References `products(stock_code)`.
- `quantity` (INTEGER): Quantity of the product purchased.
- `price` (REAL): Unit price of the product.

### 5. `transactions_view`
A flattened view joining all tables for easy analysis.
- Columns: `invoice_id`, `stock_code`, `description`, `quantity`, `invoice_date`, `price`, `customer_id`, `country`

## Usage Example

```python
import sqlite3
import pandas as pd

# Connect to database
db_path = 'sales_analysis.db'
conn = sqlite3.connect(db_path)

# 1. Query the View (Easiest way to get data)
query = "SELECT * FROM transactions_view LIMIT 5"
df = pd.read_sql(query, conn)
print(df)

# 2. Query Tables Directly
query_items = """
    SELECT i.country, SUM(ii.quantity * ii.price) as total_revenue
    FROM invoice_items ii
    JOIN invoices i ON ii.invoice_id = i.invoice_id
    GROUP BY i.country
    ORDER BY total_revenue DESC
    LIMIT 5
"""
top_countries = pd.read_sql(query_items, conn)
print(top_countries)

conn.close()
```
