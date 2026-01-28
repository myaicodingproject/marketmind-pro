# Database Configuration Guide

## Overview

MarketMind Pro now uses a **centralized database configuration system** that eliminates conflicts between different configuration files and provides a single source of truth for all database settings.

## Architecture

### Centralized Configuration (`app/core/db_config.py`)

The `DatabaseConfig` class provides:
- **Single source of truth** for database URLs
- **Automatic URL resolution** with fallback priority
- **Format conversion** between sync/async URLs
- **Validation and normalization** of database URLs

### Configuration Priority

Database URL resolution follows this priority order:

1. `DATABASE_URL` environment variable
2. `POSTGRES_URL` environment variable  
3. `DB_URL` environment variable
4. Default: `postgresql://marketmind:password@localhost:5432/marketmind_pro`
5. Fallback: `sqlite:///./marketmind.db`

## Files Updated

### Core Configuration Files
- ✅ `app/core/db_config.py` - **NEW**: Centralized database configuration
- ✅ `app/core/config.py` - Updated to use centralized config
- ✅ `app/core/database.py` - Updated to use centralized config
- ✅ `app/core/production_config.py` - Updated to use centralized config

### Migration Files
- ✅ `alembic.ini` - Updated to use dynamic configuration
- ✅ `alembic/env.py` - **NEW**: Uses centralized config
- ✅ `alembic/script.py.mako` - **NEW**: Migration template

### Environment Files
- ✅ `.env.example` - **NEW**: Standardized environment template
- ✅ `hackathon-project/.env` - Updated to use standard format

### Utility Scripts
- ✅ `validate_db_config.py` - **NEW**: Validates configuration
- ✅ `setup_database.py` - **NEW**: Sets up database with proper config

## Usage

### 1. Environment Setup

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your database settings:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 2. Validate Configuration

Run the validation script to check your configuration:
```bash
python validate_db_config.py
```

### 3. Setup Database

Initialize the database:
```bash
python setup_database.py
```

### 4. Run Migrations

Create and run migrations:
```bash
# Create a new migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Configuration Examples

### PostgreSQL (Recommended)
```bash
DATABASE_URL=postgresql://marketmind:password@localhost:5432/marketmind_pro
```

### PostgreSQL with Custom Host/Port
```bash
DATABASE_URL=postgresql://user:pass@db.example.com:5433/marketmind
```

### SQLite (Development/Testing)
```bash
DATABASE_URL=sqlite:///./data/marketmind.db
```

### Environment-Specific Settings

The system automatically detects the environment:

- **Development**: Uses `DATABASE_URL` or defaults to PostgreSQL
- **Testing**: Can override to use SQLite test database
- **Production**: Uses `DATABASE_URL` with validation

## Benefits

### ✅ Eliminated Conflicts
- No more mismatched URLs between `alembic.ini`, `config.py`, and environment files
- Single source of truth prevents configuration drift

### ✅ Flexible Configuration
- Supports multiple environment variable names
- Automatic fallback to SQLite for development
- Environment-specific overrides

### ✅ Better Error Handling
- URL validation and normalization
- Clear error messages for invalid configurations
- Connection testing utilities

### ✅ Developer Experience
- Easy validation with `validate_db_config.py`
- Automated setup with `setup_database.py`
- Clear documentation and examples

## Migration from Old System

If you have existing configurations:

1. **Check current settings**: Run `python validate_db_config.py`
2. **Update environment**: Set `DATABASE_URL` in your `.env` file
3. **Test configuration**: Run validation script again
4. **Initialize database**: Run `python setup_database.py`

## Troubleshooting

### Common Issues

**"Database connection failed"**
- Check that PostgreSQL is running
- Verify credentials in `DATABASE_URL`
- Ensure database exists

**"Alembic migrations fail"**
- Run `python validate_db_config.py` to check configuration
- Ensure `alembic/env.py` imports are working
- Check that database is accessible

**"Import errors"**
- Install required packages: `pip install psycopg2-binary asyncpg`
- Ensure Python path includes the app directory

### Getting Help

1. Run `python validate_db_config.py` for configuration status
2. Check logs for detailed error messages
3. Verify environment variables are set correctly
4. Test database connection manually

## API Reference

### DatabaseConfig Class

```python
from app.core.db_config import db_config

# Get database URLs
db_config.database_url          # Auto-detected URL
db_config.async_database_url    # Async version (asyncpg/aiosqlite)
db_config.sync_database_url     # Sync version (psycopg2/sqlite3)
db_config.get_alembic_url()     # URL for Alembic migrations

# Get connection parameters
params = db_config.get_connection_params()
```

This centralized system ensures consistent database configuration across all components of MarketMind Pro.