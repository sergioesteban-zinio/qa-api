from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

app = FastAPI(title="Mocked QA API")

# --- MODELS ---

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
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    specs: Specs = Specs()
    reviews: List[Review] = []


# --- INITIAL DATA ---

items: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "name": "Laptop",
        "description": "A high-end gaming laptop",
        "tags": ["electronics", "gaming", "portable"],
        "specs": {
            "weight": "2.5kg",
            "color": "black",
            "dimensions": "35x25x2cm"
        },
        "reviews": [
            {"user": "Alice", "rating": 5, "comment": "Fantastic performance!"},
            {"user": "Bob", "rating": 4, "comment": "Great but heavy."}
        ]
    },
    2: {
        "id": 2,
        "name": "Phone",
        "description": "A smartphone with a great camera",
        "tags": ["electronics", "mobile"],
        "specs": {
            "weight": "180g",
            "color": "blue",
            "dimensions": "15x7x0.8cm"
        },
        "reviews": [
            {"user": "Charlie", "rating": 5, "comment": "Best camera I've used!"},
            {"user": "Dana", "rating": 3, "comment": "Battery life could be better."}
        ]
    },
    3: {
        "id": 3,
        "name": "Headphones",
        "description": "Noise-cancelling over-ear headphones",
        "tags": ["audio", "music", "wireless"],
        "specs": {
            "weight": "300g",
            "color": "silver",
            "dimensions": "20x18x9cm"
        },
        "reviews": [
            {"user": "Eve", "rating": 4, "comment": "Excellent noise cancellation."}
        ]
    },
}

# --- ENDPOINTS ---

@app.get("/items")
def get_items():
    return list(items.values())

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.post("/items")
def create_item(item: Item):
    if item.id in items:
        raise HTTPException(status_code=400, detail="Item already exists")
    items[item.id] = item.dict()
    return {"message": "Item created", "item": item}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item.dict()
    return {"message": "Item updated", "item": item}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"message": "Item deleted"}
