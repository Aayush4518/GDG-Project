"""
Quick test for anomaly service imports
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 Testing Anomaly Service Imports")

try:
    from app.services.anomaly_service import get_anomaly_detection_status
    print("✅ Successfully imported get_anomaly_detection_status")
    
    status = get_anomaly_detection_status()
    print(f"✅ Status function working: {status['service']}")
    print(f"📊 Configuration: {status['configuration']}")
    print(f"🎯 Features: {len(status['features'])} features available")
    
except Exception as e:
    print(f"❌ Import failed: {e}")

try:
    from app.services import anomaly_service
    print("✅ Successfully imported anomaly_service module")
    
    functions = [
        'check_inactivity',
        'check_route_deviation', 
        'check_high_risk_zone',
        'run_single_tourist_check',
        'run_anomaly_checks_periodically'
    ]
    
    for func in functions:
        if hasattr(anomaly_service, func):
            print(f"✅ Function available: {func}")
        else:
            print(f"❌ Function missing: {func}")
            
except Exception as e:
    print(f"❌ Module import failed: {e}")

print("\n🎯 Anomaly service imports completed!")
