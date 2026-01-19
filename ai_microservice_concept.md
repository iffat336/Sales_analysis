# How to Build an AI Microservice for ProductFlight
**Goal:** Create a "Black Box" API that takes messy product text and returns clean structured data.

This is the technical blueprint you can pitch to Thorin.

---

## 1. The Concept
ProductFlight receives raw data like: `Nike Air Max -- Size 10 (Red)!!`
They want clean data:
*   **Brand:** Nike
*   **Product:** Air Max
*   **Size:** 10
*   **Color:** Red
*   **Category:** Footwear

You will build a **FastAPI Microservice** that does this transformation automatically.

---

## 2. The Implementation (Code)

You don't need a heavy framework. You can use **FastAPI** + **OpenAI** (simplest) or **spaCy** (free/local).
Here is how the code would look (using OpenAI for powerful reasoning):

### `requirements.txt`
```text
fastapi
uvicorn
openai
pydantic
```

### `ai_service.py`
```python
from fastapi import FastAPI
from pydantic import BaseModel
import openai

app = FastAPI()

# 1. Define the Output Schema (Structure you want)
class ProductInfo(BaseModel):
    brand: str
    product_name: str
    size: str | None
    color: str | None
    category: str

class ProductRequest(BaseModel):
    raw_text: str

# 2. The AI Logic
@app.post("/clean-product", response_model=ProductInfo)
def clean_product_data(item: ProductRequest):
    prompt = f"Extract structured data from this product title: '{item.raw_text}'"
    
    # Call OpenAI (Pseudo-code)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a data extraction assistant. Output JSON."},
            {"role": "user", "content": prompt}
        ],
        functions=[{...}] # Use Function Calling to force JSON output
    )
    
    # Parse and return
    return parse_response(response)
```

---

## 3. The "Docker" Wrap (The Pitch)

Thorin cares about deployment. You tell him:
*"I won't just give you a script. I will give you a **Docker Image**."*

### The `Dockerfile`
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "ai_service:app", "--host", "0.0.0.0", "--port", "80"]
```

### Why this is valuable?
1.  **Scalable**: He can run 1 container or 100 containers depending on traffic.
2.  **Isolated**: It doesn't break his existing code. It just sits there and waits for requests.
3.  **Simple**: He sends raw text -> Gets clean JSON. Magic. ✨

---

## 4. How to Start?
1.  **Get an OpenAI Key** (Cost is pennies for testing).
2.  **Copy the code above** into a new folder.
3.  **Run it locally**: `uvicorn ai_service:app`.
4.  **Test it** with Postman: Send `{"raw_text": "iPhone 12 Pro Max 256GB"}`.
5.  **Show Thorin**: "Look, I feed it garbage, it gives me gold."
