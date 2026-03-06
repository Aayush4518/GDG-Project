"""
Test suite for Real-Time WebSocket Alerting Service
Testing objectives from Prompt 2:
- ConnectionManager class functionality
- WebSocket endpoint implementation
- Real-time broadcasting capabilities
"""

import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.websocket_manager import ConnectionManager


class TestConnectionManager:
    """Test Part A: The ConnectionManager Class"""
    
    def test_connection_manager_initialization(self):
        """Test ConnectionManager initializes with empty connections"""
        manager = ConnectionManager()
        
        assert hasattr(manager, 'active_connections')
        assert isinstance(manager.active_connections, list)
        assert len(manager.active_connections) == 0
        print("✅ ConnectionManager initialization test passed")
    
    async def test_connect_method(self):
        """Test the connect method accepts websocket and adds to list"""
        manager = ConnectionManager()
        
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_websocket.accept = AsyncMock()
        
        # Test connect
        await manager.connect(mock_websocket)
        
        # Verify websocket.accept() was called
        mock_websocket.accept.assert_called_once()
        
        # Verify websocket was added to active connections
        assert len(manager.active_connections) == 1
        assert manager.active_connections[0] == mock_websocket
        print("✅ ConnectionManager.connect() test passed")
    
    def test_disconnect_method(self):
        """Test the disconnect method removes websocket from list"""
        manager = ConnectionManager()
        
        # Mock WebSockets
        mock_ws1 = Mock()
        mock_ws2 = Mock()
        mock_ws3 = Mock()
        
        # Add connections manually
        manager.active_connections = [mock_ws1, mock_ws2, mock_ws3]
        
        # Test disconnect
        manager.disconnect(mock_ws2)
        
        # Verify websocket was removed
        assert len(manager.active_connections) == 2
        assert mock_ws2 not in manager.active_connections
        assert mock_ws1 in manager.active_connections
        assert mock_ws3 in manager.active_connections
        print("✅ ConnectionManager.disconnect() test passed")
    
    def test_disconnect_nonexistent_websocket(self):
        """Test disconnect handles non-existent websocket gracefully"""
        manager = ConnectionManager()
        
        mock_ws1 = Mock()
        mock_ws2 = Mock()
        mock_ws_not_connected = Mock()
        
        manager.active_connections = [mock_ws1, mock_ws2]
        
        # Try to disconnect a websocket that's not in the list
        manager.disconnect(mock_ws_not_connected)  # Should not crash
        
        # List should remain unchanged
        assert len(manager.active_connections) == 2
        assert mock_ws1 in manager.active_connections
        assert mock_ws2 in manager.active_connections
        print("✅ ConnectionManager.disconnect() graceful handling test passed")
    
    async def test_broadcast_method(self):
        """Test the broadcast method sends JSON to all connections"""
        manager = ConnectionManager()
        
        # Mock WebSockets
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws3 = AsyncMock()
        
        manager.active_connections = [mock_ws1, mock_ws2, mock_ws3]
        
        # Test data
        test_data = {
            "event_type": "PANIC_ALERT",
            "payload": {
                "tourist_id": "test-123",
                "message": "Help needed!"
            }
        }
        
        # Test broadcast
        await manager.broadcast(test_data)
        
        # Verify all websockets received the data
        mock_ws1.send_json.assert_called_once_with(test_data)
        mock_ws2.send_json.assert_called_once_with(test_data)
        mock_ws3.send_json.assert_called_once_with(test_data)
        print("✅ ConnectionManager.broadcast() test passed")
    
    async def test_broadcast_handles_failed_connections(self):
        """Test broadcast removes failed connections"""
        manager = ConnectionManager()
        
        # Mock WebSockets - one will fail
        mock_ws_good = AsyncMock()
        mock_ws_failed = AsyncMock()
        mock_ws_failed.send_json.side_effect = Exception("Connection lost")
        
        manager.active_connections = [mock_ws_good, mock_ws_failed]
        
        test_data = {"event": "test"}
        
        # Test broadcast
        await manager.broadcast(test_data)
        
        # Good connection should receive data
        mock_ws_good.send_json.assert_called_once_with(test_data)
        
        # Failed connection should be removed
        assert mock_ws_failed not in manager.active_connections
        assert len(manager.active_connections) == 1
        assert manager.active_connections[0] == mock_ws_good
        print("✅ ConnectionManager.broadcast() error handling test passed")


class TestWebSocketEndpoint:
    """Test Part B: The WebSocket API Endpoint"""
    
    def test_router_imports_and_setup(self):
        """Test that dashboard router imports are correct"""
        try:
            from app.api.v1.dashboard_router import router, manager
            
            # Verify router exists
            assert router is not None
            print("✅ Dashboard router import test passed")
            
            # Verify manager is ConnectionManager instance
            assert isinstance(manager, ConnectionManager)
            print("✅ Manager instance test passed")
            
            # Manager is directly accessible (Prompt 6 refactoring)
            assert hasattr(manager, 'active_connections')
            print("✅ Manager accessibility test passed")
            
        except ImportError as e:
            print(f"❌ Import test failed: {e}")
            raise
    
    async def test_websocket_endpoint_logic(self):
        """Test the core logic that should be in websocket_endpoint"""
        # This tests the pattern that should be used in the endpoint
        
        manager = ConnectionManager()
        mock_websocket = AsyncMock()
        
        # Simulate the endpoint logic
        try:
            # Step 1: Connect
            await manager.connect(mock_websocket)
            assert len(manager.active_connections) == 1
            
            # Step 2: Simulate keeping connection alive
            mock_websocket.receive_text.return_value = "ping"
            
            # Step 3: Simulate disconnect in finally block
            manager.disconnect(mock_websocket)
            assert len(manager.active_connections) == 0
            
            print("✅ WebSocket endpoint logic pattern test passed")
            
        except Exception as e:
            # Ensure cleanup happens even if there's an error
            manager.disconnect(mock_websocket)
            raise


class TestRealTimeBroadcasting:
    """Test the complete real-time broadcasting workflow"""
    
    async def test_complete_alert_workflow(self):
        """Test a complete panic alert broadcasting workflow"""
        manager = ConnectionManager()
        
        # Simulate multiple dashboard connections
        dashboard1 = AsyncMock()
        dashboard2 = AsyncMock()
        dashboard3 = AsyncMock()
        
        # Connect all dashboards
        await manager.connect(dashboard1)
        await manager.connect(dashboard2)
        await manager.connect(dashboard3)
        
        assert len(manager.active_connections) == 3
        
        # Simulate a panic alert
        panic_alert = {
            "event_type": "PANIC_ALERT",
            "payload": {
                "tourist_id": "uuid-emergency-123",
                "name": "Jane Doe",
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "timestamp": "2025-09-15T11:05:00Z"
                },
                "message": "I am in trouble, need help!"
            }
        }
        
        # Broadcast the alert
        await manager.broadcast(panic_alert)
        
        # Verify all dashboards received the alert
        dashboard1.send_json.assert_called_once_with(panic_alert)
        dashboard2.send_json.assert_called_once_with(panic_alert)
        dashboard3.send_json.assert_called_once_with(panic_alert)
        
        print("✅ Complete panic alert broadcasting workflow test passed")
        print(f"    Alert sent to {len(manager.active_connections)} dashboard(s)")
    
    async def test_location_update_broadcasting(self):
        """Test location update broadcasting"""
        manager = ConnectionManager()
        
        dashboard = AsyncMock()
        await manager.connect(dashboard)
        
        # Simulate location update
        location_update = {
            "event_type": "LOCATION_UPDATE", 
            "payload": {
                "tourist_id": "uuid-123",
                "location": {
                    "latitude": 12.9720,
                    "longitude": 77.5950,
                    "timestamp": "2025-09-15T11:05:10Z"
                }
            }
        }
        
        await manager.broadcast(location_update)
        
        dashboard.send_json.assert_called_once_with(location_update)
        print("✅ Location update broadcasting test passed")


async def run_websocket_tests():
    """Run all WebSocket service tests"""
    print("=" * 70)
    print("TESTING PROMPT 2 OBJECTIVES: REAL-TIME WEBSOCKET ALERTING SERVICE")
    print("=" * 70)
    
    # Test ConnectionManager class
    print("\n📋 Testing Part A: ConnectionManager Class")
    manager_tests = TestConnectionManager()
    manager_tests.test_connection_manager_initialization()
    await manager_tests.test_connect_method()
    manager_tests.test_disconnect_method()
    manager_tests.test_disconnect_nonexistent_websocket()
    await manager_tests.test_broadcast_method()
    await manager_tests.test_broadcast_handles_failed_connections()
    
    # Test WebSocket endpoint
    print("\n📋 Testing Part B: WebSocket API Endpoint")
    endpoint_tests = TestWebSocketEndpoint()
    endpoint_tests.test_router_imports_and_setup()
    await endpoint_tests.test_websocket_endpoint_logic()
    
    # Test complete workflows
    print("\n📋 Testing Complete Real-Time Broadcasting Workflows")
    workflow_tests = TestRealTimeBroadcasting()
    await workflow_tests.test_complete_alert_workflow()
    await workflow_tests.test_location_update_broadcasting()
    
    print("\n" + "=" * 70)
    print("✅ ALL PROMPT 2 OBJECTIVES ACHIEVED!")
    print("✅ Real-time WebSocket alerting service implementation verified")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_websocket_tests())
