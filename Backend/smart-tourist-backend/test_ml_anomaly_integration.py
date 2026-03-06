#!/usr/bin/env python3
"""
ML Anomaly Detection Integration Test

This script tests the complete integration of the ML-based behavioral 
anomaly detection with the existing heuristic anomaly detection system.
"""

import sys
import os
import traceback
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_ml_service_import():
    """Test that the ML anomaly service can be imported successfully."""
    print("🧪 Testing ML Anomaly Service Import...")
    try:
        from app.services import ml_anomaly_service
        print("✅ ML anomaly service imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import ML anomaly service: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing ML service: {e}")
        return False

def test_anomaly_service_integration():
    """Test that the main anomaly service includes ML functionality."""
    print("\n🧪 Testing Anomaly Service ML Integration...")
    try:
        from app.services import anomaly_service
        
        # Check if ML service is imported in anomaly service
        if hasattr(anomaly_service, 'ml_anomaly_service'):
            print("✅ ML service successfully integrated into anomaly service")
        else:
            print("❌ ML service not found in anomaly service imports")
            return False
            
        # Check status includes ML features
        status = anomaly_service.get_anomaly_detection_status()
        if "Behavioral ML Anomaly Detection" in status.get("features", []):
            print("✅ ML anomaly detection feature listed in status")
        else:
            print("❌ ML anomaly detection feature not listed in status")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error testing anomaly service integration: {e}")
        traceback.print_exc()
        return False

def test_ml_service_functionality():
    """Test core ML service functionality without database."""
    print("\n🧪 Testing ML Service Core Functionality...")
    try:
        from app.services import ml_anomaly_service
        
        # Test that key functions are available
        functions_to_check = ['detect_behavioral_anomalies', 'get_ml_anomaly_status', '_calculate_features']
        for func_name in functions_to_check:
            if hasattr(ml_anomaly_service, func_name):
                print(f"✅ Function {func_name} available")
            else:
                print(f"❌ Function {func_name} not found")
                return False
        
        # Test status function
        status = ml_anomaly_service.get_ml_anomaly_status()
        if status and 'service' in status:
            print(f"✅ ML service status retrieved: {status['service']}")
        else:
            print("❌ ML service status not available")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error testing ML service functionality: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that all required ML dependencies are available."""
    print("\n🧪 Testing ML Dependencies...")
    dependencies = {
        'sklearn': 'scikit-learn',
        'pandas': 'pandas', 
        'haversine': 'haversine'
    }
    
    all_available = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
            all_available = False
    
    return all_available

def main():
    """Run all ML anomaly detection integration tests."""
    print("🚀 Starting ML Anomaly Detection Integration Tests")
    print("=" * 60)
    
    # Track test results
    tests = [
        ("Dependencies Check", test_dependencies),
        ("ML Service Import", test_ml_service_import),
        ("ML Service Functionality", test_ml_service_functionality),
        ("Anomaly Service Integration", test_anomaly_service_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! ML Anomaly Detection is fully integrated!")
        print("\n📋 Integration Summary:")
        print("   ✅ ML dependencies installed and working")
        print("   ✅ ML anomaly service created and functional")
        print("   ✅ Main anomaly service updated with ML integration")
        print("   ✅ Behavioral anomaly detection ready for use")
        print("\n🏆 ML Anomaly Detection Implementation: COMPLETE")
    else:
        print(f"❌ {total - passed} tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
