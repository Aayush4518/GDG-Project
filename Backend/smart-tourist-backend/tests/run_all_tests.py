"""
Master Test Runner
Executes all test suites to verify both prompt objectives are achieved
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_ledger_service import run_ledger_tests
from test_websocket_service import run_websocket_tests
from test_integration import run_integration_tests


def print_test_header():
    """Print the main test header"""
    print("\n" + "=" * 100)
    print("🚀 SMART TOURIST BACKEND - COMPREHENSIVE TEST SUITE")
    print("=" * 100)
    print(f"📅 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Objective: Verify both engineering prompt implementations")
    print("\n📋 Test Coverage:")
    print("   ✓ Prompt 1: Tamper-Evident Ledger Service")
    print("   ✓ Prompt 2: Real-Time WebSocket Alerting Service") 
    print("   ✓ Integration: End-to-End Workflows")
    print("=" * 100)


async def run_all_tests():
    """Execute all test suites"""
    
    print_test_header()
    
    try:
        # Run Prompt 1 tests (Ledger Service)
        print("\n🔗 PHASE 1: TAMPER-EVIDENT LEDGER TESTS")
        run_ledger_tests()
        
        # Run Prompt 2 tests (WebSocket Service)
        print("\n📡 PHASE 2: WEBSOCKET ALERTING TESTS")
        await run_websocket_tests()
        
        # Run Integration tests
        print("\n🔄 PHASE 3: INTEGRATION TESTS")
        await run_integration_tests()
        
        # Final summary
        print_success_summary()
        
    except Exception as e:
        print_failure_summary(e)
        sys.exit(1)


def print_success_summary():
    """Print success summary"""
    print("\n" + "🎉" * 50)
    print("🏆 COMPREHENSIVE TEST SUITE - ALL TESTS PASSED!")
    print("🎉" * 50)
    
    print("\n📊 VERIFICATION RESULTS:")
    print("=" * 60)
    
    print("\n✅ PROMPT 1 OBJECTIVES ACHIEVED:")
    print("   ✓ Hash utilities implemented and tested")
    print("   ✓ Latest block retrieval working")
    print("   ✓ New block creation with proper chaining")
    print("   ✓ Chain verification detects tampering")
    print("   ✓ Deterministic hashing verified")
    
    print("\n✅ PROMPT 2 OBJECTIVES ACHIEVED:")
    print("   ✓ ConnectionManager class implemented")
    print("   ✓ WebSocket connect/disconnect lifecycle")
    print("   ✓ Real-time broadcasting to all clients")
    print("   ✓ Error handling for failed connections")
    print("   ✓ Dashboard WebSocket endpoint ready")
    
    print("\n✅ INTEGRATION VERIFICATION:")
    print("   ✓ Tourist registration workflow")
    print("   ✓ Panic button end-to-end flow")
    print("   ✓ Location tracking with ledger+broadcast")
    print("   ✓ Data consistency across services")
    print("   ✓ Broadcast message structure verified")
    
    print("\n🚀 SYSTEM STATUS:")
    print("   ✓ Backend foundation ready for frontend integration")
    print("   ✓ Tamper-evident ledger operational")
    print("   ✓ Real-time alerting system functional")
    print("   ✓ API contracts satisfied")
    print("   ✓ Ready for Developer 2 & 3 integration")
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("   1. Start PostgreSQL database")
    print("   2. Run: uvicorn main:app --reload")
    print("   3. Test WebSocket: ws://localhost:8000/api/v1/dashboard/ws/dashboard")
    print("   4. Ready for mobile app and dashboard development!")
    print("=" * 60)


def print_failure_summary(error):
    """Print failure summary"""
    print("\n" + "❌" * 50)
    print("💥 TEST SUITE FAILED!")
    print("❌" * 50)
    print(f"\n🚨 Error Details: {str(error)}")
    print("\n📋 Troubleshooting:")
    print("   1. Check that all imports are working")
    print("   2. Verify project structure is correct")
    print("   3. Ensure Python path includes project root")
    print("   4. Review error message above for specific issue")


def run_quick_verification():
    """Run a quick verification of key components"""
    print("\n🔍 QUICK COMPONENT VERIFICATION:")
    print("-" * 50)
    
    try:
        # Test imports
        from app.services.ledger_service import hash_string, get_latest_block_hash, add_new_block, verify_chain
        print("✅ Ledger service imports successful")
        
        from app.services.websocket_manager import ConnectionManager
        print("✅ WebSocket manager imports successful")
        
        from app.api.v1.dashboard_router import router, manager
        print("✅ Dashboard router imports successful")
        
        # Test basic functionality
        test_hash = hash_string("test")
        assert len(test_hash) == 64
        print("✅ Hash function working")
        
        connection_manager = ConnectionManager()
        assert hasattr(connection_manager, 'active_connections')
        print("✅ ConnectionManager instantiation working")
        
        # Test manager instance from router
        assert hasattr(manager, 'active_connections')
        print("✅ WebSocket manager instance working")
        
        print("\n🎯 All core components verified - ready for full test suite!")
        return True
        
    except Exception as e:
        print(f"❌ Component verification failed: {e}")
        return False


if __name__ == "__main__":
    # Run quick verification first
    if run_quick_verification():
        # If basic verification passes, run full test suite
        asyncio.run(run_all_tests())
    else:
        print("\n💡 Fix component issues before running full test suite")
        sys.exit(1)
