"""
Test script to verify imports are working correctly.
Run this from the project root directory.
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all required imports work."""
    # Add project root to Python path
    project_root = str(Path(__file__).parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print(f"Project root: {project_root}")
    print(f"Python path: {sys.path}\n")

    # Test core imports
    print("Testing core imports...")
    try:
        from ges_neu_api.core.config import settings
        from ges_neu_api.core.database import get_session
        print("✅ Core imports successful")
        print(f"  - Environment: {settings.ENVIRONMENT}")
        return True
    except ImportError as e:
        print(f"❌ Core import error: {e}")
        return False

if __name__ == "__main__":
    if test_imports():
        print("\n✅ All imports are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some imports failed. Please check the error messages above.")
        sys.exit(1)
