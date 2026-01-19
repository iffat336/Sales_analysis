from fastapi.testclient import TestClient
from ai_service import app
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

client = TestClient(app)

def test_clean_product():
    # Test case 1: Nike Shoe
    payload = {"raw_text": "Nike Air Max 90 Shoe Size 10 Red"}
    response = client.post("/clean-product", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code != 200:
        print(f"[FAILED] Status {response.status_code}")
        return

    data = response.json()
    assert data["brand"] == "Nike"
    assert data["category"] == "Footwear"
    assert data["color"] == "Red"
    assert data["size"] == "10"
    print("[SUCCESS] Nike Shoe cleaned correctly")

    # Test case 2: Apple Laptop
    payload = {"raw_text": "Apple MacBook Pro Laptop Silver"}
    response = client.post("/clean-product", json=payload)
    data = response.json()
    assert data["brand"] == "Apple"
    assert data["category"] == "Electronics"
    print("[SUCCESS] Apple Laptop cleaned correctly")

if __name__ == "__main__":
    try:
        test_clean_product()
        print("\nAI SERVICE TESTS PASSED")
    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        exit(1)
