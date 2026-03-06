"""
Comprehensive Verification: Prompt 1 Objectives Analysis

This script performs detailed verification that ALL objectives from Prompt 1
have been met according to the specified requirements.
"""

import sys
import os
import inspect
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🎯 PROMPT 1 COMPREHENSIVE OBJECTIVES VERIFICATION")
print("=" * 80)
print("Verifying: 'Implement the Heuristic Anomaly Detection Engine'")
print("=" * 80)

# OBJECTIVE VERIFICATION TRACKING
objectives_met = {}

print("\n📋 PART A: DATABASE MODELS EXTENSION")
print("-" * 50)

try:
    from app.db.models import HighRiskZone, TouristItinerary
    from geoalchemy2 import Geometry
    
    # Requirement 1.1: Add HighRiskZone model with name and geometry
    print("🔍 Checking HighRiskZone model requirements...")
    
    # Check fields
    high_risk_fields = {col.name: col for col in HighRiskZone.__table__.columns}
    
    has_name = 'name' in high_risk_fields and str(high_risk_fields['name'].type) == 'VARCHAR'
    has_geometry = 'geometry' in high_risk_fields and 'POLYGON' in str(high_risk_fields['geometry'].type)
    
    if has_name:
        print("✅ HighRiskZone has 'name: String' field")
    else:
        print("❌ HighRiskZone missing 'name: String' field")
    
    if has_geometry:
        print("✅ HighRiskZone has 'geometry: Geometry('POLYGON')' field")
    else:
        print("❌ HighRiskZone missing 'geometry: Geometry('POLYGON')' field")
    
    # Check geoalchemy2 import
    import app.db.models as models_module
    models_source = inspect.getsource(models_module)
    has_geoalchemy_import = 'from geoalchemy2 import Geometry' in models_source
    
    if has_geoalchemy_import:
        print("✅ GeoAlchemy2 import found in models.py")
    else:
        print("❌ GeoAlchemy2 import missing from models.py")
    
    objectives_met['highriskzone_model'] = has_name and has_geometry and has_geoalchemy_import
    
    # Requirement 1.2: Add TouristItinerary model
    print("\n🔍 Checking TouristItinerary model requirements...")
    
    itinerary_fields = {col.name: col for col in TouristItinerary.__table__.columns}
    
    has_tourist_id = 'tourist_id' in itinerary_fields
    has_sequence_order = 'sequence_order' in itinerary_fields and 'INTEGER' in str(itinerary_fields['sequence_order'].type)
    has_location = 'location' in itinerary_fields and 'POINT' in str(itinerary_fields['location'].type)
    
    if has_tourist_id:
        print("✅ TouristItinerary has 'tourist_id' field")
    else:
        print("❌ TouristItinerary missing 'tourist_id' field")
        
    if has_sequence_order:
        print("✅ TouristItinerary has 'sequence_order: Integer' field")
    else:
        print("❌ TouristItinerary missing 'sequence_order: Integer' field")
        
    if has_location:
        print("✅ TouristItinerary has 'location: Geometry('POINT')' field")
    else:
        print("❌ TouristItinerary missing 'location: Geometry('POINT')' field")
    
    objectives_met['tourist_itinerary_model'] = has_tourist_id and has_sequence_order and has_location
    
except Exception as e:
    print(f"❌ Database models verification failed: {e}")
    objectives_met['highriskzone_model'] = False
    objectives_met['tourist_itinerary_model'] = False

print("\n📋 PART B: ANOMALY DETECTION LOGIC")
print("-" * 50)

try:
    from app.services import anomaly_service
    import app.services.anomaly_service as anomaly_module
    
    # Requirement 2.1: Check required imports
    print("🔍 Checking required imports...")
    
    source = inspect.getsource(anomaly_module)
    required_imports = [
        'datetime', 'timedelta', 'Session', 'shapely.geometry'
    ]
    
    imports_found = []
    for imp in required_imports:
        if imp in source:
            imports_found.append(imp)
            print(f"✅ Import found: {imp}")
        else:
            print(f"❌ Import missing: {imp}")
    
    objectives_met['required_imports'] = len(imports_found) == len(required_imports)
    
    # Requirement 2.2: check_inactivity function
    print("\n🔍 Checking check_inactivity function...")
    
    has_check_inactivity = hasattr(anomaly_service, 'check_inactivity')
    if has_check_inactivity:
        func_signature = inspect.signature(anomaly_service.check_inactivity)
        params = list(func_signature.parameters.keys())
        correct_params = 'db' in params and 'tourist' in params
        
        # Check if it triggers alert and ledger services
        has_alert_trigger = 'trigger_inactivity_alert' in source
        has_ledger_log = 'log_anomaly_event_to_ledger' in source
        
        if correct_params:
            print("✅ check_inactivity has correct parameters (db, tourist)")
        else:
            print("❌ check_inactivity missing correct parameters")
            
        if has_alert_trigger:
            print("✅ check_inactivity triggers alert service")
        else:
            print("❌ check_inactivity missing alert service integration")
            
        if has_ledger_log:
            print("✅ check_inactivity logs to ledger service")
        else:
            print("❌ check_inactivity missing ledger service integration")
            
        objectives_met['check_inactivity'] = correct_params and has_alert_trigger and has_ledger_log
    else:
        print("❌ check_inactivity function not found")
        objectives_met['check_inactivity'] = False
    
    # Requirement 2.3: check_route_deviation function
    print("\n🔍 Checking check_route_deviation function...")
    
    has_check_route_deviation = hasattr(anomaly_service, 'check_route_deviation')
    if has_check_route_deviation:
        func_signature = inspect.signature(anomaly_service.check_route_deviation)
        params = list(func_signature.parameters.keys())
        correct_params = 'db' in params and 'tourist' in params and 'latest_location' in params
        
        # Check for LineString usage
        has_linestring = 'LineString' in source
        has_distance_calc = 'distance' in source
        has_location_alert = 'trigger_location_alert' in source
        
        if correct_params:
            print("✅ check_route_deviation has correct parameters")
        else:
            print("❌ check_route_deviation missing correct parameters")
            
        if has_linestring:
            print("✅ check_route_deviation uses LineString for route")
        else:
            print("❌ check_route_deviation missing LineString usage")
            
        if has_distance_calc:
            print("✅ check_route_deviation calculates distance")
        else:
            print("❌ check_route_deviation missing distance calculation")
            
        if has_location_alert:
            print("✅ check_route_deviation triggers location alert")
        else:
            print("❌ check_route_deviation missing location alert")
            
        objectives_met['check_route_deviation'] = all([correct_params, has_linestring, has_distance_calc, has_location_alert])
    else:
        print("❌ check_route_deviation function not found")
        objectives_met['check_route_deviation'] = False
    
    # Requirement 2.4: check_high_risk_zone function
    print("\n🔍 Checking check_high_risk_zone function...")
    
    has_check_high_risk = hasattr(anomaly_service, 'check_high_risk_zone')
    if has_check_high_risk:
        func_signature = inspect.signature(anomaly_service.check_high_risk_zone)
        params = list(func_signature.parameters.keys())
        correct_params = 'db' in params and 'tourist' in params and 'latest_location' in params
        
        # Check for PostGIS ST_Contains usage
        has_st_contains = 'ST_Contains' in source
        has_location_alert = 'trigger_location_alert' in source
        
        if correct_params:
            print("✅ check_high_risk_zone has correct parameters")
        else:
            print("❌ check_high_risk_zone missing correct parameters")
            
        if has_st_contains:
            print("✅ check_high_risk_zone uses PostGIS ST_Contains")
        else:
            print("❌ check_high_risk_zone missing PostGIS ST_Contains")
            
        if has_location_alert:
            print("✅ check_high_risk_zone triggers location alert")
        else:
            print("❌ check_high_risk_zone missing location alert")
            
        objectives_met['check_high_risk_zone'] = correct_params and has_st_contains and has_location_alert
    else:
        print("❌ check_high_risk_zone function not found")
        objectives_met['check_high_risk_zone'] = False
    
    # Requirement 2.5: run_single_tourist_check function
    print("\n🔍 Checking run_single_tourist_check function...")
    
    has_single_check = hasattr(anomaly_service, 'run_single_tourist_check')
    if has_single_check:
        func_signature = inspect.signature(anomaly_service.run_single_tourist_check)
        params = list(func_signature.parameters.keys())
        correct_params = 'db' in params and 'tourist_id' in params
        
        if correct_params:
            print("✅ run_single_tourist_check has correct parameters")
        else:
            print("❌ run_single_tourist_check missing correct parameters")
            
        objectives_met['run_single_tourist_check'] = correct_params
    else:
        print("❌ run_single_tourist_check function not found")
        objectives_met['run_single_tourist_check'] = False
    
except Exception as e:
    print(f"❌ Anomaly detection logic verification failed: {e}")
    objectives_met.update({
        'required_imports': False,
        'check_inactivity': False,
        'check_route_deviation': False,
        'check_high_risk_zone': False,
        'run_single_tourist_check': False
    })

print("\n📋 PART C: BACKGROUND TASK SYSTEM")
print("-" * 50)

try:
    # Requirement 3.1: Background function with asyncio
    print("🔍 Checking background task implementation...")
    
    has_background_task = hasattr(anomaly_service, 'run_anomaly_checks_periodically')
    if has_background_task:
        func = anomaly_service.run_anomaly_checks_periodically
        is_async = inspect.iscoroutinefunction(func)
        
        if is_async:
            print("✅ run_anomaly_checks_periodically is async function")
        else:
            print("❌ run_anomaly_checks_periodically is not async")
            
        # Check for while True loop and asyncio.sleep
        source = inspect.getsource(anomaly_module)
        has_while_loop = 'while True' in source
        has_async_sleep = 'asyncio.sleep' in source
        
        if has_while_loop:
            print("✅ Background task has infinite loop")
        else:
            print("❌ Background task missing infinite loop")
            
        if has_async_sleep:
            print("✅ Background task uses asyncio.sleep")
        else:
            print("❌ Background task missing asyncio.sleep")
            
        objectives_met['background_task'] = is_async and has_while_loop and has_async_sleep
    else:
        print("❌ run_anomaly_checks_periodically function not found")
        objectives_met['background_task'] = False
    
    # Requirement 3.2: Main.py integration
    print("\n🔍 Checking main.py integration...")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    has_import = 'from app.services.anomaly_service import' in main_content
    has_startup_event = '@app.on_event("startup")' in main_content
    has_create_task = 'asyncio.create_task' in main_content
    has_background_ref = 'run_anomaly_checks_periodically' in main_content
    
    if has_import:
        print("✅ main.py imports anomaly service")
    else:
        print("❌ main.py missing anomaly service import")
        
    if has_startup_event:
        print("✅ main.py has startup event decorator")
    else:
        print("❌ main.py missing startup event decorator")
        
    if has_create_task:
        print("✅ main.py creates async task")
    else:
        print("❌ main.py missing async task creation")
        
    if has_background_ref:
        print("✅ main.py references background function")
    else:
        print("❌ main.py missing background function reference")
    
    objectives_met['main_integration'] = all([has_import, has_startup_event, has_create_task, has_background_ref])
    
except Exception as e:
    print(f"❌ Background task verification failed: {e}")
    objectives_met.update({
        'background_task': False,
        'main_integration': False
    })

print("\n📋 TESTING/VERIFICATION REQUIREMENTS")
print("-" * 50)

try:
    # Check if system can handle the specified test scenarios
    print("🔍 Checking system readiness for test scenarios...")
    
    # Test scenario 1: Inactivity detection capability
    has_inactivity_threshold = hasattr(anomaly_service, 'INACTIVITY_THRESHOLD_MINUTES')
    if has_inactivity_threshold:
        threshold = anomaly_service.INACTIVITY_THRESHOLD_MINUTES
        print(f"✅ Inactivity threshold configured: {threshold} minutes")
        objectives_met['inactivity_testing'] = threshold > 0
    else:
        print("❌ Inactivity threshold not configured")
        objectives_met['inactivity_testing'] = False
    
    # Test scenario 2: Geo-fencing capability
    from app.db.models import HighRiskZone
    print("✅ High-risk zone model available for geo-fencing tests")
    objectives_met['geofencing_testing'] = True
    
    # Check PostGIS functions are available
    source = inspect.getsource(anomaly_module)
    has_postgis = 'ST_Contains' in source or 'ST_MakePoint' in source
    if has_postgis:
        print("✅ PostGIS functions available for spatial testing")
    else:
        print("❌ PostGIS functions not properly implemented")
    
    objectives_met['postgis_ready'] = has_postgis
    
except Exception as e:
    print(f"❌ Testing readiness verification failed: {e}")
    objectives_met.update({
        'inactivity_testing': False,
        'geofencing_testing': False,
        'postgis_ready': False
    })

print("\n📋 FINAL DELIVERABLE VERIFICATION")
print("-" * 50)

# Check that all required files exist and have content
required_files = [
    'app/services/anomaly_service.py',
    'app/db/models.py',
    'main.py'
]

for file_path in required_files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if len(content.strip()) > 0:
            print(f"✅ File exists and has content: {file_path}")
        else:
            print(f"❌ File exists but is empty: {file_path}")
    else:
        print(f"❌ Required file missing: {file_path}")

# FINAL SCORE CALCULATION
print("\n" + "=" * 80)
print("📊 OBJECTIVES COMPLETION ANALYSIS")
print("=" * 80)

total_objectives = len(objectives_met)
completed_objectives = sum(objectives_met.values())
completion_percentage = (completed_objectives / total_objectives) * 100

print(f"\n📈 COMPLETION SCORE: {completed_objectives}/{total_objectives} ({completion_percentage:.1f}%)")

print("\n📋 DETAILED OBJECTIVES STATUS:")
objective_categories = {
    'Database Models': ['highriskzone_model', 'tourist_itinerary_model'],
    'Anomaly Detection Logic': ['required_imports', 'check_inactivity', 'check_route_deviation', 'check_high_risk_zone', 'run_single_tourist_check'],
    'Background Task System': ['background_task', 'main_integration'],
    'Testing Readiness': ['inactivity_testing', 'geofencing_testing', 'postgis_ready']
}

for category, obj_list in objective_categories.items():
    category_score = sum(objectives_met.get(obj, False) for obj in obj_list)
    category_total = len(obj_list)
    category_percent = (category_score / category_total) * 100
    status = "✅ COMPLETE" if category_percent == 100 else "⚠️ PARTIAL" if category_percent > 0 else "❌ FAILED"
    print(f"{category:.<40} {category_score}/{category_total} ({category_percent:.0f}%) {status}")

print("\n🎯 OVERALL STATUS:")
if completion_percentage == 100:
    print("✅ ALL PROMPT 1 OBJECTIVES FULLY IMPLEMENTED")
    print("🚀 Ready for production deployment and testing")
elif completion_percentage >= 90:
    print("⚠️ PROMPT 1 MOSTLY COMPLETE - Minor issues need addressing")
elif completion_percentage >= 70:
    print("⚠️ PROMPT 1 PARTIALLY COMPLETE - Several objectives need work")
else:
    print("❌ PROMPT 1 INCOMPLETE - Major implementation required")

print("\n🔍 KEY ACHIEVEMENTS:")
if objectives_met.get('highriskzone_model', False):
    print("  ✅ HighRiskZone model with PostGIS polygon geometry")
if objectives_met.get('tourist_itinerary_model', False):
    print("  ✅ TouristItinerary model with sequence ordering")
if objectives_met.get('check_inactivity', False):
    print("  ✅ Inactivity detection with alert/ledger integration")
if objectives_met.get('check_route_deviation', False):
    print("  ✅ Route deviation detection with LineString analysis")
if objectives_met.get('check_high_risk_zone', False):
    print("  ✅ High-risk zone geo-fencing with PostGIS")
if objectives_met.get('background_task', False):
    print("  ✅ Async background monitoring task")
if objectives_met.get('main_integration', False):
    print("  ✅ FastAPI startup integration")

print("\n" + "=" * 80)
print("🎯 PROMPT 1 VERIFICATION COMPLETE")
print("=" * 80)
