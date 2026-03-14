"""
Ledger Client - Python client library for Auth & Location services

This module provides a simple Python client for Auth & Location services
to integrate with the tamper-evident ledger HTTP API.
"""

import httpx
import os
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio


class LedgerClient:
    """
    Python client for the Smart Tourist Ledger API
    
    This client handles all HTTP communication with the ledger service
    and provides simple methods for Auth & Location services to log events.
    
    Usage:
        client = LedgerClient()
        result = await client.log_panic_event(tourist_id, location_data)
        proof_hash = result["proof_hash"]  # Use this for immutable proof
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize the ledger client
        
        Args:
            base_url: Base URL of the ledger service (defaults to env var)
            api_key: Internal API key (defaults to env var)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv(
            "LEDGER_SERVICE_URL", 
            "http://localhost:8000/api/v1/internal/ledger"
        )
        self.api_key = api_key or os.getenv("LEDGER_INTERNAL_API_KEY", "dev-key-123")
        self.timeout = timeout
        
        # Create HTTP client with timeout configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"X-API-Key": self.api_key} if self.api_key else {}
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def log_event(
        self, 
        tourist_id: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Log a generic event to the tamper-evident ledger
        
        Args:
            tourist_id: UUID of the tourist
            event_type: Type of event (PANIC, REGISTER, AI_ANOMALY, etc.)
            event_data: Event payload data
            
        Returns:
            Dictionary with success status and proof_hash for immutable proof
            
        Raises:
            LedgerClientError: If the request fails
            
        Example:
            result = await client.log_event(
                tourist_id="123e4567-e89b-12d3-a456-426614174000",
                event_type="REGISTER",
                event_data={
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "phone": "+1234567890"
                }
            )
            proof_hash = result["proof_hash"]  # Store this for immutable proof
        """
        try:
            request_payload = {
                "tourist_id": tourist_id,
                "event_type": event_type,
                "event_data": event_data
            }
            
            response = await self.client.post(
                f"{self.base_url}/events",
                json=request_payload,
                params={"api_key": self.api_key} if self.api_key else {}
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                raise LedgerClientError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except httpx.RequestError as e:
            raise LedgerClientError(f"Network error: {str(e)}")
        except Exception as e:
            raise LedgerClientError(f"Unexpected error: {str(e)}")
    
    async def log_panic_event(
        self, 
        tourist_id: str, 
        location_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        **Convenience method** - Log a panic event to the ledger
        
        This is the most common use case for Auth & Location services.
        
        Args:
            tourist_id: UUID of the tourist who triggered panic
            location_data: Location information dictionary
            
        Returns:
            Dictionary with success status and proof_hash
            
        Example:
            result = await client.log_panic_event(
                tourist_id="123e4567-e89b-12d3-a456-426614174000",
                location_data={
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "timestamp": "2025-09-15T14:30:00Z",
                    "accuracy": 5.0
                }
            )
            proof_hash = result["proof_hash"]  # Include in panic alert response
        """
        return await self.log_event(
            tourist_id=tourist_id,
            event_type="PANIC",
            event_data={
                "location": location_data,
                "event_source": "panic_button",
                "logged_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def log_registration_event(
        self, 
        tourist_id: str, 
        registration_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        **Convenience method** - Log a tourist registration event
        
        Used by Auth service when a new tourist registers.
        
        Args:
            tourist_id: UUID of the newly registered tourist
            registration_data: Registration information
            
        Returns:
            Dictionary with success status and proof_hash
            
        Example:
            result = await client.log_registration_event(
                tourist_id="123e4567-e89b-12d3-a456-426614174000",
                registration_data={
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "phone": "+1234567890",
                    "registration_timestamp": "2025-09-15T10:00:00Z"
                }
            )
        """
        return await self.log_event(
            tourist_id=tourist_id,
            event_type="TOURIST_REGISTERED",
            event_data=registration_data
        )
    
    async def verify_ledger_integrity(self) -> Dict[str, Any]:
        """
        Verify the integrity of the tamper-evident ledger
        
        Returns:
            Dictionary with verification status
            
        Example:
            result = await client.verify_ledger_integrity()
            if result["chain_valid"]:
                print("Ledger is secure and untampered")
            else:
                print("CRITICAL: Ledger tampering detected!")
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/verify",
                params={"api_key": self.api_key} if self.api_key else {}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise LedgerClientError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except httpx.RequestError as e:
            raise LedgerClientError(f"Network error: {str(e)}")
        except Exception as e:
            raise LedgerClientError(f"Unexpected error: {str(e)}")


class LedgerClientError(Exception):
    """Exception raised by LedgerClient operations"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Synchronous wrapper for compatibility
class SyncLedgerClient:
    """
    Synchronous wrapper for LedgerClient
    
    Use this if your code is not async/await compatible.
    
    Usage:
        client = SyncLedgerClient()
        result = client.log_panic_event(tourist_id, location_data)
    """
    
    def __init__(self, **kwargs):
        self._async_client = LedgerClient(**kwargs)
    
    def log_event(self, tourist_id: str, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of log_event"""
        return asyncio.run(self._async_client.log_event(tourist_id, event_type, event_data))
    
    def log_panic_event(self, tourist_id: str, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of log_panic_event"""
        return asyncio.run(self._async_client.log_panic_event(tourist_id, location_data))
    
    def log_registration_event(self, tourist_id: str, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of log_registration_event"""
        return asyncio.run(self._async_client.log_registration_event(tourist_id, registration_data))
    
    def verify_ledger_integrity(self) -> Dict[str, Any]:
        """Synchronous version of verify_ledger_integrity"""
        return asyncio.run(self._async_client.verify_ledger_integrity())
    
    def close(self):
        """Close the underlying async client"""
        asyncio.run(self._async_client.close())


# Convenience functions for quick integration
async def log_panic_event(tourist_id: str, location_data: Dict[str, Any]) -> str:
    """
    **Quick Helper Function** - Log panic event and return proof hash
    
    This is the simplest way to integrate panic logging.
    
    Args:
        tourist_id: UUID of the tourist
        location_data: Location information
        
    Returns:
        proof_hash string for immutable proof
        
    Example:
        proof_hash = await log_panic_event(
            tourist_id="123e4567-e89b-12d3-a456-426614174000",
            location_data={"latitude": 12.9716, "longitude": 77.5946}
        )
        # Include proof_hash in your panic alert response
    """
    async with LedgerClient() as client:
        result = await client.log_panic_event(tourist_id, location_data)
        return result["proof_hash"]


async def log_registration_event(tourist_id: str, registration_data: Dict[str, Any]) -> str:
    """
    **Quick Helper Function** - Log registration event and return proof hash
    
    Args:
        tourist_id: UUID of the tourist
        registration_data: Registration information
        
    Returns:
        proof_hash string for immutable proof
    """
    async with LedgerClient() as client:
        result = await client.log_registration_event(tourist_id, registration_data)
        return result["proof_hash"]
