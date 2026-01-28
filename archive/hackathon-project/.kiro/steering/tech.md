# Technical Architecture

## Technology Stack

### Core Technologies (Fixed)
- **Backend**: Python 3.11+ with FastAPI
- **AI Framework**: Pydantic AI for intelligent data processing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: React 18+ with TypeScript
- **Caching**: Redis for performance optimization

### Supporting Technologies
- **Testing**: pytest with fixtures and coverage
- **Validation**: Pydantic v2 for data validation
- **API Documentation**: FastAPI automatic OpenAPI/Swagger
- **Database Migrations**: Alembic
- **Process Management**: Uvicorn with Gunicorn
- **Containerization**: Docker and Docker Compose

## Architecture Patterns

### Foundation Architecture (From AI-Optimized FastAPI Reference)
**6 Foundation Layers Implementation**:
1. **Testing & Validation Layer**: pytest, coverage, validation patterns
2. **Structured Logging Layer**: Comprehensive logging with correlation IDs
3. **Infrastructure Layer**: Docker, environment management, health checks
4. **Database Layer**: PostgreSQL, SQLAlchemy, migrations, connection pooling
5. **Monitoring & Health Layer**: Health endpoints, metrics, observability
6. **Shared Patterns Layer**: Common utilities, error handling, response patterns

### Vertical Slice Architecture (VSA)
- **Feature-based organization**: Each feature contains all layers
- **Minimal coupling**: Features are independent and testable
- **Clear boundaries**: Well-defined interfaces between components
- **Scalable structure**: Easy to add new features without affecting existing ones

## Code Standards

### Python Standards
- **PEP 8 compliance** with Black formatting
- **Type hints required** (mypy strict mode)
- **Docstrings**: Google style for all public functions
- **Import organization**: isort for consistent imports

### TypeScript/React Standards
- **Strict TypeScript**: No implicit any, strict null checks
- **Component patterns**: Functional components with hooks
- **Naming**: PascalCase for components, camelCase for functions
- **File organization**: Feature-based folder structure

## Reference Integration

### AI-Optimized FastAPI Command
- **Location**: `C:\kiro\Reference\AI-Optimized FastAPI Command\`
- **Usage**: Foundation setup, architecture patterns, best practices
- **Key Files**: `init-ai-optimized-fastapi.md`, `QUICK-START-GUIDE.md`

### Claude Commands
- **Location**: `C:\kiro\Reference\claude-commands\`
- **Usage**: Development workflow, validation patterns
- **Key Patterns**: PIV loop (prime → plan-feature → execute), validation suite

### AI-as-Educator Methodology
- **Location**: `C:\kiro\Reference\coding-agent-as-educator\`
- **Usage**: Learning approach, question frameworks
- **Application**: Code review, architecture decisions, debugging
