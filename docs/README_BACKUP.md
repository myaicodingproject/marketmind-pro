# MarketMind Pro - AI-Powered Stock Research Platform

**The Mind Behind Smart Investing** - Generate comprehensive 25-30 page institutional-quality stock research reports in 5-8 minutes using 100% Kiro CLI AI processing.

## Overview

MarketMind Pro transforms the $5,000+ institutional analyst experience into an accessible $49/month service for elite retail investors. Our platform generates professional stock research reports with the same depth and quality as Wall Street firms, but in minutes instead of weeks.

## Key Features

### 🚀 One-Click Report Generation
- Enter any stock ticker → Get comprehensive 25-30 page report
- 5-8 minute generation time using parallel AI processing
- Institutional-quality analysis with professional formatting

### 📊 Six Core Report Sections
- **Executive Summary** (2 pages) - Price targets, ratings, key metrics
- **Company Deep Dive** (5 pages) - Business model, competitive analysis
- **Financial Analysis** (8 pages) - 3-year historical + 2-year projections
- **Valuation Analysis** (6 pages) - DCF, peer comparison, scenario modeling
- **Risk Assessment** (3 pages) - Key risks and mitigation strategies
- **Interactive Q&A** - Chat with your report for clarifications

### 🎨 Professional Visualizations
- Timeline charts showing company milestones
- Financial comparison tables and matrices
- Business model canvas visualization
- Corporate-styled bar/line/pie charts
- Peer comparison analysis

### 💡 Innovative Features
- **Report Chat** - Ask questions about any section
- **Scenario Modeling** - Adjust assumptions, see real-time impact
- **Mobile-Optimized** - Full reports readable on any device
- **PDF Export** - Professional formatting preserved

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker and Docker Compose
- Kiro CLI installed and authenticated

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/username/marketmind-pro
cd marketmind-pro
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your API keys and database settings
```

### 3. Database Setup
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run database migrations
cd backend
python -m alembic upgrade head
```

### 4. Install Dependencies
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend-react
npm install
```

### 5. Start the Application
```bash
# Start backend (from backend directory)
uvicorn app.main:app --reload --port 8000

# Start frontend (from frontend-react directory)
npm start
```

### 6. Access the Application
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin

## Architecture Overview

### Technology Stack
- **Backend**: FastAPI with Pydantic AI integration
- **Frontend**: React 18 with TypeScript
- **Database**: PostgreSQL with pgvector for RAG
- **Caching**: Redis for performance optimization
- **AI Processing**: Kiro CLI with custom prompts
- **Containerization**: Docker and Docker Compose

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  Kiro CLI AI    │
│                 │◄──►│                 │◄──►│   Processing    │
│  - Report UI    │    │  - API Routes   │    │  - 8 Parallel  │
│  - Progress     │    │  - Orchestration│    │    Subagents    │
│  - Chat Interface│   │  - Quality Gates│    │  - Custom Prompts│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   PostgreSQL    │              │
         └──────────────►│   + pgvector    │◄─────────────┘
                        │  - Reports DB   │
                        │  - Vector Store │
                        │  - User Data    │
                        └─────────────────┘
```

### Key Components

#### Backend Services
- **Report Generator** (`app/services/report_generator.py`): Orchestrates AI processing
- **Kiro CLI Integration** (`app/services/kiro_service.py`): Manages AI subagents
- **Quality Auditor** (`app/services/quality_auditor.py`): Validates report quality
- **Chart Generator** (`app/services/chart_service.py`): Creates professional visualizations

#### Frontend Components
- **StockForm** (`src/components/StockForm.tsx`): Report generation interface
- **ProgressTracker** (`src/components/ProgressTracker.tsx`): Real-time progress
- **ReportDisplay** (`src/components/ReportDisplay.tsx`): Report viewing and chat
- **Dashboard** (`src/pages/Dashboard.tsx`): Main application interface

#### Kiro CLI Integration
- **Custom Prompts** (`.kiro/prompts/`): 11+ specialized AI commands
- **Steering Documents** (`.kiro/steering/`): Project knowledge and guidelines
- **Quality Gates**: Automated validation and retry mechanisms

## Usage Examples

### Generate a Stock Report
```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/generate-report" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "include_charts": true}'

# Via Web Interface
1. Navigate to http://localhost:3000
2. Enter stock symbol (e.g., "AAPL")
3. Select report options
4. Click "Generate Report"
5. Monitor real-time progress
6. Download or view completed report
```

### Chat with Report
```bash
# Ask questions about generated report
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"report_id": "123", "question": "What are the main risks?"}'
```

### Scenario Modeling
```bash
# Adjust valuation assumptions
curl -X POST "http://localhost:8000/api/v1/scenario" \
  -H "Content-Type: application/json" \
  -d '{"report_id": "123", "growth_rate": 0.15, "discount_rate": 0.10}'
```

## Development with Kiro CLI

### Core Workflow
```bash
# Load project context
@prime

# Plan new features
@plan-feature

# Execute implementation
@execute

# Review code quality
@code-review
```

### Custom Prompts Available
- `@generate-section` - Create specific report sections
- `@quality-audit` - Validate report completeness
- `@create-charts` - Generate professional visualizations
- `@financial-analysis` - Perform DCF and valuation analysis

## Performance Metrics

### Current Benchmarks
- **Report Generation**: 5-8 minutes (parallel processing)
- **Quality Score**: 85%+ average across all sections
- **Success Rate**: 87.5% (7/8 sections minimum threshold)
- **Chart Generation**: <5 seconds per visualization
- **Database Queries**: <100ms average response time

### Scalability
- **Concurrent Reports**: Up to 10 simultaneous generations
- **Database**: Optimized for 10,000+ reports
- **Caching**: 80% hit rate reduces AI costs by 70%

## Troubleshooting

### Common Issues

**Report generation fails**
```bash
# Check Kiro CLI status
kiro-cli status

# Verify database connection
python -c "from app.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check Redis connection
redis-cli ping
```

**Slow report generation**
```bash
# Monitor parallel processing
tail -f logs/kiro_execution.log

# Check system resources
docker stats

# Verify AI API limits
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/usage
```

**Frontend not loading**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check environment variables
cat .env | grep REACT_APP
```

**Database connection errors**
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check database logs
docker-compose logs postgres

# Verify connection string
echo $DATABASE_URL
```

### Getting Help
- **Logs**: Check `logs/` directory for detailed error information
- **API Docs**: Visit http://localhost:8000/docs for interactive API documentation
- **Kiro CLI**: Use `kiro-cli --help` for command assistance
- **Issues**: Open GitHub issue with error details and logs

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Use Kiro CLI for development (`@prime` → `@plan-feature` → `@execute`)
4. Run tests (`pytest` for backend, `npm test` for frontend)
5. Update documentation
6. Submit pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Kiro CLI](https://kiro.dev) for AI-powered development
- Developed for the [Dynamous Kiro Hackathon](https://dynamous.ai/kiro-hackathon)
- Inspired by institutional research standards and accessibility needs

---

**MarketMind Pro** - Democratizing institutional-quality stock research through AI innovation.
