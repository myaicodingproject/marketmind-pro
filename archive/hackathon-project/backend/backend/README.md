# MarketMind Pro Backend

AI-Powered Stock Research Platform - FastAPI Backend with Kiro CLI Integration

## 🏗️ Architecture

This backend uses **Vertical Slice Architecture** for better maintainability and feature isolation:

```
app/
├── core/                   # Core configuration
│   └── config.py          # Settings and environment variables
├── shared/                # Shared components
│   ├── database/          # Database connection and setup
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   └── utils/             # Utilities (auth, logging, exceptions, Kiro integration)
├── features/              # Feature modules (Vertical Slices)
│   ├── auth/              # Authentication feature
│   ├── reports/           # Reports feature
│   └── companies/         # Companies feature
└── main.py               # FastAPI application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (for production)
- Redis 7+ (for background tasks)
- Kiro CLI (latest version)

### Installation

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations (when database is available):**
   ```bash
   alembic upgrade head
   ```

5. **Start the server:**
   ```bash
   ./start_server.sh
   # OR
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh access token

### Reports
- `POST /api/reports/` - Create new report
- `GET /api/reports/` - Get user reports
- `GET /api/reports/{id}` - Get specific report
- `DELETE /api/reports/{id}` - Delete report
- `POST /api/reports/{id}/regenerate` - Regenerate report
- `GET /api/reports/{id}/progress` - Get generation progress

### Companies
- `GET /api/companies/` - Get all companies
- `GET /api/companies/{ticker}` - Get company by ticker
- `POST /api/companies/` - Create company
- `GET /api/companies/search/{query}` - Search companies

### System
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)

## 🔧 Key Features

### 1. Kiro CLI Integration
- **Location**: `app/shared/utils/kiro_integration.py`
- **Purpose**: 100% Kiro CLI processing for financial analysis
- **Features**:
  - Concurrent execution of multiple analysis prompts
  - Company fundamentals analysis
  - Valuation modeling (DCF, peer comparison)
  - Risk assessment
  - Executive summary generation

### 2. Authentication System
- **JWT-based authentication** with Bearer tokens
- **Password hashing** using bcrypt
- **Token refresh** mechanism
- **User management** with SQLAlchemy models

### 3. Report Generation
- **Background processing** with FastAPI BackgroundTasks
- **Real-time progress tracking**
- **Comprehensive analysis** using 12+ Kiro prompts
- **JSON content storage** with structured data

### 4. Database Models
- **User**: Authentication and user management
- **Company**: Stock ticker and company information
- **Report**: Generated analysis reports with status tracking

### 5. Error Handling & Logging
- **Comprehensive exception handling**
- **Structured logging** with file and console output
- **Custom exception types** for better error management
- **Request validation** with Pydantic

## 🧪 Testing

### Basic API Test
```bash
python simple_test.py
```

### Comprehensive API Test (requires database)
```bash
python test_api.py
```

### Manual Testing
1. Start the server: `./start_server.sh`
2. Visit: http://localhost:8000/docs
3. Use the interactive Swagger UI to test endpoints

## 📁 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Companies Table
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    sector VARCHAR,
    industry VARCHAR,
    market_cap VARCHAR,
    description TEXT,
    extra_data JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Reports Table
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company_id INTEGER REFERENCES companies(id),
    title VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    report_type VARCHAR DEFAULT 'comprehensive',
    content JSON,
    file_path VARCHAR,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🔐 Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/marketmind_pro
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Kiro CLI
KIRO_CLI_PATH=/usr/local/bin/kiro-cli
KIRO_WORKSPACE_PATH=/tmp/kiro_workspace

# Application
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

## 🚀 Deployment

### Development
```bash
./start_server.sh
```

### Production
```bash
# Install production dependencies
pip install gunicorn

# Start with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 📝 API Usage Examples

### Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Create Report
```bash
curl -X POST "http://localhost:8000/api/reports/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "ticker": "AAPL",
    "report_type": "comprehensive"
  }'
```

## 🔍 Monitoring & Debugging

### Logs
- Application logs: `app.log`
- Console output with structured logging
- Error tracking with stack traces

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛠️ Development

### Adding New Features
1. Create feature directory in `app/features/`
2. Add service, router, and schemas
3. Register router in `app/main.py`
4. Add tests

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📦 Dependencies

### Core
- **FastAPI**: Modern web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization

### Authentication
- **python-jose**: JWT token handling
- **passlib**: Password hashing
- **bcrypt**: Secure password hashing

### Background Tasks
- **Redis**: Task queue backend
- **Celery**: Distributed task queue

### HTTP & Utilities
- **httpx**: Async HTTP client
- **python-dotenv**: Environment variable management

## 🎯 Next Steps

1. **Database Setup**: Configure PostgreSQL and Redis
2. **Kiro CLI Integration**: Ensure Kiro CLI is installed and configured
3. **Frontend Integration**: Connect with React frontend
4. **Production Deployment**: Set up production environment
5. **Monitoring**: Add application monitoring and metrics

## 🤝 Contributing

1. Follow the Vertical Slice Architecture pattern
2. Add comprehensive error handling
3. Include logging for debugging
4. Write tests for new features
5. Update documentation

---

**MarketMind Pro Backend** - Powering AI-driven stock research with institutional-grade analysis.