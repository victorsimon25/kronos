"""
KRONOS API Client Module
Central HTTP transport layer with error handling, timeouts, and health monitoring.
"""

import time
import logging
from typing import Any, Dict, Optional, Tuple
import httpx
from config import BACKEND_URL, API_TIMEOUT_SECONDS

logger = logging.getLogger("kronos.api_client")


class APIError(Exception):
    """Base exception for KRONOS API communication failures."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class BackendUnavailableError(APIError):
    """Raised when the backend server is unreachable (connection refused, DNS failure)."""
    pass


class NotFoundError(APIError):
    """Raised when a requested resource (entity, case, pattern) is not found."""
    pass


class APIClient:
    """
    HTTP client for connecting Streamlit frontend to Core Backend APIs.
    """
    def __init__(self, base_url: str = BACKEND_URL, timeout: float = API_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    def check_health(self) -> Tuple[bool, float, str]:
        """
        Check backend server connectivity and measure response latency.
        Returns (is_online, latency_ms, status_message)
        """
        url = self._build_url("/health")
        start_time = time.perf_counter()
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(url)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 1)
                if response.status_code == 200:
                    return True, latency_ms, "LIVE"
                elif response.status_code == 404:
                    # Backend running but no /health endpoint, check root /
                    root_resp = client.get(self.base_url)
                    if root_resp.status_code in (200, 404, 405):
                        return True, latency_ms, "LIVE (No /health)"
                return False, latency_ms, f"HTTP {response.status_code}"
        except httpx.ConnectError:
            return False, 0.0, "CONNECTION REFUSED"
        except httpx.TimeoutException:
            return False, 0.0, "TIMEOUT"
        except Exception as e:
            return False, 0.0, f"ERROR: {type(e).__name__}"

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform a synchronous HTTP GET request against the backend.
        """
        url = self._build_url(endpoint)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise NotFoundError(f"Resource at '{endpoint}' not found.", status_code=404)
                else:
                    raise APIError(
                        f"Backend returned HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        details=response.text
                    )
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.debug(f"Backend connection failed at {url}: {e}")
            raise BackendUnavailableError(
                f"Cannot connect to Core Backend at '{self.base_url}'. Ensure FastAPI service is running.",
                details=str(e)
            )
        except httpx.TimeoutException as e:
            logger.debug(f"Backend request timed out at {url}: {e}")
            raise APIError(
                f"Backend request to '{endpoint}' timed out after {self.timeout}s.",
                details=str(e)
            )
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected API error at {url}: {e}")
            raise APIError(f"Unexpected client error: {str(e)}", details=str(e))

    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform a synchronous HTTP POST request against the backend.
        """
        url = self._build_url(endpoint)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=json_data)
                if response.status_code in (200, 201):
                    return response.json()
                elif response.status_code == 404:
                    raise NotFoundError(f"Resource at '{endpoint}' not found.", status_code=404)
                else:
                    raise APIError(
                        f"Backend returned HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code
                    )
        except httpx.ConnectError as e:
            raise BackendUnavailableError(
                f"Cannot connect to Core Backend at '{self.base_url}'.",
                details=str(e)
            )
        except httpx.TimeoutException as e:
            raise APIError(f"POST request to '{endpoint}' timed out.", details=str(e))


# Global singleton client instance
api_client = APIClient()
