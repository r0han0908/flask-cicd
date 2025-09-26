#!/usr/bin/env python3
"""
Test runner script for the Flask Social Media application.
"""
import pytest
import sys
import os

def run_tests():
    """Run the test suite."""
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Run pytest with coverage
    exit_code = pytest.main([
        'tests/',
        '-v',
        '--cov=app',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-fail-under=75'
    ])
    
    return exit_code

if __name__ == '__main__':
    exit_code = run_tests()
    print("\n" + "="*50)
    if exit_code == 0:
        print("🎉 All tests passed!")
        print("📊 Check htmlcov/index.html for coverage report")
    else:
        print("❌ Some tests failed")
    print("="*50)
    sys.exit(exit_code)
