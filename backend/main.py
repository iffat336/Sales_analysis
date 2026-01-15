from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import os
from . import models, database
from pydantic import BaseModel
from datetime import datetime

# Initialize App
app = FastAPI(title="Sales Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local dev convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Schemas ---
class ProductSchema(BaseModel):
    stock_code: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class InvoiceItemSchema(BaseModel):
    stock_code: str
    description: Optional[str] = None # Enriched from product
    quantity: int
    price: float
    
    class Config:
        from_attributes = True

class InvoiceSchema(BaseModel):
    invoice_id: str
    customer_id: Optional[float]
    invoice_date: Optional[datetime]
    country: Optional[str]
    items: List[InvoiceItemSchema] = []

    class Config:
        from_attributes = True

# --- Routes ---



# Mount Frontend (Static Files)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure frontend directory exists
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

app.mount("/", StaticFiles(directory=frontend_path), name="static")

@app.get("/products", response_model=List[ProductSchema])
def read_products(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@app.get("/search/products/{query}")
def search_products(query: str, db: Session = Depends(get_db)):
    """Search products by description"""
    products = db.query(models.Product).filter(models.Product.description.contains(query)).limit(20).all()
    return products

@app.get("/transactions", response_model=List[InvoiceSchema])
def read_transactions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get transactions with their items. 
    Note: loading items might be heavy if not optimized, but good for inspection.
    """
    invoices = db.query(models.Invoice).offset(skip).limit(limit).all()
    # Manual join for item descriptions if needed, but SQLAlchemy handles relationships
    return invoices

@app.get("/stats/revenue/by-country")
def get_revenue_by_country(db: Session = Depends(get_db)):
    """
    Aggregate revenue by country.
    """
    # Using raw SQL for aggregation as it's often cleaner for analytics
    result = db.execute(text("""
        SELECT i.country, SUM(ii.quantity * ii.price) as total_revenue
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.invoice_id
        GROUP BY i.country
        ORDER BY total_revenue DESC
    """)).fetchall()
    
    return [{"country": row[0], "total_revenue": row[1]} for row in result]

# --- Analytics Endpoints ---

@app.get("/analytics/monthly-sales")
def get_monthly_sales(db: Session = Depends(get_db)):
    """Aggregate revenue by month."""
    result = db.execute(text("""
        SELECT strftime('%Y-%m', i.invoice_date) as month, SUM(ii.quantity * ii.price) as revenue
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.invoice_id
        GROUP BY month
        ORDER BY month
    """)).fetchall()
    return [{"month": row[0], "revenue": row[1]} for row in result]

@app.get("/analytics/top-customers")
def get_top_customers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top customers by total spend."""
    result = db.execute(text(f"""
        SELECT i.customer_id, SUM(ii.quantity * ii.price) as total_spend
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.invoice_id
        GROUP BY i.customer_id
        ORDER BY total_spend DESC
        LIMIT {limit}
    """)).fetchall()
    return [{"customer_id": row[0], "total_spend": row[1]} for row in result]

# --- System Integration ---

import sys
import subprocess

@app.post("/system/rebuild-database")
def rebuild_database():
    """
    WARNING: This triggers the backend script to recreate the database.
    It will delete and repopulate all data.
    """
    try:
        # Assuming create_database.py is in the parent directory
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "create_database.py")
        
        # Run it as a subprocess to ensure clean execution environment
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            return {"status": "success", "message": "Database rebuilt successfully", "log": result.stdout}
        else:
            raise HTTPException(status_code=500, detail=f"Script failed: {result.stderr}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

