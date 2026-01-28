# Project Structure

## Directory Layout

```
hackathon-project/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes and endpoints
│   │   ├── core/          # Core functionality, config, security
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI application entry
│   ├── tests/             # Backend tests
│   ├── alembic/           # Database migrations
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API client services
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container
├── .kiro/
│   ├── steering/          # Project knowledge and guidelines
│   ├── prompts/           # Custom Kiro commands
│   └── settings/          # Kiro configuration
├── docs/                  # Project documentation
├── docker-compose.yml     # Development environment
├── README.md              # Project overview and setup
├── DEVLOG.md              # Development timeline and decisions
└── .env.example           # Environment variables template
```

## File Naming Conventions

### Backend (Python)
- **Files**: snake_case (e.g., `user_service.py`)
- **Classes**: PascalCase (e.g., `UserService`)
- **Functions**: snake_case (e.g., `get_user_by_id`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_ATTEMPTS`)

### Frontend (TypeScript/React)
- **Files**: kebab-case for components (e.g., `user-profile.tsx`)
- **Components**: PascalCase (e.g., `UserProfile`)
- **Functions**: camelCase (e.g., `getUserById`)
- **Types/Interfaces**: PascalCase (e.g., `UserData`)

## Module Organization

### Backend Structure (Vertical Slice Architecture)
```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/     # Route handlers
│   │   └── dependencies/  # Dependency injection
├── core/
│   ├── config.py          # Configuration management
│   ├── security.py        # Authentication/authorization
│   └── database.py        # Database connection
├── features/              # Feature-based organization
│   ├── users/
│   │   ├── models.py      # User database models
│   │   ├── schemas.py     # User Pydantic schemas
│   │   ├── service.py     # User business logic
│   │   └── router.py      # User API routes
│   └── [feature]/         # Additional features
└── shared/
    ├── exceptions.py      # Custom exceptions
    ├── utils.py           # Utility functions
    └── constants.py       # Application constants
```

### Frontend Structure (Feature-based)
```
src/
├── components/
│   ├── ui/                # Basic UI components
│   ├── forms/             # Form components
│   └── layout/            # Layout components
├── features/              # Feature-specific components
│   ├── users/
│   │   ├── components/    # User-related components
│   │   ├── hooks/         # User-related hooks
│   │   └── services/      # User API services
│   └── [feature]/         # Additional features
├── shared/
│   ├── hooks/             # Shared custom hooks
│   ├── services/          # Shared API services
│   ├── types/             # Shared TypeScript types
│   └── utils/             # Shared utility functions
└── pages/                 # Page-level components
```

## Configuration Files

### Backend Configuration
- **`requirements.txt`**: Python dependencies
- **`alembic.ini`**: Database migration configuration
- **`.env`**: Environment variables (not in git)
- **`pyproject.toml`**: Python project configuration
- **`Dockerfile`**: Container configuration

### Frontend Configuration
- **`package.json`**: Node.js dependencies and scripts
- **`tsconfig.json`**: TypeScript configuration
- **`vite.config.ts`**: Build tool configuration
- **`tailwind.config.js`**: CSS framework configuration
- **`Dockerfile`**: Container configuration

### Development Configuration
- **`docker-compose.yml`**: Local development environment
- **`.gitignore`**: Git ignore patterns
- **`.env.example`**: Environment variables template

## Documentation Structure

### Required Documentation
- **`README.md`**: Project overview, setup instructions, usage
- **`DEVLOG.md`**: Development timeline, decisions, challenges
- **`docs/api.md`**: API documentation and examples
- **`docs/deployment.md`**: Deployment instructions
- **`docs/architecture.md`**: Technical architecture details

### Code Documentation
- **Docstrings**: All public functions and classes
- **Type hints**: All function parameters and returns
- **Comments**: Complex business logic and algorithms
- **README files**: In each major directory explaining purpose

## Asset Organization

### Static Assets
- **`frontend/public/images/`**: Images and icons
- **`frontend/public/fonts/`**: Custom fonts
- **`frontend/src/assets/`**: Bundled assets

### Generated Assets
- **`backend/logs/`**: Application logs (not in git)
- **`frontend/dist/`**: Built frontend assets (not in git)
- **`coverage/`**: Test coverage reports (not in git)

## Build Artifacts

### Backend Artifacts
- **`__pycache__/`**: Python bytecode (not in git)
- **`.pytest_cache/`**: Pytest cache (not in git)
- **`htmlcov/`**: Coverage HTML reports (not in git)

### Frontend Artifacts
- **`node_modules/`**: Node.js dependencies (not in git)
- **`dist/`**: Built application (not in git)
- **`.next/`**: Next.js cache (if using Next.js, not in git)

## Environment-Specific Files

### Development
- **`.env.development`**: Development environment variables
- **`docker-compose.override.yml`**: Development overrides

### Testing
- **`.env.test`**: Test environment variables
- **`pytest.ini`**: Pytest configuration

### Production
- **`.env.production`**: Production environment variables (not in git)
- **`docker-compose.prod.yml`**: Production configuration

## Reference Integration Points

### Kiro CLI Integration
- **`.kiro/steering/`**: Links to `C:\kiro\Reference\` materials
- **`.kiro/prompts/`**: Custom commands based on reference patterns
- **`.kiro/settings/`**: Configuration for optimal workflow

### Reference Material Mapping
- **AI-Optimized FastAPI**: Foundation architecture implementation
- **Claude Commands**: Development workflow and validation
- **AI-as-Educator**: Code review and learning approach
- **Hackathon Template**: Scoring optimization and documentation
