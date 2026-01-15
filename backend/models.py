from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    # In the existing DB, customer_id is REAL (Float). 
    # Ideally should be Integer, but we match schema.
    customer_id = Column(Float, primary_key=True, index=True)

class Product(Base):
    __tablename__ = "products"
    
    stock_code = Column(String, primary_key=True, index=True)
    description = Column(String)

class Invoice(Base):
    __tablename__ = "invoices"
    
    invoice_id = Column(String, primary_key=True, index=True)
    customer_id = Column(Float, ForeignKey("customers.customer_id"))
    invoice_date = Column(DateTime)
    country = Column(String)
    
    # Relationships
    customer = relationship("Customer")
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String, ForeignKey("invoices.invoice_id"))
    stock_code = Column(String, ForeignKey("products.stock_code"))
    quantity = Column(Integer)
    price = Column(Float)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")
