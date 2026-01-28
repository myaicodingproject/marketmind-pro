# MarketMind Pro - Deployment & Validation

Complete deployment and validation system for MarketMind Pro with background server management.

## Quick Start

```bash
# Deploy entire system
./deploy_hybrid_system.sh

# Quick health check
./quick_test.py

# Full system validation
./validate_hybrid_system.py

# Check system status
./status.sh

# Stop all services
./stop_servers.sh
```

## Scripts Overview

### 🚀 `deploy_hybrid_system.sh`
Main deployment script with background server management:
- Environment setup and dependency installation
- Docker services (PostgreSQL, Redis)
- Background server startup with PID tracking
- Automatic validation
- Non-blocking execution

**Usage:**
```bash
./deploy_hybrid_system.sh          # Full deployment
./deploy_hybrid_system.sh stop     # Stop all services
./deploy_hybrid_system.sh status   # Check status
```

### ✅ `validate_hybrid_system.py`
Comprehensive system validation:
- Backend health and API endpoints
- Frontend accessibility
- Database connectivity
- Docker services status
- Process management verification
- File structure validation

**Features:**
- 8+ validation tests
- Detailed success/failure reporting
- Color-coded output
- Exit codes for CI/CD integration

### ⚡ `quick_test.py`
Rapid validation for development:
- Essential endpoint checks only
- 3-second timeout per test
- Minimal output for quick feedback

### 📊 `status.sh`
Real-time system monitoring:
- Process status with PID tracking
- Docker services overview
- Endpoint health checks
- Recent log tails

### 🛑 `stop_servers.sh`
Clean shutdown:
- Graceful process termination
- PID file cleanup
- Docker services shutdown

## Background Server Management

### Process Tracking
- PID files stored in `./pids/`
- Logs stored in `./logs/`
- Automatic cleanup on exit

### Non-blocking Execution
```bash
# Servers start in background with nohup
nohup uvicorn app.main:app --port 8000 > logs/backend.log 2>&1 &
echo $! > pids/backend.pid
```

### Health Monitoring
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

## Validation Tests

| Test | Description | Endpoint |
|------|-------------|----------|
| Backend Health | Service availability | `/health` |
| API Documentation | Swagger UI access | `/docs` |
| Frontend Access | React app loading | `/` |
| Database Connection | DB connectivity | `/api/v1/status` |
| Report Generation | Endpoint validation | `/api/v1/generate-report` |
| Docker Services | PostgreSQL, Redis | `docker-compose ps` |
| File Structure | Required files exist | Local filesystem |
| Process Management | PID tracking | Process signals |

## Error Handling

### Common Issues

**Port conflicts:**
```bash
# Check what's using ports
lsof -i :8000
lsof -i :3000

# Kill conflicting processes
./stop_servers.sh
```

**Docker services not starting:**
```bash
# Check Docker status
docker-compose ps
docker-compose logs postgres redis

# Restart services
docker-compose down && docker-compose up -d postgres redis
```

**Permission errors:**
```bash
# Make scripts executable
chmod +x *.sh *.py

# Check file permissions
ls -la deploy_hybrid_system.sh
```

### Log Files
- Backend: `./logs/backend.log`
- Frontend: `./logs/frontend.log`
- Deployment: Console output with color coding

## CI/CD Integration

### Exit Codes
- `0`: Success
- `1`: Validation failure
- `2`: Setup error

### Example GitHub Actions
```yaml
- name: Deploy and Validate
  run: |
    ./deploy_hybrid_system.sh
    ./validate_hybrid_system.py
```

## Development Workflow

```bash
# 1. Deploy system
./deploy_hybrid_system.sh

# 2. Quick validation during development
./quick_test.py

# 3. Check status anytime
./status.sh

# 4. Full validation before commit
./validate_hybrid_system.py

# 5. Clean shutdown
./stop_servers.sh
```

## Architecture

```
deploy_hybrid_system.sh
├── Environment Setup
├── Dependency Installation
├── Docker Services (postgres, redis)
├── Background Server Startup
│   ├── Backend (FastAPI) → PID tracking
│   └── Frontend (React) → PID tracking
└── System Validation

validate_hybrid_system.py
├── File Structure Tests
├── Docker Services Tests
├── Process Management Tests
├── Backend API Tests
├── Frontend Access Tests
└── Comprehensive Reporting
```

## Performance

- **Deployment Time**: ~2-3 minutes
- **Validation Time**: ~10-15 seconds
- **Quick Test Time**: ~3-5 seconds
- **Background Startup**: Non-blocking, immediate return

## Security

- No hardcoded credentials
- Environment variable configuration
- Graceful process cleanup
- PID-based process management