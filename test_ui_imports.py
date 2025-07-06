#!/usr/bin/env python3
"""
Test script to verify UI dashboard imports work correctly.
This tests the import fix without requiring Streamlit to be installed.
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_ui_imports():
    """Test that UI dashboard imports work correctly."""
    try:
        # Mock streamlit to avoid import error
        from unittest.mock import Mock
        sys.modules['streamlit'] = Mock()

        # Test the import
        from src.ui_dashboard import broadcaster
        print("✅ UI dashboard imports working correctly!")
        print(f"✅ Successfully imported broadcaster: {type(broadcaster)}")

        # Test the main function exists
        from src.ui_dashboard import main  # noqa: F401
        print("✅ Main dashboard function imported successfully!")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    print("Testing UI dashboard imports...")
    success = test_ui_imports()

    if success:
        print("\n🎉 All UI import tests passed!")
        print("\nThe ImportError with relative imports has been fixed.")
        print("You can now run the UI dashboard using:")
        print("  1. python -m src.app --ui")
        print("  2. streamlit run src/ui_dashboard.py")
        print("  3. streamlit run run_ui.py")
    else:
        print("\n❌ UI import tests failed!")
        sys.exit(1)
