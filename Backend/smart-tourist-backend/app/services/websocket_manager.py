from fastapi import WebSocket
from typing import List


class ConnectionManager:
    """
    Manages WebSocket connections for real-time broadcasting to dashboard clients
    """
    
    def __init__(self):
        """
        Initialize the connection manager with an empty list of active connections
        """
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection and add it to active connections
        
        Args:
            websocket: The WebSocket connection to accept and manage
        """
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active connections
        
        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, data: dict):
        """
        Broadcast JSON data to all active WebSocket connections
        
        Args:
            data: Dictionary to send as JSON to all connected clients
        """
        # Create a copy of the list to avoid modification during iteration
        connections_to_broadcast = self.active_connections.copy()
        
        for connection in connections_to_broadcast:
            try:
                await connection.send_json(data)
            except Exception:
                # If sending fails, remove the connection (it's likely disconnected)
                self.disconnect(connection)
