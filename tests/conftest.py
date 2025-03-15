import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.service.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> Generator:
    """Create a TestClient instance for synchronous tests."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an AsyncClient instance for async tests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_successful_response() -> dict:
    """Mock successful API response."""
    return {
        "id": "123",
        "name": "Test Resource",
        "status": "active"
    }


@pytest.fixture
def mock_error_response() -> dict:
    """Mock error API response."""
    return {
        "error": "Resource not found",
        "code": "404"
    }
