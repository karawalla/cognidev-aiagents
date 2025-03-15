from abc import ABC, abstractmethod
from typing import Any, Dict

from .models.config import ToolConfig, ToolResponse


class BaseAPIClient(ABC):
    """Base class for all API clients."""
    
    def __init__(self, config: ToolConfig):
        self.config = config
    
    @abstractmethod
    async def execute(self) -> ToolResponse:
        """Execute the API call and return the response."""
        pass
    
    def _build_metadata(self, status_code: int, headers: Dict[str, str], timing: int) -> Dict[str, Any]:
        """Build standard metadata for API responses."""
        return {
            "status_code": status_code,
            "headers": headers,
            "timing": timing
        }
    
    def _build_response(self, status: str, result: Dict[str, Any], metadata: Dict[str, Any]) -> ToolResponse:
        """Build standard tool response."""
        return ToolResponse(
            status=status,
            data={"result": result},
            metadata=metadata
        )
