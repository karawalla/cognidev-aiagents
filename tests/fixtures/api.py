import pytest
from typing import Dict, Any

@pytest.fixture
def api_config() -> Dict[str, Any]:
    """Fixture providing a basic API configuration."""
    return {
        "protocol": "rest",
        "base_url": "https://api.example.com",
        "headers": {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
    }

@pytest.fixture
def mock_response_data() -> Dict[str, Any]:
    """Fixture providing mock API response data."""
    return {
        "status": "success",
        "data": {
            "id": "123",
            "name": "Test Resource",
            "created_at": "2025-03-14T19:45:00Z"
        }
    }

@pytest.fixture
def mock_error_response() -> Dict[str, str]:
    """Fixture providing mock API error response."""
    return {
        "status": "error",
        "message": "Resource not found",
        "error_code": "NOT_FOUND"
    }
