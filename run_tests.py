#!/usr/bin/env python
"""
Script to run all project tests.
"""

import os
import sys
import subprocess
import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests():
    """Runs all project tests."""
    print("🧪 Running Virtual Secretary project tests...")
    
    # Check if PostgreSQL is requested
    use_postgres = '--postgres' in sys.argv
    if use_postgres:
        sys.argv.remove('--postgres')
        print("🗄️ Using PostgreSQL as test database...")
        # Set environment variables for PostgreSQL
        os.environ['TEST_DB_NAME'] = 'secretaria_virtual_test'
        # Use main settings for PostgreSQL tests
        os.environ['DJANGO_SETTINGS_MODULE'] = 'secretariaVirtual.settings'
    else:
        # Use SQLite for faster tests
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secretariaVirtual.test_settings')
    
    django.setup()
    
    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # List of apps to test
    test_apps = [
        'apps.empresas',
        'apps.autenticacao', 
        'apps.agendamentos',
        'apps.pagamentos',
        'apps.notificacoes',
        'apps.feature_flags'
    ]
    
    failures = test_runner.run_tests(test_apps)
    
    if failures:
        print(f"❌ {failures} test(s) failed")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)


def run_tests_with_coverage():
    """Runs tests with code coverage."""
    print("🧪 Running tests with code coverage...")
    
    try:
        # Install coverage if not installed
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], check=True)
        
        # Run tests with coverage
        cmd = [
            sys.executable, '-m', 'coverage', 'run', '--source=.', 
            'manage.py', 'test', '--settings=secretariaVirtual.test_settings'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
        
        # Generate coverage report
        subprocess.run([sys.executable, '-m', 'coverage', 'report'], check=True)
        subprocess.run([sys.executable, '-m', 'coverage', 'html'], check=True)
        
        print("✅ Tests executed successfully!")
        print("📊 Coverage report generated in htmlcov/index.html")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_specific_tests(test_pattern):
    """Runs specific tests based on a pattern."""
    print(f"🧪 Running tests that match pattern: {test_pattern}")
    
    cmd = [
        sys.executable, 'manage.py', 'test', 
        '--settings=secretariaVirtual.test_settings',
        '--pattern', test_pattern
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    """Main script function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'coverage':
            success = run_tests_with_coverage()
            sys.exit(0 if success else 1)
        
        elif command == 'pattern' and len(sys.argv) > 2:
            pattern = sys.argv[2]
            success = run_specific_tests(pattern)
            sys.exit(0 if success else 1)
        
        elif command == 'postgres':
            # Run tests with PostgreSQL
            run_tests()
        
        else:
            print("Usage: python run_tests.py [coverage|pattern <pattern>|postgres]")
            sys.exit(1)
    
    else:
        # Run all tests
        run_tests()


if __name__ == '__main__':
    main()
