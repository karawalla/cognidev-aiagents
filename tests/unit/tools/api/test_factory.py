import pytest
from src.tools.api.factory import ClientFactory
from src.tools.api.clients.rest import RestClient


@pytest.mark.asyncio
class TestClientFactory:
    async def test_create_rest_client(self):
        """Test creating a REST client from the factory."""
        # Arrange
        factory = ClientFactory()
        config = {
            "protocol": "rest",
            "base_url": "https://api.example.com",
            "headers": {"Authorization": "Bearer test-token"},
        }

        # Act
        client = await factory.create_client(config)

        # Assert
        assert isinstance(client, RestClient)
        assert client.base_url == "https://api.example.com"
        assert client.headers == {"Authorization": "Bearer test-token"}

    async def test_create_client_invalid_protocol(self):
        """Test creating a client with an invalid protocol raises an error."""
        # Arrange
        factory = ClientFactory()
        config = {
            "protocol": "invalid",
            "base_url": "https://api.example.com",
        }

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported protocol: invalid"):
            await factory.create_client(config)
