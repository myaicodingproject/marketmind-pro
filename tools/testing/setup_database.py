#!/usr/bin/env python3
"""
Database Setup Script
Sets up the database with proper configuration
"""

import sys
import os
import asyncio
from urllib.parse import urlparse

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def setup_database():
    """Setup database with centralized configuration"""
    
    print("=== MarketMind Pro Database Setup ===\n")
    
    try:
        from app.core.db_config import db_config
        from app.core.database import init_db, engine
        
        print(f"📊 Using database: {db_config.database_url}")
        
        # Initialize database
        print("🔧 Initializing database...")
        await init_db()
        
        print("✅ Database setup completed successfully!")
        
        # Close engine
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    return True

def run_alembic_migrations():
    """Run Alembic migrations"""
    print("\n🔄 Running database migrations...")
    
    try:
        import subprocess
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠️  Alembic not found. Install with: pip install alembic")
        return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("Starting database setup...\n")
    
    # Run async database setup
    success = asyncio.run(setup_database())
    
    if success:
        # Run migrations
        run_alembic_migrations()
    
    print("\n=== Setup Complete ===")

if __name__ == "__main__":
    main()