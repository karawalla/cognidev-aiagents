import pytest
from respx import MockRouter

from src.tools.api.clients.rest import RestClient
from src.tools.api.models.config import Method, Protocol, ToolConfig


@pytest.fixture
def rest_config() -> ToolConfig:
    """Create a sample REST client configuration."""
    return ToolConfig(
        protocol=Protocol.REST,
        method=Method.GET,
        url="https://api.example.com/test",
        headers={"Authorization": "Bearer test-token"},
        payload={"key": "value"}
    )


@pytest.mark.asyncio
async def test_successful_get_request(
    rest_config: ToolConfig,
    mock_successful_response: dict,
    respx_mock: MockRouter
) -> None:
    """Test successful GET request with the REST client."""
    # Mock the API response
    route = respx_mock.get(
        "https://api.example.com/test",
        params={"key": "value"}
    ).mock(
        return_value=MockRouter.build_response(200, json=mock_successful_response)
    )
    
    client = RestClient(rest_config)
    response = await client.execute()
    
    assert route.called
    assert response.status == "success"
    assert response.data["result"] == mock_successful_response
    assert response.metadata["status_code"] == 200


@pytest.mark.asyncio
async def test_failed_request(
    rest_config: ToolConfig,
    mock_error_response: dict,
    respx_mock: MockRouter
) -> None:
    """Test failed request handling."""
    # Mock a failed API response
    route = respx_mock.get(
        "https://api.example.com/test"
    ).mock(
        return_value=MockRouter.build_response(404, json=mock_error_response)
    )
    
    client = RestClient(rest_config)
    response = await client.execute()
    
    assert route.called
    assert response.status == "error"
    assert response.data["result"] == mock_error_response
    assert response.metadata["status_code"] == 404


@pytest.mark.asyncio
async def test_retry_mechanism(
    rest_config: ToolConfig,
    mock_successful_response: dict,
    respx_mock: MockRouter
) -> None:
    """Test retry mechanism on temporary failure."""
    # First two calls fail, third succeeds
    route = respx_mock.get(
        "https://api.example.com/test"
    ).mock(
        side_effect=[
            MockRouter.build_response(500),
            MockRouter.build_response(500),
            MockRouter.build_response(200, json=mock_successful_response)
        ]
    )
    
    client = RestClient(rest_config)
    response = await client.execute()
    
    assert route.call_count == 3
    assert response.status == "success"
    assert response.data["result"] == mock_successful_response


@pytest.mark.asyncio
async def test_post_request_with_json(
    rest_config: ToolConfig,
    mock_successful_response: dict,
    respx_mock: MockRouter
) -> None:
    """Test POST request with JSON payload."""
    rest_config.method = Method.POST
    
    route = respx_mock.post(
        "https://api.example.com/test"
    ).mock(
        return_value=MockRouter.build_response(201, json=mock_successful_response)
    )
    
    client = RestClient(rest_config)
    response = await client.execute()
    
    assert route.called
    assert response.status == "success"
    assert response.metadata["status_code"] == 201
    assert route.calls.last.request.content == b'{"key": "value"}'


@pytest.mark.asyncio
async def test_timeout_handling(rest_config: ToolConfig, respx_mock: MockRouter) -> None:
    """Test request timeout handling."""
    rest_config.timeout = 1  # 1ms timeout
    
    route = respx_mock.get(
        "https://api.example.com/test"
    ).mock(side_effect=TimeoutError)
    
    client = RestClient(rest_config)
    response = await client.execute()
    
    assert route.called
    assert response.status == "error"
    assert "timeout" in str(response.data["error"]).lower()
