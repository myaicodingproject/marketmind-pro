# MarketMind Pro - Folder Reorganization Plan

## Current Status
- **Total Files Analyzed**: 678 files and directories
- **Main Deployment Script**: `./deploy_production.sh`
- **Project Type**: MarketMind Pro - AI-Powered Stock Research Platform

## Organization Strategy

### 🔥 CRITICAL - DO NOT MOVE (Production Dependencies)
These files are directly referenced by `deploy_production.sh` and must stay in root:

#### Core Production Files
```
/mnt/c/kiro/
├── deploy_production.sh                    # Main deployment script
├── complete_production_system.py           # Main backend server
├── react_server.py                        # Frontend server
├── system_monitor.py                       # Process monitoring
├── validate_deployment.py                 # Pre-deployment validation
├── requirements.txt                        # Python dependencies
├── requirements-enhanced.txt               # Enhanced dependencies
├── .env                                   # Environment variables
├── .env.example                           # Environment template
└── logs/                                  # Runtime logs directory
```

#### Core Service Files (Referenced by complete_production_system.py)
```
├── real_kiro_agents.py                    # Kiro CLI integration
├── enhanced_service.py                    # Enhanced processing
├── enhanced_models.py                     # Data models
├── ultra_formatter.py                     # Report formatting
├── ultra_pdf_generator.py                 # PDF generation
├── template_service.py                    # Template processing
├── process_manager.py                     # Process management
├── database_service.py                    # Database operations
├── content_parser_service.py              # Content parsing
├── chart_image_service.py                 # Chart generation
└── polishing_service.py                   # Content polishing
```

### 📁 NEW ORGANIZED STRUCTURE

#### 1. Create `backend/` Directory
**Purpose**: Centralize all backend application code
```
backend/
├── app/                                   # [KEEP EXISTING] Main application
├── services/                              # [NEW] Move root-level services
│   ├── enhanced_service.py               # [MOVE FROM ROOT]
│   ├── database_service.py               # [MOVE FROM ROOT]
│   ├── template_service.py               # [MOVE FROM ROOT]
│   ├── content_parser_service.py         # [MOVE FROM ROOT]
│   ├── chart_image_service.py            # [MOVE FROM ROOT]
│   ├── polishing_service.py              # [MOVE FROM ROOT]
│   ├── ultra_formatter.py                # [MOVE FROM ROOT]
│   ├── ultra_pdf_generator.py            # [MOVE FROM ROOT]
│   └── real_kiro_agents.py               # [MOVE FROM ROOT]
├── models/                                # [NEW] Data models
│   └── enhanced_models.py                # [MOVE FROM ROOT]
├── core/                                  # [NEW] Core utilities
│   └── process_manager.py                # [MOVE FROM ROOT]
├── tests/                                 # [NEW] All test files
│   ├── test_*.py                         # [MOVE FROM ROOT]
│   └── integration/                      # [NEW] Integration tests
├── alembic/                              # [KEEP EXISTING] DB migrations
└── requirements/                         # [NEW] Dependency management
    ├── base.txt                          # [MOVE FROM requirements.txt]
    └── enhanced.txt                      # [MOVE FROM requirements-enhanced.txt]
```

#### 2. Create `frontend/` Directory
**Purpose**: Centralize all frontend code
```
frontend/
├── react-app/                           # [RENAME FROM frontend-react]
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
├── static/                               # [MOVE FROM ROOT]
│   ├── css/
│   └── assets/
├── templates/                            # [MOVE FROM ROOT]
│   ├── handlebars/
│   └── stock_report.html
└── server/                               # [NEW] Frontend server code
    └── react_server.py                   # [MOVE FROM ROOT]
```

#### 3. Create `docs/` Directory
**Purpose**: Centralize all documentation
```
docs/
├── README.md                             # [KEEP IN ROOT + COPY]
├── DEVLOG.md                             # [MOVE FROM ROOT]
├── deployment/                           # [NEW] Deployment docs
│   ├── DEPLOYMENT.md                     # [MOVE FROM ROOT]
│   ├── DEPLOYMENT_READY.md               # [MOVE FROM ROOT]
│   ├── LOCAL_SETUP.md                    # [MOVE FROM ROOT]
│   ├── AUTH_SETUP.md                     # [MOVE FROM ROOT]
│   └── DATABASE_CONFIG.md                # [MOVE FROM ROOT]
├── implementation/                       # [NEW] Implementation docs
│   ├── *.md files from root             # [MOVE ALL CAPS .md FILES]
│   └── session-summaries/               # [NEW]
│       └── SESSION_SUMMARY_*.md         # [MOVE FROM ROOT]
├── api/                                  # [NEW] API documentation
└── architecture/                         # [NEW] Architecture docs
```

#### 4. Create `tools/` Directory
**Purpose**: Development and utility scripts
```
tools/
├── deployment/                           # [NEW] Deployment scripts
│   ├── deploy_hybrid_system.sh          # [MOVE FROM ROOT]
│   ├── start_with_monitoring.sh         # [MOVE FROM ROOT]
│   ├── stop_servers.sh                  # [MOVE FROM ROOT]
│   ├── status.sh                        # [MOVE FROM ROOT]
│   └── monitor_kiro.sh                  # [MOVE FROM ROOT]
├── testing/                             # [NEW] Testing utilities
│   ├── debug_*.py                       # [MOVE FROM ROOT]
│   ├── validate_*.py                    # [MOVE FROM ROOT]
│   └── quick_test.py                    # [MOVE FROM ROOT]
├── data/                                # [NEW] Data processing
│   ├── data_extraction_service.py       # [MOVE FROM ROOT]
│   └── fix_*.py                         # [MOVE FROM ROOT]
└── monitoring/                          # [NEW] Monitoring tools
    ├── production_monitor.py            # [MOVE FROM ROOT]
    ├── auto_monitor.py                  # [MOVE FROM ROOT]
    └── debug_monitor.py                 # [MOVE FROM ROOT]
```

#### 5. Create `data/` Directory
**Purpose**: Data storage and outputs
```
data/
├── reports/                             # [MOVE FROM ROOT]
│   └── *.pdf files
├── reports_storage/                     # [MOVE FROM ROOT]
│   └── reports.json
├── charts/                              # [NEW] Chart outputs
│   ├── chart_output/                    # [MOVE FROM ROOT]
│   └── *.png files                     # [MOVE FROM ROOT]
├── test_output/                         # [MOVE FROM ROOT]
└── logs/                                # [KEEP IN ROOT - SYMLINK HERE]
```

#### 6. Create `config/` Directory
**Purpose**: Configuration files
```
config/
├── .env.example                         # [COPY FROM ROOT]
├── .gitignore                           # [MOVE FROM ROOT]
├── .kiroignore                          # [MOVE FROM ROOT]
├── .coveragerc                          # [MOVE FROM ROOT]
├── pytest.ini                          # [MOVE FROM ROOT]
├── package.json                         # [MOVE FROM ROOT]
├── alembic.ini                          # [MOVE FROM ROOT]
└── docker/                             # [NEW] Docker configs
    └── docker-compose.yml               # [MOVE FROM hackathon-project]
```

#### 7. Archive Old/Unused Files
**Purpose**: Keep old files but out of the way
```
archive/
├── experiments/                         # [MOVE FROM ROOT]
├── hackathon-project/                   # [MOVE FROM ROOT]
├── backend/                             # [MOVE FROM ROOT - old backend]
├── old-implementations/                 # [NEW]
│   ├── simplified_production_system.py # [MOVE FROM ROOT]
│   ├── professional_pdf_generator_backup.py # [MOVE FROM ROOT]
│   └── *.py files with "backup" or "old" # [MOVE FROM ROOT]
├── screenshots/                         # [NEW]
│   ├── *.png screenshot files          # [MOVE FROM ROOT]
│   └── Firefox_Screenshot_*.png        # [MOVE FROM ROOT]
└── temp-files/                         # [NEW]
    ├── empty files (fix, my, use, etc.) # [MOVE FROM ROOT]
    └── temporary scripts                # [MOVE FROM ROOT]
```

### 🔧 IMPLEMENTATION STEPS

#### Phase 1: Create New Directory Structure
```bash
mkdir -p backend/{services,models,core,tests/integration,requirements}
mkdir -p frontend/{react-app,static,templates,server}
mkdir -p docs/{deployment,implementation,session-summaries,api,architecture}
mkdir -p tools/{deployment,testing,data,monitoring}
mkdir -p data/{reports,charts,test_output}
mkdir -p config/docker
mkdir -p archive/{old-implementations,screenshots,temp-files}
```

#### Phase 2: Move Files (Preserve Production Dependencies)
**CRITICAL**: Update import paths in moved files

1. **Backend Services** (Update imports in complete_production_system.py)
2. **Frontend Files** (Update react_server.py paths)
3. **Documentation** (No import dependencies)
4. **Tools & Utilities** (Update any cross-references)
5. **Archive Files** (No active dependencies)

#### Phase 3: Update Configuration Files
1. Update `deploy_production.sh` with new paths
2. Update `complete_production_system.py` imports
3. Update `react_server.py` paths
4. Create symlinks for critical paths if needed

#### Phase 4: Validation
1. Test `./deploy_production.sh` still works
2. Verify all imports resolve correctly
3. Run test suite to ensure functionality
4. Update documentation with new structure

### 📋 FILE MOVEMENT MAPPING

#### Files to Move to `backend/services/`
- enhanced_service.py → backend/services/
- database_service.py → backend/services/
- template_service.py → backend/services/
- content_parser_service.py → backend/services/
- chart_image_service.py → backend/services/
- polishing_service.py → backend/services/
- ultra_formatter.py → backend/services/
- ultra_pdf_generator.py → backend/services/
- real_kiro_agents.py → backend/services/
- data_extraction_service.py → backend/services/

#### Files to Move to `backend/models/`
- enhanced_models.py → backend/models/

#### Files to Move to `backend/core/`
- process_manager.py → backend/core/

#### Files to Move to `backend/tests/`
- test_*.py (all test files) → backend/tests/
- *_test.py → backend/tests/

#### Files to Move to `frontend/`
- frontend-react/ → frontend/react-app/
- react_server.py → frontend/server/
- static/ → frontend/static/
- templates/ → frontend/templates/

#### Files to Move to `docs/`
- DEVLOG.md → docs/
- All CAPS .md files → docs/implementation/
- SESSION_SUMMARY_*.md → docs/session-summaries/

#### Files to Move to `tools/`
- All deployment scripts → tools/deployment/
- All debug/test utilities → tools/testing/
- All monitoring scripts → tools/monitoring/

#### Files to Move to `data/`
- reports/ → data/reports/
- reports_storage/ → data/reports_storage/
- chart_output/ → data/charts/chart_output/
- test_output/ → data/test_output/
- *.png chart files → data/charts/

#### Files to Move to `archive/`
- experiments/ → archive/
- hackathon-project/ → archive/
- backend/ (old) → archive/
- All screenshot files → archive/screenshots/
- Empty/temp files → archive/temp-files/

### ⚠️ CRITICAL WARNINGS

1. **DO NOT MOVE** these files from root:
   - deploy_production.sh
   - complete_production_system.py
   - .env
   - logs/ directory

2. **UPDATE IMPORTS** after moving:
   - complete_production_system.py imports
   - react_server.py paths
   - Any cross-file references

3. **TEST THOROUGHLY** after reorganization:
   - Run ./deploy_production.sh
   - Verify all services start correctly
   - Check all API endpoints work

4. **BACKUP FIRST**:
   - Create full backup before starting
   - Test in isolated environment first

### 📊 EXPECTED RESULTS

**Before**: 678 files scattered in root directory
**After**: ~50 files in root (only production essentials)

**Root Directory After Cleanup**:
```
/mnt/c/kiro/
├── deploy_production.sh          # Production deployment
├── complete_production_system.py # Main backend
├── .env                         # Environment config
├── .env.example                 # Environment template
├── README.md                    # Project overview
├── logs/                        # Runtime logs
├── .kiro/                       # Kiro CLI config
├── Reference/                   # Reference materials
├── backend/                     # Backend application
├── frontend/                    # Frontend application
├── docs/                        # Documentation
├── tools/                       # Development tools
├── data/                        # Data and outputs
├── config/                      # Configuration files
└── archive/                     # Archived/old files
```

This organization will make the project much more maintainable while preserving all production functionality.
