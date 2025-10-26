#!/usr/bin/env python
"""
Script to test PostgreSQL connection and configuration.
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def test_database_connection():
    """Test database connection."""
    print("🔍 Testing PostgreSQL connection...")
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secretariaVirtual.settings')
        django.setup()
        
        # Test database connection
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result:
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_database_creation():
    """Test database creation and migrations."""
    print("🔍 Testing database creation and migrations...")
    
    try:
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def test_models():
    """Test model creation and queries."""
    print("🔍 Testing model operations...")
    
    try:
        from apps.companies.models import Company
        from apps.authentication.models import User
        
        # Test model creation
        company = Company.objects.create(
            name='Test Company',
            email='test@company.com'
        )
        
        user = User.objects.create_user(
            username='testuser',
            email='test@user.com',
            company=company
        )
        
        # Test queries
        companies = Company.objects.all()
        users = User.objects.all()
        
        print(f"✅ Created {companies.count()} companies and {users.count()} users")
        
        # Cleanup
        user.delete()
        company.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Model operation error: {e}")
        return False

def test_feature_flags():
    """Test feature flags functionality."""
    print("🔍 Testing feature flags...")
    
    try:
        from apps.feature_flags.models import FeatureFlag, LocalizationConfig
        
        # Test feature flag creation
        flag = FeatureFlag.objects.create(
            name='test_flag',
            description='Test flag',
            is_active=True
        )
        
        # Test localization config
        loc = LocalizationConfig.objects.create(
            language_code='test',
            is_enabled=True
        )
        
        print("✅ Feature flags created successfully!")
        
        # Cleanup
        flag.delete()
        loc.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Feature flags error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 PostgreSQL Configuration Test")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Database Creation", test_database_creation),
        ("Model Operations", test_models),
        ("Feature Flags", test_feature_flags),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed!")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! PostgreSQL is configured correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the configuration.")
        sys.exit(1)

if __name__ == '__main__':
    main()
