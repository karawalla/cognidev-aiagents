import pytest
from respx import MockRouter
from httpx import Response
from src.tools.api.clients.rest import RestClient
from src.tools.api.models.config import ToolConfig, ToolResponse, Method, Protocol


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


@pytest.fixture
def api_config():
    """Create a sample API configuration."""
    return {
        "base_url": "https://api.example.com",
        "headers": {"Authorization": "Bearer test-token"}
    }


@pytest.fixture
def mock_response_data():
    """Create a sample response data."""
    return {"status": "success"}


@pytest.fixture
def mock_error_response():
    """Create a sample error response."""
    return {"message": "Not Found"}


@pytest.fixture
def http_client():
    """Create a mock HTTP client."""
    return Response(200)


@pytest.mark.asyncio
class TestRestClient:
    async def test_successful_get_request(self, http_client, api_config, mock_response_data):
        """Test successful GET request execution."""
        # Arrange
        client = RestClient(
            base_url=api_config["base_url"],
            headers=api_config["headers"]
        )
        
        # Mock the response
        async def mock_get(*args, **kwargs):
            return Response(200, json=mock_response_data)
        
        http_client.get = mock_get
        client._client = http_client

        # Act
        response = await client.execute()

        # Assert
        assert isinstance(response, ToolResponse)
        assert response.status_code == 200
        assert response.data == mock_response_data

    async def test_failed_request_with_retry(self, http_client, api_config):
        """Test request retry mechanism on failure."""
        # Arrange
        client = RestClient(
            base_url=api_config["base_url"],
            headers=api_config["headers"],
            max_retries=2
        )

        # Mock failing response followed by success
        call_count = 0
        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return Response(500, json={"error": "Internal Server Error"})
            return Response(200, json={"status": "success"})

        http_client.get = mock_get
        client._client = http_client

        # Act
        response = await client.execute()

        # Assert
        assert call_count == 2
        assert response.status_code == 200
        assert response.data == {"status": "success"}

    async def test_request_with_error(self, http_client, api_config, mock_error_response):
        """Test handling of error responses."""
        # Arrange
        client = RestClient(
            base_url=api_config["base_url"],
            headers=api_config["headers"]
        )

        # Mock error response
        async def mock_get(*args, **kwargs):
            return Response(404, json=mock_error_response)

        http_client.get = mock_get
        client._client = http_client

        # Act
        response = await client.execute()

        # Assert
        assert response.status_code == 404
        assert response.error == mock_error_response["message"]


@pytest.mark.asyncio
async def test_successful_get_request(
    rest_config: ToolConfig,
    mock_response_data: dict,
    respx_mock: MockRouter
) -> None:
    """Test successful GET request with the REST client."""
    # Mock the API response
    route = respx_mock.get(
        "https://api.example.com/test",
        params={"key": "value"}
    ).mock(
        return_value=MockRouter.build_response(200, json=mock_response_data)
    )
    
    client = RestClient(rest_config)
    response = await client.execute()
    
    assert route.called
    assert response.status == "success"
    assert response.data["result"] == mock_response_data
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
    mock_response_data: dict,
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
            MockRouter.build_response(200, json=mock_response_data)
        ]
    )
    
    client = RestClient(rest_config)
    response = await client.execute()
    
    assert route.call_count == 3
    assert response.status == "success"
    assert response.data["result"] == mock_response_data


@pytest.mark.asyncio
async def test_post_request_with_json(
    rest_config: ToolConfig,
    mock_response_data: dict,
    respx_mock: MockRouter
) -> None:
    """Test POST request with JSON payload."""
    rest_config.method = Method.POST
    
    route = respx_mock.post(
        "https://api.example.com/test"
    ).mock(
        return_value=MockRouter.build_response(201, json=mock_response_data)
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
