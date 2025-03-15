import pytest
from typing import AsyncGenerator
import httpx
from fastapi.testclient import TestClient
from src.service.main import app

pytest_plugins = [
    "tests.fixtures.api",
]

@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for FastAPI application."""
    return TestClient(app)

@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Setup test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
