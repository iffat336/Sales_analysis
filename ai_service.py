from fastapi import FastAPI
from pydantic import BaseModel
import re

# This is the "Microservice" you pitched to Thorin.
# Ideally, you would import 'openai' here, but for the demo
# we will use simple Python logic to SIMULATE the AI.

app = FastAPI()

class ProductRequest(BaseModel):
    raw_text: str

class ProductInfo(BaseModel):
    brand: str | None
    product_name: str | None
    color: str | None
    size: str | None
    category: str

@app.post("/clean-product", response_model=ProductInfo)
def clean_product_data(item: ProductRequest):
    """
    Simulates AI Cleaning.
    In real life: You would send 'item.raw_text' to OpenAI/GPT-4 via API.
    Here: We use rule-based logic to PROVE it works instantly.
    """
    text = item.raw_text
    
    # --- Mock AI Logic (Regex & Rules) ---
    
    # 1. Detect Brand
    brand = "Generic"
    common_brands = ["Nike", "Adidas", "Puma", "Apple", "Samsung"]
    for b in common_brands:
        if b.lower() in text.lower():
            brand = b
            
    # 2. Detect Color
    color = "Unknown"
    common_colors = ["Red", "Blue", "Black", "White", "Green", "Silver"]
    for c in common_colors:
        if c.lower() in text.lower():
            color = c

    # 3. Detect Size (e.g. Sz 10, Size: 10)
    size = None
    size_match = re.search(r"(?:Size|Sz)[:\s]*(\d+\.?\d*)", text, re.IGNORECASE)
    if size_match:
        size = size_match.group(1)

    # 4. Categorize
    category = "Other"
    if any(x in text.lower() for x in ["shoe", "sneaker", "boot"]):
        category = "Footwear"
    elif any(x in text.lower() for x in ["shirt", "pant", "jacket"]):
        category = "Apparel"
    elif any(x in text.lower() for x in ["phone", "laptop", "watch"]):
        category = "Electronics"

    return {
        "brand": brand,
        "product_name": text,
        "color": color,
        "size": size,
        "category": category
    }

# To Run: uvicorn ai_service:app --reload --port 8001
