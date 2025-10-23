#!/usr/bin/env python
"""
Script to run tests with PostgreSQL database.
"""

import os
import sys
import subprocess
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secretariaVirtual.test_settings')
    django.setup()

def run_tests():
    """Run tests with PostgreSQL."""
    
    # Set environment variables for test database
    os.environ['TEST_DB_NAME'] = 'secretaria_virtual_test'
    
    # Run tests
    test_args = [
        'python', '-m', 'pytest',
        '--tb=short',
        '--disable-warnings',
        '--reuse-db',
        'apps/'
    ]
    
    # Add specific test markers if provided
    if len(sys.argv) > 1:
        test_args.extend(sys.argv[1:])
    
    try:
        result = subprocess.run(test_args, check=True)
        print("Tests completed successfully!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with exit code: {e.returncode}")
        return e.returncode

if __name__ == '__main__':
    setup_django()
    exit_code = run_tests()
    sys.exit(exit_code)
