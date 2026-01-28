#!/usr/bin/env python3
"""
Database Configuration Validation Script
Validates and displays current database configuration across all components
"""

import sys
import os
from urllib.parse import urlparse

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def validate_database_config():
    """Validate database configuration across all components"""
    
    print("=== MarketMind Pro Database Configuration Validation ===\n")
    
    try:
        # Import centralized config
        from app.core.db_config import db_config
        
        print("✅ Centralized Database Configuration:")
        print(f"   Database URL: {db_config.database_url}")
        print(f"   Async URL: {db_config.async_database_url}")
        print(f"   Sync URL: {db_config.sync_database_url}")
        print(f"   Alembic URL: {db_config.get_alembic_url()}")
        
        # Parse URL details
        parsed = urlparse(db_config.database_url)
        print(f"\n📊 Connection Details:")
        print(f"   Scheme: {parsed.scheme}")
        print(f"   Host: {parsed.hostname or 'N/A'}")
        print(f"   Port: {parsed.port or 'N/A'}")
        print(f"   Database: {parsed.path.lstrip('/') if parsed.path else 'N/A'}")
        print(f"   Username: {parsed.username or 'N/A'}")
        print(f"   Password: {'***' if parsed.password else 'N/A'}")
        
    except Exception as e:
        print(f"❌ Error loading centralized config: {e}")
        return False
    
    # Check environment variables
    print(f"\n🌍 Environment Variables:")
    env_vars = ['DATABASE_URL', 'POSTGRES_URL', 'DB_URL']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   {var}: {value}")
        else:
            print(f"   {var}: Not set")
    
    # Check config files
    print(f"\n📁 Configuration Files:")
    
    # Check alembic.ini
    try:
        with open('alembic.ini', 'r') as f:
            content = f.read()
            if 'Database URL will be set dynamically' in content:
                print("   ✅ alembic.ini: Uses dynamic configuration")
            elif 'sqlalchemy.url = ' in content and not content.count('sqlalchemy.url = postgresql'):
                print("   ✅ alembic.ini: Uses dynamic configuration")
            else:
                print("   ⚠️  alembic.ini: May have hardcoded URL")
    except FileNotFoundError:
        print("   ❌ alembic.ini: Not found")
    
    # Check .env files
    env_files = ['.env', '.env.example', 'hackathon-project/.env']
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   ✅ {env_file}: Found")
        else:
            print(f"   ⚠️  {env_file}: Not found")
    
    # Test database connection
    print(f"\n🔌 Database Connection Test:")
    try:
        if db_config.database_url.startswith('postgresql'):
            import psycopg2
            from psycopg2 import OperationalError
            
            params = db_config.get_connection_params()
            conn = psycopg2.connect(
                host=params['host'],
                port=params['port'],
                database=params['database'],
                user=params['username'],
                password=params['password']
            )
            conn.close()
            print("   ✅ PostgreSQL connection successful")
            
        elif db_config.database_url.startswith('sqlite'):
            import sqlite3
            params = db_config.get_connection_params()
            conn = sqlite3.connect(params['database'])
            conn.close()
            print("   ✅ SQLite connection successful")
            
    except ImportError as e:
        print(f"   ⚠️  Database driver not installed: {e}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
    
    print(f"\n=== Validation Complete ===")
    return True

if __name__ == "__main__":
    validate_database_config()