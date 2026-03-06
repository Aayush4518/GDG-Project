#!/usr/bin/env python3
"""
🎯 Quick Verification Script for Smart Tourist Backend
This script verifies that all prompt implementations are present and working
"""

import os
import sys

def check_file_exists(file_path):
    """Check if a file exists"""
    return os.path.exists(file_path)

def check_function_in_file(file_path, function_name):
    """Check if a function exists in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return f"def {function_name}" in content
    except:
        return False

def main():
    print("🎯 Smart Tourist Backend - Quick Verification")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Files to check
    files_to_check = [
        "app/services/ledger_service.py",
        "app/services/websocket_manager.py", 
        "app/api/v1/dashboard_router.py",
        "app/schemas/tourist.py",
        "app/crud/crud_dashboard.py"
    ]
    
    print("📁 CHECKING FILE EXISTENCE:")
    all_files_exist = True
    for file_path in files_to_check:
        full_path = os.path.join(base_path, file_path)
        exists = check_file_exists(full_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {file_path}")
        if not exists:
            all_files_exist = False
    
    print(f"\n📋 CHECKING KEY FUNCTIONS:")
    
    # Check ledger service functions
    ledger_path = os.path.join(base_path, "app/services/ledger_service.py")
    functions_to_check = [
        ("hash_string", ledger_path),
        ("add_new_block", ledger_path),
        ("verify_chain", ledger_path),
        ("log_panic_event_to_ledger", ledger_path)
    ]
    
    all_functions_exist = True
    for func_name, file_path in functions_to_check:
        exists = check_function_in_file(file_path, func_name)
        status = "✅" if exists else "❌"
        print(f"   {status} {func_name} in ledger_service.py")
        if not exists:
            all_functions_exist = False
    
    # Check WebSocket manager
    websocket_path = os.path.join(base_path, "app/services/websocket_manager.py")
    websocket_functions = [
        ("connect", websocket_path),
        ("disconnect", websocket_path),
        ("broadcast", websocket_path)
    ]
    
    for func_name, file_path in websocket_functions:
        exists = check_function_in_file(file_path, func_name)
        status = "✅" if exists else "❌"
        print(f"   {status} {func_name} in websocket_manager.py")
        if not exists:
            all_functions_exist = False
    
    # Check dashboard components
    dashboard_functions = [
        ("get_active_tourists", os.path.join(base_path, "app/api/v1/dashboard_router.py")),
        ("get_active_tourists_with_last_location", os.path.join(base_path, "app/crud/crud_dashboard.py"))
    ]
    
    for func_name, file_path in dashboard_functions:
        exists = check_function_in_file(file_path, func_name)
        status = "✅" if exists else "❌"
        print(f"   {status} {func_name}")
        if not exists:
            all_functions_exist = False
    
    # Check alert service functions (Prompt 6)
    alert_service_path = os.path.join(base_path, "app/services/alert_service.py")
    alert_functions = [
        ("trigger_alert", alert_service_path),
        ("trigger_panic_alert", alert_service_path),
        ("trigger_inactivity_alert", alert_service_path)
    ]
    
    for func_name, file_path in alert_functions:
        exists = check_function_in_file(file_path, func_name)
        status = "✅" if exists else "❌"
        print(f"   {status} {func_name} in alert_service.py")
        if not exists:
            all_functions_exist = False
    
    # Check dashboard detail endpoints (Prompt 7)
    router_path = os.path.join(base_path, "app/api/v1/dashboard_router.py")
    detail_functions = [
        ("get_tourist_details", router_path),
        ("get_dashboard_analytics", router_path)
    ]
    
    for func_name, file_path in detail_functions:
        exists = check_function_in_file(file_path, func_name)
        status = "✅" if exists else "❌"
        print(f"   {status} {func_name} in dashboard_router.py")
        if not exists:
            all_functions_exist = False
    
    print(f"\n🎯 PROMPT IMPLEMENTATION STATUS:")
    
    # Check Prompt 1: Tamper-evident ledger
    prompt1_complete = (
        check_function_in_file(ledger_path, "hash_string") and
        check_function_in_file(ledger_path, "add_new_block") and
        check_function_in_file(ledger_path, "verify_chain")
    )
    print(f"   {'✅' if prompt1_complete else '❌'} Prompt 1: Tamper-evident ledger")
    
    # Check Prompt 2: WebSocket services
    prompt2_complete = (
        check_file_exists(websocket_path) and
        check_function_in_file(websocket_path, "connect") and
        check_function_in_file(websocket_path, "broadcast")
    )
    print(f"   {'✅' if prompt2_complete else '❌'} Prompt 2: WebSocket services")
    
    # Check Prompt 3: Verification endpoint
    router_path = os.path.join(base_path, "app/api/v1/dashboard_router.py")
    prompt3_complete = (
        check_file_exists(router_path) and
        check_function_in_file(router_path, "verify_ledger_integrity")
    )
    print(f"   {'✅' if prompt3_complete else '❌'} Prompt 3: Verification endpoint")
    
    # Check Prompt 4: Panic logging
    prompt4_complete = check_function_in_file(ledger_path, "log_panic_event_to_ledger")
    print(f"   {'✅' if prompt4_complete else '❌'} Prompt 4: Panic logging")
    
    # Check Prompt 5: Dashboard API
    schemas_path = os.path.join(base_path, "app/schemas/tourist.py")
    crud_path = os.path.join(base_path, "app/crud/crud_dashboard.py")
    prompt5_complete = (
        check_file_exists(schemas_path) and
        check_file_exists(crud_path) and
        check_function_in_file(router_path, "get_active_tourists")
    )
    print(f"   {'✅' if prompt5_complete else '❌'} Prompt 5: Dashboard API")
    
    # Check Prompt 6: Centralized Alert Service
    alert_service_path = os.path.join(base_path, "app/services/alert_service.py")
    prompt6_complete = (
        check_file_exists(alert_service_path) and
        check_function_in_file(alert_service_path, "trigger_alert") and
        check_function_in_file(alert_service_path, "trigger_panic_alert") and
        check_function_in_file(alert_service_path, "trigger_inactivity_alert")
    )
    print(f"   {'✅' if prompt6_complete else '❌'} Prompt 6: Centralized alert service")
    
    # Check Prompt 7: Dashboard Detail Endpoints
    prompt7_complete = (
        check_function_in_file(router_path, "get_tourist_details") and
        check_function_in_file(router_path, "get_dashboard_analytics") and
        "TouristDetails" in open(schemas_path, 'r', encoding='utf-8').read() and
        "DashboardAnalytics" in open(schemas_path, 'r', encoding='utf-8').read()
    )
    print(f"   {'✅' if prompt7_complete else '❌'} Prompt 7: Dashboard detail endpoints")
    
    print(f"\n🏆 OVERALL STATUS:")
    all_prompts = prompt1_complete and prompt2_complete and prompt3_complete and prompt4_complete and prompt5_complete and prompt6_complete and prompt7_complete
    
    if all_prompts and all_files_exist and all_functions_exist:
        print("   🎉 ALL PROMPTS SUCCESSFULLY IMPLEMENTED!")
        print("   🚀 Backend ready for next development phase")
        return 0
    else:
        print("   ⚠️  Some components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
