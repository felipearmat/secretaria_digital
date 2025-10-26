#!/usr/bin/env python
"""
Script to setup test database for PostgreSQL.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_test_database():
    """Create test database if it doesn't exist."""
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'database': 'postgres'  # Connect to default postgres database
    }
    
    test_db_name = os.getenv('TEST_DB_NAME', 'secretaria_virtual_test')
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (test_db_name,)
        )
        
        if cursor.fetchone():
            print(f"Test database '{test_db_name}' already exists.")
        else:
            # Create test database
            cursor.execute(f'CREATE DATABASE "{test_db_name}"')
            print(f"Test database '{test_db_name}' created successfully.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error creating test database: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_test_database()
