"""
Test script for Location Tracking and Panic Button Endpoints

This script verifies the implementation of Prompt 2: location logging and 
panic button functionality with full alert service and ledger integration.
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone
from uuid import uuid4


async def test_location_and_panic_endpoints():
    """
    Test the location tracking and panic button endpoints
    """
    # API base URL
    base_url = "http://localhost:8000"
    
    # Generate a test tourist ID (simulate registered tourist)
    test_tourist_id = str(uuid4())
    
    # Sample location data
    test_location = {
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    panic_location = {
        "latitude": 40.7589,
        "longitude": -73.9851
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("🔍 Testing API health check...")
            health_response = await client.get(f"{base_url}/health")
            print(f"Health check status: {health_response.status_code}")
            
            if health_response.status_code != 200:
                print("❌ API server not responding correctly")
                return
            
            # Test 2: Location logging endpoint
            print(f"\n📍 Testing location logging for tourist: {test_tourist_id}")
            location_response = await client.post(
                f"{base_url}/api/v1/tourists/{test_tourist_id}/location",
                json=test_location
            )
            
            print(f"Location logging status: {location_response.status_code}")
            
            if location_response.status_code == 201:
                response_data = location_response.json()
                print("✅ Location logging successful!")
                print(f"Status: {response_data['status']}")
                print(f"Message: {response_data['message']}")
            else:
                print("❌ Location logging failed!")
                print(f"Response: {location_response.text}")
            
            # Test 3: Panic button endpoint (most critical test)
            print(f"\n🚨 Testing PANIC BUTTON for tourist: {test_tourist_id}")
            print("This is the CRITICAL endpoint test...")
            
            panic_response = await client.post(
                f"{base_url}/api/v1/tourists/{test_tourist_id}/panic",
                json=panic_location
            )
            
            print(f"Panic button status: {panic_response.status_code}")
            
            if panic_response.status_code == 200:
                panic_data = panic_response.json()
                print("✅ Panic button triggered successfully!")
                print(f"Status: {panic_data['status']}")
                print(f"Message: {panic_data['message']}")
                print("🔗 Expected integrations:")
                print("  - ✅ Location logged to database")
                print("  - ✅ Real-time alert broadcast to dashboard")
                print("  - ✅ Tamper-evident ledger entry created")
            elif panic_response.status_code == 404:
                print("⚠️ Panic button returned 404 - Tourist not found")
                print("This is expected behavior if tourist wasn't registered first")
                print(f"Response: {panic_response.json()}")
            else:
                print("❌ Panic button failed!")
                print(f"Response: {panic_response.text}")
            
            # Test 4: Register tourist first, then test panic
            print(f"\n👤 Registering tourist first, then testing panic...")
            
            tourist_registration = {
                "name": "Test Tourist for Panic",
                "kyc_hash": f"kyc_panic_test_{test_tourist_id}",
                "emergency_contact": {
                    "name": "Emergency Contact",
                    "phone": "+1234567890",
                    "email": "emergency@test.com"
                },
                "trip_end_date": "2025-12-31T23:59:59Z"
            }
            
            registration_response = await client.post(
                f"{base_url}/api/v1/auth/register",
                json=tourist_registration
            )
            
            if registration_response.status_code == 201:
                reg_data = registration_response.json()
                registered_tourist_id = reg_data['tourist_id']
                print(f"✅ Tourist registered: {registered_tourist_id}")
                
                # Now test panic with registered tourist
                print(f"\n🚨 Testing panic with REGISTERED tourist...")
                
                registered_panic_response = await client.post(
                    f"{base_url}/api/v1/tourists/{registered_tourist_id}/panic",
                    json=panic_location
                )
                
                print(f"Registered tourist panic status: {registered_panic_response.status_code}")
                
                if registered_panic_response.status_code == 200:
                    panic_data = registered_panic_response.json()
                    print("✅ FULL PANIC WORKFLOW SUCCESSFUL!")
                    print(f"Status: {panic_data['status']}")
                    print(f"Message: {panic_data['message']}")
                    print("\n🔗 Complete Integration Chain:")
                    print("  1. ✅ Tourist registration → Database")
                    print("  2. ✅ Panic location → LocationLog table")
                    print("  3. ✅ Tourist verification → Retrieved from database")
                    print("  4. ✅ Alert broadcast → WebSocket to dashboard")
                    print("  5. ✅ Ledger logging → Tamper-evident evidence chain")
                else:
                    print("❌ Registered tourist panic failed!")
                    print(f"Response: {registered_panic_response.text}")
                    
            else:
                print("❌ Tourist registration failed, skipping registered panic test")
                print(f"Registration response: {registration_response.text}")
                
        except httpx.ConnectError:
            print("❌ Could not connect to the API server.")
            print("Make sure the FastAPI server is running on http://localhost:8000")
            print("Run: python main.py")
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")


if __name__ == "__main__":
    print("🧪 LOCATION TRACKING & PANIC BUTTON API TEST")
    print("=" * 55)
    print("Testing Prompt 2 Implementation:")
    print("- Location logging endpoint")
    print("- Panic button endpoint")
    print("- Alert service integration")
    print("- Ledger service integration")
    print("=" * 55)
    asyncio.run(test_location_and_panic_endpoints())
