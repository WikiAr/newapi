#!/usr/bin/env python3
"""
Test runner for all z_te_sts/*.py files
Usage: python3 core8/pwb.py newapi_bot/z_te_sts/test_runner
"""

import io
from contextlib import redirect_stdout
import sys
import os
import importlib.util
import traceback
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_test_file(file_path):
    """Run a single test file"""
    try:
        print(f"\n{'='*60}")
        print(f"Running: {file_path.name}")
        print(f"{'='*60}")

        # Load the module
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)

        # Capture stdout

        f = io.StringIO()
        with redirect_stdout(f):
            spec.loader.exec_module(module)

        output = f.getvalue()
        if output:
            print("Output:")
            print(output)

        print(f"✓ {file_path.name} completed successfully")
        return True

    except Exception as e:
        print(f"✗ {file_path.name} failed: {e}")
        print(traceback.format_exc())
        return False


def main():
    """Run all test files"""
    # Get directory of this script
    test_dir = Path(__file__).parent

    # Find all test files
    test_files = []
    for file_path in test_dir.glob("test_*.py"):
        if file_path.name != "test_runner.py":  # Skip this file
            test_files.append(file_path)

    if not test_files:
        print("No test files found in x_tests directory")
        return

    # Sort files for consistent execution
    test_files.sort()

    print(f"Found {len(test_files)} test files:")
    for file_path in test_files:
        print(f"  - {file_path.name}")

    print("\nStarting test execution...")

    # Run all tests
    passed = 0
    failed = 0

    for file_path in test_files:
        if run_test_file(file_path):
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    print(f"Total tests: {len(test_files)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print(f"\n❌ {failed} test(s) failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
