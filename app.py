from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import hashlib

app = FastAPI(title="Shopping Cart")

# -----------------------------
# STATIC CREDENTIALS AND TOKEN
# -----------------------------
EXPECTED_CLIENT = "qa-test"
EXPECTED_SECRET = "zinio"
STATIC_TOKEN = hashlib.sha256(b"qa-test:zinio").hexdigest()  # Example static hash

# -----------------------------
# SIMPLE TOKEN CHECK
# -----------------------------
def check_token(authorization: str = Header(...)):
    """Verify token in Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ")[1]
    if token != STATIC_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

# -----------------------------
# TOKEN REQUEST MODEL
# -----------------------------
class TokenRequest(BaseModel):
    client: str
    client_secret: str

class TokenResponse(BaseModel):
    token: str

# -----------------------------
# MODELS
# -----------------------------
class Review(BaseModel):
    user: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class Specs(BaseModel):
    weight: Optional[str] = None
    color: Optional[str] = None
    dimensions: Optional[str] = None

class Item(BaseModel):
    id: int
    name: str = Field(..., description="Product name (required)")
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    specs: Specs = Specs()
    reviews: List[Review] = Field(default_factory=list)

# -----------------------------
# INITIAL DATA
# -----------------------------
items: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "name": "Laptop", "description": "A high-end gaming laptop", "tags": ["electronics","gaming","portable"], "specs":{"weight":"2.5kg","color":"black","dimensions":"35x25x2cm"}, "reviews":[{"user":"Alice","rating":5},{"user":"Bob","rating":4}]},
    2: {"id": 2, "name": "Phone", "description": "A smartphone with a great camera", "tags":["electronics","mobile"], "specs":{"weight":"180g","color":"blue","dimensions":"15x7x0.8cm"}, "reviews":[{"user":"Charlie","rating":5},{"user":"Dana","rating":3}]},
    3: {"id": 3, "name": "Headphones", "description": "Noise-cancelling headphones", "tags":["audio","music","wireless"], "specs":{"weight":"300g","color":"silver","dimensions":"20x18x9cm"}, "reviews":[{"user":"Eve","rating":4}]}
}

# -----------------------------
# TOKEN ENDPOINT
# -----------------------------
@app.post("/token", response_model=TokenResponse)
def get_token(data: TokenRequest):
    if data.client != EXPECTED_CLIENT or data.client_secret != EXPECTED_SECRET:
        raise HTTPException(status_code=400, detail="Invalid client or client_secret")
    return {"token": STATIC_TOKEN}

# -----------------------------
# PROTECTED ENDPOINTS
# -----------------------------
@app.get("/items", dependencies=[Depends(check_token)])
def get_items(search: Optional[str] = None, tag: Optional[str] = None, min_rating: Optional[int] = None):
    results = list(items.values())
    if search:
        results = [i for i in results if search.lower() in i["name"].lower() or (i.get("description") and search.lower() in i["description"].lower())]
    if tag:
        results = [i for i in results if tag.lower() in [t.lower() for t in i.get("tags", [])]]
    if min_rating:
        def avg_rating(item):
            reviews = item.get("reviews", [])
            return sum(r["rating"] for r in reviews)/len(reviews) if reviews else 0
        results = [i for i in results if avg_rating(i) >= min_rating]
    return results

@app.get("/items/{item_id}", dependencies=[Depends(check_token)])
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.post("/items", dependencies=[Depends(check_token)])
def create_item(item: Item):
    if item.id in items:
        raise HTTPException(status_code=400, detail="Item already exists")
    items[item.id] = item.dict()
    return {"message": "Item created", "item": item}

@app.put("/items/{item_id}", dependencies=[Depends(check_token)])
def update_item(item_id: int, item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item.dict()
    return {"message": "Item updated", "item": item}

@app.delete("/items/{item_id}", dependencies=[Depends(check_token)])
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"message": "Item deleted"}
