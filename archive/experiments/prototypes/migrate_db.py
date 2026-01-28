#!/usr/bin/env python3
"""
Database migration script for MarketMind Pro
Run this script to set up the database schema
"""

import asyncio
import asyncpg
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/marketmind_pro")

async def create_tables():
    """Create all necessary database tables"""
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Creating database tables...")
        
        # Enable UUID extension
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        
        # Users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reports table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                ticker VARCHAR(10) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'queued',
                progress INTEGER DEFAULT 0,
                sections TEXT[] DEFAULT ARRAY['all'],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                file_path TEXT,
                error_message TEXT,
                metadata JSONB DEFAULT '{}'
            )
        ''')
        
        # Companies table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                ticker VARCHAR(10) PRIMARY KEY,
                name VARCHAR(255),
                sector VARCHAR(100),
                industry VARCHAR(100),
                market_cap BIGINT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data JSONB DEFAULT '{}'
            )
        ''')
        
        # Create indexes
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_reports_ticker ON reports(ticker)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_companies_market_cap ON companies(market_cap)')
        
        # Create updated_at trigger function
        await conn.execute('''
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        ''')
        
        # Create trigger for users table
        await conn.execute('''
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
            CREATE TRIGGER update_users_updated_at
                BEFORE UPDATE ON users
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        ''')
        
        print("✅ Database tables created successfully!")
        
        # Insert sample data (optional)
        await insert_sample_data(conn)
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await conn.close()

async def insert_sample_data(conn):
    """Insert sample data for testing"""
    try:
        print("Inserting sample data...")
        
        # Check if sample user exists
        existing_user = await conn.fetchrow("SELECT id FROM users WHERE email = 'demo@marketmind.com'")
        
        if not existing_user:
            # Insert sample user (password: "demo123456")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash("demo123456")
            
            await conn.execute(
                """INSERT INTO users (email, hashed_password, full_name) 
                   VALUES ($1, $2, $3)""",
                "demo@marketmind.com", hashed_password, "Demo User"
            )
            print("✅ Sample user created: demo@marketmind.com / demo123456")
        
        # Insert sample companies
        sample_companies = [
            ("AAPL", "Apple Inc.", "Technology", "Consumer Electronics", 3000000000000),
            ("MSFT", "Microsoft Corporation", "Technology", "Software", 2800000000000),
            ("GOOGL", "Alphabet Inc.", "Technology", "Internet Content & Information", 1700000000000),
            ("AMZN", "Amazon.com Inc.", "Consumer Discretionary", "Internet Retail", 1500000000000),
            ("TSLA", "Tesla Inc.", "Consumer Discretionary", "Auto Manufacturers", 800000000000)
        ]
        
        for ticker, name, sector, industry, market_cap in sample_companies:
            await conn.execute(
                """INSERT INTO companies (ticker, name, sector, industry, market_cap) 
                   VALUES ($1, $2, $3, $4, $5)
                   ON CONFLICT (ticker) DO NOTHING""",
                ticker, name, sector, industry, market_cap
            )
        
        print("✅ Sample companies inserted!")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not insert sample data: {e}")

async def main():
    """Main migration function"""
    print("🚀 Starting MarketMind Pro database migration...")
    print(f"Database URL: {DATABASE_URL}")
    
    try:
        await create_tables()
        print("🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Start the application with: python main_production.py")
        print("3. Access the API at: http://localhost:8000")
        print("4. View API docs at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())