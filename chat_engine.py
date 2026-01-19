import pandas as pd
import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_analysis.db")

class DataChatAgent:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    def ask(self, question):
        """
        Translates natural language to SQL and returns the result df.
        """
        question = question.lower().strip()
        sql = None
        interpretation = ""
        
        # --- Simple Rule-Based NLP ---
        
        # 1. Total Revenue
        if "total revenue" in question or "how much sales" in question:
            sql = "SELECT SUM(quantity * price) as Total_Revenue FROM invoice_items"
            interpretation = "Calculating total global revenue."
            
        # 2. Top Customers
        elif "top customer" in question or "best customer" in question:
            limit = 5
            match = re.search(r"top (\d+)", question)
            if match:
                limit = match.group(1)
            sql = f"""
                SELECT i.customer_id, SUM(ii.quantity * ii.price) as total_spend
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.invoice_id
                GROUP BY i.customer_id
                ORDER BY total_spend DESC
                LIMIT {limit}
            """
            interpretation = f"Listing top {limit} customers by spend."

        # 3. Sales by Country
        elif "by country" in question or "which country" in question:
            sql = """
                SELECT country, SUM(ii.quantity * ii.price) as revenue
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.invoice_id
                GROUP BY country
                ORDER BY revenue DESC
            """
            interpretation = "Aggregating revenue by country."

        # 4. Sales IN a specific Country (Parametric)
        # e.g. "sales in France"
        elif "sales in" in question or "revenue in" in question:
            country_match = re.search(r"in\s+([a-zA-Z\s]+)", question)
            if country_match:
                country = country_match.group(1).title().strip() 
                # Note: This is case sensitive in SQL usually, but we use title() as guess
                sql = f"""
                    SELECT SUM(ii.quantity * ii.price) as Revenue_in_{country.replace(' ', '_')}
                    FROM invoice_items ii
                    JOIN invoices i ON ii.invoice_id = i.invoice_id
                    WHERE i.country LIKE '{country}%'
                """
                interpretation = f"Calculating revenue specifically for {country}."
        
        # 5. Top Products
        elif "top product" in question or "best selling" in question:
            sql = """
                SELECT description, SUM(quantity) as units_sold
                FROM invoice_items
                GROUP BY description
                ORDER BY units_sold DESC
                LIMIT 10
            """
            interpretation = "Identifying top 10 best-selling products."

        # --- Execution ---
        if sql:
            try:
                df = pd.read_sql(sql, self.conn)
                return {
                    "answer": "Here is the data:",
                    "dataframe": df,
                    "sql": sql,
                    "interpretation": interpretation
                }
            except Exception as e:
                return {
                    "answer": f"I tried to run SQL but failed: {e}",
                    "sql": sql,
                    "interpretation": interpretation
                }
        else:
            return {
                "answer": "I didn't understand that. Try asking about 'Total revenue', 'Top customers', 'Sales by country', or 'Sales in France'.",
                "dataframe": None
            }

if __name__ == "__main__":
    agent = DataChatAgent()
    print("Test 1:", agent.ask("What is total revenue?"))
    print("Test 2:", agent.ask("Show top 3 customers"))
    print("Test 3:", agent.ask("Sales in United Kingdom"))
