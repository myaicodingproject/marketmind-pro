#!/usr/bin/env python3

from app.core.database import engine
from sqlalchemy import text
import redis
from app.core.config import settings

def test_connections():
    # Test PostgreSQL
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1')).scalar()
            print(f"✅ PostgreSQL connection: {result}")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
    
    # Test Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis connection: PONG")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
    
    # Test ChromaDB
    try:
        import requests
        response = requests.get("http://localhost:8002/api/v2/version")
        if response.status_code == 200:
            print("✅ ChromaDB connection: OK")
        else:
            print(f"❌ ChromaDB connection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")

if __name__ == "__main__":
    test_connections()