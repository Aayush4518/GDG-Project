"""
Test script for the tourist registration endpoint

This script demonstrates and tests the tourist registration API functionality
to ensure it works correctly with the database and ledger integration.
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone


async def test_registration_endpoint():
    """
    Test the tourist registration endpoint with sample data
    """
    # API base URL
    base_url = "http://localhost:8000"
    
    # Sample tourist registration data
    test_tourist = {
        "name": "Alice Johnson",
        "kyc_hash": "kyc_abc123def456_test",
        "emergency_contact": {
            "name": "John Johnson",
            "phone": "+1234567890",
            "email": "emergency@example.com"
        },
        "trip_end_date": "2025-09-22T18:00:00Z"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("🔍 Testing health check...")
            health_response = await client.get(f"{base_url}/health")
            print(f"Health check status: {health_response.status_code}")
            
            # Test 2: Tourist registration
            print("\n📝 Testing tourist registration...")
            registration_response = await client.post(
                f"{base_url}/api/v1/auth/register",
                json=test_tourist
            )
            
            print(f"Registration status code: {registration_response.status_code}")
            
            if registration_response.status_code == 201:
                response_data = registration_response.json()
                print("✅ Registration successful!")
                print(f"Tourist ID: {response_data['tourist_id']}")
                print(f"Name: {response_data['name']}")
                print(f"Message: {response_data['message']}")
                print(f"Ledger Block ID: {response_data['ledger_entry']['block_id']}")
                print(f"Ledger Hash: {response_data['ledger_entry']['hash'][:16]}...")
                
                # Test 3: Retrieve tourist info
                tourist_id = response_data['tourist_id']
                print(f"\n🔍 Testing tourist info retrieval for ID: {tourist_id}")
                
                info_response = await client.get(
                    f"{base_url}/api/v1/auth/tourist/{tourist_id}"
                )
                
                if info_response.status_code == 200:
                    info_data = info_response.json()
                    print("✅ Tourist info retrieval successful!")
                    print(f"Retrieved name: {info_data['name']}")
                    print(f"Status: {info_data['status']}")
                else:
                    print(f"❌ Tourist info retrieval failed: {info_response.status_code}")
                    print(info_response.text)
                
                # Test 4: Test duplicate registration (should fail)
                print("\n🔁 Testing duplicate registration (should fail)...")
                duplicate_response = await client.post(
                    f"{base_url}/api/v1/auth/register",
                    json=test_tourist
                )
                
                if duplicate_response.status_code == 400:
                    print("✅ Duplicate registration correctly rejected!")
                    print(f"Error message: {duplicate_response.json()['detail']}")
                else:
                    print(f"❌ Duplicate registration not handled correctly: {duplicate_response.status_code}")
                
            else:
                print("❌ Registration failed!")
                print(f"Status: {registration_response.status_code}")
                print(f"Response: {registration_response.text}")
                
        except httpx.ConnectError:
            print("❌ Could not connect to the API server.")
            print("Make sure the FastAPI server is running on http://localhost:8000")
            print("Run: python main.py")
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")


if __name__ == "__main__":
    print("🧪 Smart Tourist Registration API Test")
    print("=" * 50)
    asyncio.run(test_registration_endpoint())
