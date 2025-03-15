from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

# Models
class User(BaseModel):
    id: str
    name: str
    email: str
    status: str

class UserResponse(BaseModel):
    status: str
    data: Optional[User] = None
    error: Optional[str] = None

# Mock database
users: Dict[str, User] = {
    "123": User(
        id="123",
        name="Test User",
        email="test@example.com",
        status="active"
    )
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting user service...")
    yield
    # Shutdown
    print("Shutting down user service...")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID."""
    if user_id not in users:
        return UserResponse(
            status="error",
            error="User not found"
        )
    
    return UserResponse(
        status="success",
        data=users[user_id]
    )

@app.post("/api/v1/users", response_model=UserResponse)
async def create_user(user: User):
    """Create a new user."""
    if user.id in users:
        return UserResponse(
            status="error",
            error="User already exists"
        )
    
    users[user.id] = user
    return UserResponse(
        status="success",
        data=user
    )
