from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..tools.api.factory import APIClientFactory
from ..tools.api.models.config import ToolConfig, ToolResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup (empty for now, will add DB/cache later)
    yield
    # Cleanup (empty for now)


app = FastAPI(
    title="AI Agents API Tool",
    description="Enterprise API Tool for executing various API calls",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/v1/tools/api/execute", response_model=ToolResponse)
async def execute_api_call(config: ToolConfig) -> ToolResponse:
    """Execute an API call based on the provided configuration."""
    try:
        client = APIClientFactory.create(config)
        return await client.execute()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for consistent error responses."""
    status_code = 500
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "data": {"error": str(exc)},
            "metadata": {"path": request.url.path}
        }
    )
