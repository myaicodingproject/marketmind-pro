# Legacy Backend Structure Archive

**Moved Date**: January 27, 2026  
**Reason**: Consolidating to flat structure for deployment simplicity

## What Was Moved Here

### From `/mnt/c/kiro/backend/`
- **backend/app/** - Old FastAPI application structure
- **backend/services/** - Duplicate service implementations  
- **backend/models/** - Duplicate model definitions
- **backend/core/** - Duplicate core utilities
- **backend/tests/** - Backend test files
- **backend/requirements/** - Requirements files (kept copies in root)

## Why Moved
- **Deployment Script**: Uses flat structure (services/, models/, core/ in root)
- **Import Simplicity**: Flat imports work better with current system
- **Consistency**: Single source of truth for each component
- **Professional**: Clean, organized structure for hackathon judges

## Recovery Instructions
If needed, these files can be restored by:
1. Copying back to original locations
2. Updating import statements in `complete_production_system.py`
3. Modifying `deploy_production.sh` to use backend/ structure

## Current Active Structure
```
marketmind-pro/
├── services/           # ACTIVE - Core business logic
├── models/            # ACTIVE - Data models  
├── core/              # ACTIVE - Utilities
├── complete_production_system.py  # ACTIVE - Main system
└── deploy_production.sh           # ACTIVE - Deployment
```
