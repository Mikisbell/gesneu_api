"""
Script to test imports and module resolution.
Run this from the project root directory.
"""
import sys
from pathlib import Path

def check_imports():
    """Check that all required imports work."""
    # Add project root to Python path
    project_root = str(Path(__file__).parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print(f"Project root: {project_root}")
    print(f"Python path: {sys.path}\n")

    # Test core imports
    print("Testing core imports...")
    try:
        from core.config import settings
        from core.database import get_session
        print("✅ Core imports successful")
        print(f"  - Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
    except ImportError as e:
        print(f"❌ Core import error: {e}")
        return False

    # Test auth module imports
    print("\nTesting auth module imports...")
    try:
        from ges_neu_api.modules.auth.router import router as auth_router
        from ges_neu_api.modules.auth import schemas as auth_schemas
        print("✅ Auth module imports successful")
        print(f"  - Router prefix: {auth_router.prefix}")
    except ImportError as e:
        print(f"❌ Auth module import error: {e}")
        return False

    return True

if __name__ == "__main__":
    if check_imports():
        print("\n✅ All imports are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some imports failed. Please check the error messages above.")
        sys.exit(1)
