#!/usr/bin/env python3

"""
Test script to debug the analytics endpoint issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db
from app.crud import crud_dashboard

def test_analytics():
    print("Testing analytics CRUD function...")
    
    try:
        # Get database session
        db = next(get_db())
        print("✅ Database connection successful")
        
        # Test the analytics function
        result = crud_dashboard.get_tourists_count_by_status(db)
        print(f"✅ Analytics result: {result}")
        
        # Test active tourists function
        tourists = crud_dashboard.get_active_tourists_with_last_location(db)
        print(f"✅ Active tourists count: {len(tourists)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = test_analytics()
    sys.exit(0 if success else 1)
