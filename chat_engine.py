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
        
        # 1. Sales by Country (Global Breakdown)
        if ("by country" in question) or ("breakdown" in question and "country" in question):
            sql = """
                SELECT country, SUM(ii.quantity * ii.price) as revenue
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.invoice_id
                GROUP BY country
                ORDER BY revenue DESC
            """
            interpretation = "Aggregating revenue by country."

        # 2. Sales IN a specific Country (Filter)
        elif (" in " in question) and ("sales" in question or "revenue" in question):
            # Regex to find the word after "in"
            # We look for "in [Word] [Optional Word]"
            country_match = re.search(r" in ([a-zA-Z]+(?:\s[a-zA-Z]+)?)", question)
            if country_match:
                raw_country = country_match.group(1).strip()
                # Handle "the uk", "the us" case
                if raw_country in ["uk", "united kingdom"]: search_term = "United Kingdom"
                elif raw_country in ["us", "usa", "united states"]: search_term = "USA"
                elif raw_country == "france": search_term = "France"
                elif raw_country == "germany": search_term = "Germany"
                elif raw_country == "australia": search_term = "Australia"
                else: search_term = raw_country.title()
                
                sql = f"""
                    SELECT SUM(ii.quantity * ii.price) as Revenue_in_{search_term.replace(' ', '_')}
                    FROM invoice_items ii
                    JOIN invoices i ON ii.invoice_id = i.invoice_id
                    WHERE i.country LIKE '%{search_term}%'
                """
                interpretation = f"Calculating revenue for {search_term}."
            else:
                # Fallback if we see "in" but can't parse country, default to Total
                sql = "SELECT SUM(quantity * price) as Total_Revenue FROM invoice_items"
                interpretation = "Could not detect country, showing Total Revenue."

        # 3. Total Revenue (Broad match)
        elif "revenue" in question or "sales" in question or "how much" in question:
            sql = "SELECT SUM(quantity * price) as Total_Revenue FROM invoice_items"
            interpretation = "Calculating total global revenue."

        # 4. Top Customers
        elif "customer" in question:
            limit = 5
            match = re.search(r"(\d+)", question)
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
            interpretation = f"Listing top {limit} customers."

        # 5. Top Products
        elif "product" in question or "item" in question or "best selling" in question:
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
                    "answer": f"Found it! {interpretation}",
                    "dataframe": df,
                    "sql": sql,
                    "interpretation": interpretation
                }
            except Exception as e:
                return {
                    "answer": f"I tried to run SQL but failed: {e}",
                    "dataframe": None
                }
        else:
            return {
                "answer": f"I didn't understand '{question}'. Try: 'Total Revenue', 'Sales in France', 'Top 5 Customers'.",
                "dataframe": None
            }

if __name__ == "__main__":
    agent = DataChatAgent()
    print("Test 1:", agent.ask("What is total revenue?"))
    print("Test 2:", agent.ask("Show top 3 customers"))
    print("Test 3:", agent.ask("Sales in United Kingdom"))
