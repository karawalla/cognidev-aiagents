import pytest
from fastapi import status
from httpx import AsyncClient

from src.tools.api.models.config import Method, Protocol


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await async_client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_execute_rest_api_call(
    async_client: AsyncClient,
    respx_mock
) -> None:
    """Test successful REST API call execution."""
    mock_response = {"data": "test_response"}
    respx_mock.get("https://api.example.com/test").mock(
        return_value=respx_mock.build_response(200, json=mock_response)
    )
    
    payload = {
        "protocol": "rest",
        "method": "GET",
        "url": "https://api.example.com/test",
        "headers": {"Authorization": "Bearer test-token"},
        "payload": {"test": "data"}
    }
    
    response = await async_client.post("/v1/tools/api/execute", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["status"] == "success"
    assert "result" in response_data["data"]
    assert response_data["metadata"]["status_code"] == 200


@pytest.mark.asyncio
async def test_execute_api_call_invalid_protocol(async_client: AsyncClient) -> None:
    """Test API call with invalid protocol."""
    payload = {
        "protocol": "invalid",
        "url": "https://api.example.com/test"
    }
    
    response = await async_client.post("/v1/tools/api/execute", json=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_execute_api_call_missing_url(async_client: AsyncClient) -> None:
    """Test API call with missing URL."""
    payload = {
        "protocol": "rest",
        "method": "GET"
    }
    
    response = await async_client.post("/v1/tools/api/execute", json=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_execute_api_call_server_error(
    async_client: AsyncClient,
    respx_mock
) -> None:
    """Test API call handling of server errors."""
    respx_mock.get("https://api.example.com/test").mock(
        return_value=respx_mock.build_response(500, json={"error": "server error"})
    )
    
    payload = {
        "protocol": "rest",
        "method": "GET",
        "url": "https://api.example.com/test"
    }
    
    response = await async_client.post("/v1/tools/api/execute", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["status"] == "error"
    assert response_data["metadata"]["status_code"] == 500


@pytest.mark.asyncio
async def test_execute_api_call_timeout(
    async_client: AsyncClient,
    respx_mock
) -> None:
    """Test API call timeout handling."""
    respx_mock.get("https://api.example.com/test").mock(side_effect=TimeoutError)
    
    payload = {
        "protocol": "rest",
        "method": "GET",
        "url": "https://api.example.com/test",
        "timeout": 1  # 1ms timeout
    }
    
    response = await async_client.post("/v1/tools/api/execute", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["status"] == "error"
    assert "timeout" in str(response_data["data"]["error"]).lower()
