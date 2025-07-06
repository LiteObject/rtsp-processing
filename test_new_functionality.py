#!/usr/bin/env python3
"""
Quick test to validate the new --with-ui functionality.
This will simulate the argument parsing without actually running the services.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_argument_parsing():
    """Test the new argument parsing options."""
    import argparse

    parser = argparse.ArgumentParser(description='RTSP Processing System')
    parser.add_argument('--ui', action='store_true',
                        help='Launch with Streamlit GUI only (no background processing)')
    parser.add_argument('--with-ui', action='store_true',
                        help='Launch background processing WITH Streamlit GUI')

    # Test different argument combinations
    test_cases = [
        [],  # No arguments
        ['--ui'],  # UI only
        ['--with-ui'],  # Background + UI
    ]

    print("Testing new argument parsing:")
    print("=" * 50)

    for args in test_cases:
        parsed = parser.parse_args(args)
        print(f"Args: {args if args else '[no arguments]'}")
        print(f"  ui: {parsed.ui}")
        print(f"  with_ui: {parsed.with_ui}")

        if parsed.with_ui:
            print("  → Would run: Background processing + UI")
        elif parsed.ui:
            print("  → Would run: UI only")
        else:
            print("  → Would run: Background processing only")
        print("-" * 30)


if __name__ == "__main__":
    test_argument_parsing()

    print("\n🎉 New usage options:")
    print("1. python -m src.app              # Background processing only")
    print("2. python -m src.app --ui         # UI only")
    print("3. python -m src.app --with-ui    # Background + UI (NEW!)")
