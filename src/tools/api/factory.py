from typing import Type

from .base import BaseAPIClient
from .clients.rest import RestClient
from .models.config import Protocol, ToolConfig


class APIClientFactory:
    """Factory for creating API clients based on protocol."""
    
    _clients = {
        Protocol.REST: RestClient,
        # We'll add GraphQL and gRPC clients later
        # Protocol.GRAPHQL: GraphQLClient,
        # Protocol.GRPC: GRPCClient,
    }
    
    @classmethod
    def create(cls, config: ToolConfig) -> BaseAPIClient:
        """Create an appropriate API client based on the protocol."""
        client_class = cls._clients.get(config.protocol)
        if not client_class:
            raise ValueError(f"Unsupported protocol: {config.protocol}")
        
        return client_class(config)
