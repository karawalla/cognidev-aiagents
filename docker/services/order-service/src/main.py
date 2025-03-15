from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

# Models
class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Order(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: str
    created_at: datetime

class OrderResponse(BaseModel):
    status: str
    data: Optional[Order] = None
    error: Optional[str] = None

# Mock database
orders: Dict[str, Order] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting order service...")
    yield
    # Shutdown
    print("Shutting down order service...")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Get order by ID."""
    if order_id not in orders:
        return OrderResponse(
            status="error",
            error="Order not found"
        )
    
    return OrderResponse(
        status="success",
        data=orders[order_id]
    )

@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(order: Order):
    """Create a new order."""
    if order.id in orders:
        return OrderResponse(
            status="error",
            error="Order already exists"
        )
    
    order.created_at = datetime.utcnow()
    orders[order.id] = order
    
    return OrderResponse(
        status="success",
        data=order
    )

@app.get("/api/v1/users/{user_id}/orders", response_model=List[Order])
async def get_user_orders(user_id: str):
    """Get all orders for a user."""
    user_orders = [
        order for order in orders.values()
        if order.user_id == user_id
    ]
    return user_orders
