from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, HttpUrl


class Protocol(str, Enum):
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"


class Method(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class RetryConfig(BaseModel):
    max_attempts: int = Field(default=3, ge=1)
    delay: int = Field(default=1000, ge=0, description="Delay in milliseconds")


class ToolConfig(BaseModel):
    protocol: Protocol
    method: Optional[Method] = None  # Optional as GraphQL doesn't use HTTP methods
    url: HttpUrl
    headers: Dict[str, str] = Field(default_factory=dict)
    payload: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = Field(default=5000, ge=0, description="Timeout in milliseconds")
    retry: RetryConfig = Field(default_factory=RetryConfig)


class ToolResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
