import asyncio
import time
from typing import Any, Dict

import httpx

from ..base import BaseAPIClient
from ..models.config import Method, ToolResponse


class RestClient(BaseAPIClient):
    """REST API client implementation."""
    
    async def execute(self) -> ToolResponse:
        """Execute a REST API call with retry support."""
        attempt = 1
        last_error = None

        while attempt <= self.config.retry.max_attempts:
            try:
                return await self._make_request()
            except Exception as e:
                last_error = e
                if attempt < self.config.retry.max_attempts:
                    await asyncio.sleep(self.config.retry.delay / 1000)  # Convert to seconds
                attempt += 1
        
        return self._build_response(
            status="error",
            result={"error": str(last_error)},
            metadata=self._build_metadata(
                status_code=500,
                headers={},
                timing=-1
            )
        )

    async def _make_request(self) -> ToolResponse:
        """Make the actual HTTP request."""
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=self.config.timeout / 1000) as client:
            method = self.config.method or Method.GET
            response = await client.request(
                method=method.value,
                url=str(self.config.url),
                headers=self.config.headers,
                json=self.config.payload if method != Method.GET else None,
                params=self.config.payload if method == Method.GET else None
            )
            
            timing = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            try:
                result = response.json()
            except Exception:
                result = {"text": response.text}
            
            return self._build_response(
                status="success" if response.is_success else "error",
                result=result,
                metadata=self._build_metadata(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    timing=timing
                )
            )
