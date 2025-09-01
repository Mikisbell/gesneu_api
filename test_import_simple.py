#!/usr/bin/env python3
"""
Test simple import of main API module
"""

try:
    from ges_neu_api.main import app
    print("✅ API imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
