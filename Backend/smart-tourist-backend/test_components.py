"""
Test script to verify the tamper-evident ledger functionality
"""
import asyncio
import json
from datetime import datetime
from app.services.ledger_service import hash_string, add_new_block, verify_chain
from app.services.websocket_manager import ConnectionManager


def test_hash_function():
    """Test the hash_string function"""
    test_string = "Hello, World!"
    expected_hash = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    actual_hash = hash_string(test_string)
    
    print(f"Testing hash function:")
    print(f"Input: {test_string}")
    print(f"Expected: {expected_hash}")
    print(f"Actual: {actual_hash}")
    print(f"Match: {expected_hash == actual_hash}\n")


async def test_websocket_manager():
    """Test the WebSocket connection manager"""
    print("Testing WebSocket ConnectionManager:")
    
    manager = ConnectionManager()
    
    # Test initial state
    print(f"Initial connections: {len(manager.active_connections)}")
    
    # Test broadcast to empty list (should not crash)
    test_data = {"event_type": "TEST", "message": "Hello World"}
    await manager.broadcast(test_data)
    print("Broadcast to empty connections list: Success")
    
    print("WebSocket manager test completed\n")


def main():
    """Main test function"""
    print("=" * 50)
    print("SMART TOURIST BACKEND - COMPONENT TESTS")
    print("=" * 50)
    
    # Test hash function
    test_hash_function()
    
    # Test WebSocket manager
    asyncio.run(test_websocket_manager())
    
    print("Note: Database-dependent tests (ledger functions) require a running PostgreSQL instance.")
    print("Use 'docker-compose up db' to start the database and then run the full application.")
    
    print("=" * 50)
    print("COMPONENT TESTS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()
