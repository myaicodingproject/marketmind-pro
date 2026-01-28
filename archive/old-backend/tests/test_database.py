#!/usr/bin/env python3
"""
Test database connection directly
"""
import asyncio
import asyncpg
import os

async def test_db_connection():
    connection_string = "postgresql://postgres:postgres@localhost:5432/marketmind"
    
    print(f"Testing connection: {connection_string}")
    
    try:
        # Test basic connection
        conn = await asyncpg.connect(connection_string)
        print("✅ Basic connection successful")
        
        # Test query
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Query test: {result}")
        
        # Test tables
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print(f"✅ Tables found: {[t['table_name'] for t in tables]}")
        
        await conn.close()
        
        # Test connection pool
        print("\nTesting connection pool...")
        pool = await asyncpg.create_pool(connection_string)
        print("✅ Connection pool created")
        
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 2")
            print(f"✅ Pool query test: {result}")
        
        await pool.close()
        print("✅ All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_db_connection())
