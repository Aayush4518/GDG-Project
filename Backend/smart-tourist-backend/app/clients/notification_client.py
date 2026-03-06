"""
Notification Client - Python client library for Auth & Location services

This module provides a simple Python client for Auth & Location services
to publish events (LOCATION_UPDATE, PANIC_ALERT) to the dashboard.
"""

import httpx
import os
import uuid
from typing import Dict, Any, Optional, Literal
from datetime import datetime
import asyncio


class NotificationClient:
    """
    Python client for the Smart Tourist Notification API
    
    This client handles HTTP communication with the notification service
    and provides simple methods for Auth & Location services to publish events.
    
    Usage:
        client = NotificationClient()
        result = await client.publish_panic_alert(tourist_id, name, location, message)
        event_id = result["event_id"]  # Use this for tracking
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize the notification client
        
        Args:
            base_url: Base URL of the notification service
            api_key: Internal API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv(
            "NOTIFICATION_SERVICE_URL",
            "http://localhost:8000/api/v1/internal/notifications"
        )
        self.api_key = api_key or os.getenv("NOTIFICATION_INTERNAL_API_KEY", "dev-notify-123")
        self.timeout = timeout
        
        # Create HTTP client
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
    
    async def publish(
        self,
        event_type: Literal["LOCATION_UPDATE", "PANIC_ALERT"],
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish a generic event to the notification service
        
        Args:
            event_type: Type of event (LOCATION_UPDATE or PANIC_ALERT)
            payload: Event payload data
            
        Returns:
            Dictionary with success status and event_id for tracking
            
        Raises:
            NotificationClientError: If the request fails
        """
        try:
            # Add event_type to payload
            full_payload = {
                "event_type": event_type,
                **payload
            }
            
            response = await self.client.post(
                f"{self.base_url}/publish",
                json=full_payload,
                params={"api_key": self.api_key} if self.api_key else {}
            )
            
            if response.status_code == 202:  # Accepted
                return response.json()
            else:
                raise NotificationClientError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except httpx.RequestError as e:
            raise NotificationClientError(f"Network error: {str(e)}")
        except Exception as e:
            raise NotificationClientError(f"Unexpected error: {str(e)}")
    
    async def publish_location_update(
        self,
        tourist_id: str,
        name: str,
        location: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        **Convenience method** - Publish a LOCATION_UPDATE event
        
        Args:
            tourist_id: UUID of the tourist
            name: Tourist's full name
            location: Location data with latitude, longitude, timestamp
            
        Returns:
            Dictionary with success status and event_id
            
        Example:
            result = await client.publish_location_update(
                tourist_id="123e4567-e89b-12d3-a456-426614174000",
                name="Alice Johnson",
                location={
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "timestamp": "2025-09-15T14:30:00Z",
                    "accuracy": 5.0
                }
            )
            event_id = result["event_id"]  # Store for tracking
        """
        try:
            payload = {
                "tourist_id": tourist_id,
                "name": name,
                "location": location
            }
            
            response = await self.client.post(
                f"{self.base_url}/location-update",
                json=payload,
                params={"api_key": self.api_key} if self.api_key else {}
            )
            
            if response.status_code == 202:
                return response.json()
            else:
                raise NotificationClientError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except httpx.RequestError as e:
            raise NotificationClientError(f"Network error: {str(e)}")
        except Exception as e:
            raise NotificationClientError(f"Unexpected error: {str(e)}")
    
    async def publish_panic_alert(
        self,
        tourist_id: str,
        name: str,
        location: Dict[str, Any],
        message: str,
        panic_id: Optional[str] = None,
        ledger_proof_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        **Convenience method** - Publish a PANIC_ALERT event
        
        This is the most critical use case for Auth & Location services.
        
        Args:
            tourist_id: UUID of the tourist in distress
            name: Tourist's full name
            location: Location data with latitude, longitude, timestamp
            message: Alert message or description
            panic_id: Optional panic event UUID
            ledger_proof_hash: Optional immutable proof from ledger
            
        Returns:
            Dictionary with success status and event_id
            
        Example:
            result = await client.publish_panic_alert(
                tourist_id="123e4567-e89b-12d3-a456-426614174000",
                name="Alice Johnson",
                location={
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "timestamp": "2025-09-15T14:30:00Z"
                },
                message="Emergency panic button activated",
                panic_id="panic_789e0123-e89b-12d3-a456-426614174000",
                ledger_proof_hash="a1b2c3d4e5f6..."
            )
            event_id = result["event_id"]  # Store for tracking
        """
        try:
            payload = {
                "tourist_id": tourist_id,
                "name": name,
                "location": location,
                "message": message
            }
            
            # Add optional fields if provided
            if panic_id:
                payload["panic_id"] = panic_id
            if ledger_proof_hash:
                payload["ledger_proof_hash"] = ledger_proof_hash
            
            response = await self.client.post(
                f"{self.base_url}/panic-alert",
                json=payload,
                params={"api_key": self.api_key} if self.api_key else {}
            )
            
            if response.status_code == 202:
                return response.json()
            else:
                raise NotificationClientError(
                    f"HTTP {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
                
        except httpx.RequestError as e:
            raise NotificationClientError(f"Network error: {str(e)}")
        except Exception as e:
            raise NotificationClientError(f"Unexpected error: {str(e)}")


class NotificationClientError(Exception):
    """Exception raised by NotificationClient operations"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Synchronous wrapper for compatibility
class SyncNotificationClient:
    """
    Synchronous wrapper for NotificationClient
    
    Use this if your code is not async/await compatible.
    """
    
    def __init__(self, **kwargs):
        self._async_client = NotificationClient(**kwargs)
    
    def publish_location_update(self, tourist_id: str, name: str, location: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of publish_location_update"""
        return asyncio.run(self._async_client.publish_location_update(tourist_id, name, location))
    
    def publish_panic_alert(
        self,
        tourist_id: str,
        name: str,
        location: Dict[str, Any],
        message: str,
        panic_id: Optional[str] = None,
        ledger_proof_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous version of publish_panic_alert"""
        return asyncio.run(self._async_client.publish_panic_alert(
            tourist_id, name, location, message, panic_id, ledger_proof_hash
        ))
    
    def close(self):
        """Close the underlying async client"""
        asyncio.run(self._async_client.close())


# Convenience functions for quick integration
async def publish_location_update(tourist_id: str, name: str, location: Dict[str, Any]) -> str:
    """
    **Quick Helper Function** - Publish location update and return event_id
    
    Args:
        tourist_id: UUID of the tourist
        name: Tourist's name
        location: Location data
        
    Returns:
        event_id string for tracking
    """
    async with NotificationClient() as client:
        result = await client.publish_location_update(tourist_id, name, location)
        return result["event_id"]


async def publish_panic_alert(
    tourist_id: str,
    name: str,
    location: Dict[str, Any],
    message: str,
    panic_id: Optional[str] = None,
    ledger_proof_hash: Optional[str] = None
) -> str:
    """
    **Quick Helper Function** - Publish panic alert and return event_id
    
    Args:
        tourist_id: UUID of the tourist
        name: Tourist's name
        location: Location data
        message: Alert message
        panic_id: Optional panic UUID
        ledger_proof_hash: Optional ledger proof
        
    Returns:
        event_id string for tracking
    """
    async with NotificationClient() as client:
        result = await client.publish_panic_alert(
            tourist_id, name, location, message, panic_id, ledger_proof_hash
        )
        return result["event_id"]
