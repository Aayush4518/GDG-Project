from collections import defaultdict
from fastapi import WebSocket
from typing import Dict, List, Set


class ConnectionManager:
    """
    Manages WebSocket connections for real-time broadcasting to dashboard clients
    """
    
    def __init__(self):
        """
        Initialize the connection manager with an empty list of active connections
        """
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
    
    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection and add it to active connections
        
        Args:
            websocket: The WebSocket connection to accept and manage
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    async def connect_user(self, user_id: str, websocket: WebSocket):
        """
        Accept a user-specific websocket connection.

        Args:
            user_id: User/tourist UUID
            websocket: The WebSocket connection to accept and manage
        """
        await websocket.accept()
        self.user_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active connections
        
        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        for user_id, connections in list(self.user_connections.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.user_connections[user_id]
    
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

    async def broadcast_user(self, user_id: str, data: dict):
        """
        Broadcast JSON data to all active websocket connections of a specific user.

        Args:
            user_id: User/tourist UUID
            data: Dictionary payload to send
        """
        connections_to_broadcast = list(self.user_connections.get(user_id, set()))

        for connection in connections_to_broadcast:
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)
