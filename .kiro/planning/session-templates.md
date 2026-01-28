# Session Templates for Subagents

## How to Use These Templates

Each session template provides:
1. **Clear objectives** and deliverables
2. **Detailed task breakdown** with acceptance criteria
3. **Technical specifications** and requirements
4. **Dependencies** and integration points
5. **Quality checkpoints** and validation steps

## Session A1: Backend Foundation

### Objective
Set up FastAPI backend with Kiro CLI integration and database foundation.

### Duration & Dependencies
- **Time:** 4 hours
- **Dependencies:** None (can start immediately)
- **Subagent:** Backend Specialist

### Detailed Tasks

#### A1.1: Execute `@quickstart` for Kiro CLI Setup
**Acceptance Criteria:**
- [ ] Kiro CLI properly configured in project
- [ ] All steering documents accessible
- [ ] Custom prompts directory created
- [ ] Test Kiro CLI basic functionality

**Commands to Execute:**
```bash
cd /mnt/c/kiro
kiro-cli chat "@quickstart"
```

#### A1.2: Initialize FastAPI with AI-Optimized Foundation
**Acceptance Criteria:**
- [ ] FastAPI project structure created
- [ ] AI-Optimized foundation patterns implemented
- [ ] Basic middleware and configuration set up
- [ ] Health check endpoint working

**Reference:** Use patterns from `C:\kiro\Reference\AI-Optimized FastAPI Command\`

#### A1.3: Set up PostgreSQL Database Schema
**Acceptance Criteria:**
- [ ] PostgreSQL database created and connected
- [ ] User management tables created
- [ ] Stock data tables designed
- [ ] Report storage schema implemented
- [ ] Database migrations working

**Schema Requirements:**
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stocks table
CREATE TABLE stocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    ticker VARCHAR(10) NOT NULL,
    report_data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'completed'
);
```

#### A1.4: Create Basic API Structure
**Acceptance Criteria:**
- [ ] Authentication endpoints (/auth/login, /auth/register)
- [ ] Stock endpoints (/stocks/search, /stocks/{ticker})
- [ ] Report endpoints (/reports/generate, /reports/{id})
- [ ] Proper error handling middleware
- [ ] API documentation with FastAPI/Swagger

**API Structure:**
```python
# app/api/v1/
├── auth.py          # Authentication endpoints
├── stocks.py        # Stock data endpoints  
├── reports.py       # Report generation endpoints
└── users.py         # User management endpoints
```

#### A1.5: Test Kiro CLI Integration
**Acceptance Criteria:**
- [ ] FastAPI can execute Kiro CLI commands
- [ ] Proper error handling for Kiro failures
- [ ] Response parsing working correctly
- [ ] Basic test prompt execution successful

**Integration Test:**
```python
async def test_kiro_integration():
    result = await kiro_engine.execute_prompt("test-prompt", {"ticker": "AAPL"})
    assert result is not None
    assert "error" not in result
```

### Deliverables
1. **Working FastAPI backend** with all endpoints
2. **PostgreSQL database** with complete schema
3. **Kiro CLI integration** tested and working
4. **API documentation** generated
5. **Basic test suite** passing

### Quality Checkpoints
- [ ] All endpoints return proper HTTP status codes
- [ ] Database connections working reliably
- [ ] Kiro CLI integration handles errors gracefully
- [ ] API documentation is complete and accurate
- [ ] Code follows FastAPI best practices

---

## Session B1: Frontend Foundation

### Objective
Create React + TypeScript frontend with authentication and basic navigation.

### Duration & Dependencies
- **Time:** 4 hours
- **Dependencies:** None (can start immediately)
- **Subagent:** Frontend Specialist

### Detailed Tasks

#### B1.1: Initialize React + TypeScript Project
**Acceptance Criteria:**
- [ ] React 18+ project created with TypeScript
- [ ] Vite or Create React App configured
- [ ] ESLint and Prettier set up
- [ ] Basic folder structure established
- [ ] Development server running

**Project Structure:**
```
src/
├── components/
│   ├── ui/              # Basic UI components
│   ├── forms/           # Form components
│   └── layout/          # Layout components
├── pages/
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   └── Report.tsx
├── hooks/               # Custom React hooks
├── services/            # API client services
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── styles/              # CSS/SCSS files
```

#### B1.2: Set up Authentication System
**Acceptance Criteria:**
- [ ] Login/Register forms created
- [ ] JWT token handling implemented
- [ ] Protected route wrapper component
- [ ] Authentication context provider
- [ ] Logout functionality working

**Components to Create:**
```typescript
// components/auth/LoginForm.tsx
interface LoginFormProps {
  onSuccess: (token: string) => void;
  onError: (error: string) => void;
}

// components/auth/ProtectedRoute.tsx
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

// contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}
```

#### B1.3: Create Basic Routing and Navigation
**Acceptance Criteria:**
- [ ] React Router configured
- [ ] Navigation component with menu items
- [ ] Route protection implemented
- [ ] Breadcrumb navigation
- [ ] Mobile-responsive navigation

**Routes:**
```typescript
const routes = [
  { path: '/', component: Dashboard, protected: true },
  { path: '/login', component: Login, protected: false },
  { path: '/register', component: Register, protected: false },
  { path: '/reports/:id', component: Report, protected: true },
  { path: '/profile', component: Profile, protected: true }
];
```

#### B1.4: Design Dashboard Layout
**Acceptance Criteria:**
- [ ] Responsive dashboard layout
- [ ] Stock search component
- [ ] Recent reports list
- [ ] User profile section
- [ ] Mobile-optimized design

**Dashboard Components:**
```typescript
// components/dashboard/StockSearch.tsx
interface StockSearchProps {
  onStockSelect: (ticker: string) => void;
  placeholder?: string;
}

// components/dashboard/RecentReports.tsx
interface RecentReportsProps {
  reports: Report[];
  onReportClick: (reportId: string) => void;
}
```

#### B1.5: Set up API Client Service
**Acceptance Criteria:**
- [ ] Axios or Fetch API wrapper
- [ ] Request/response interceptors
- [ ] Error handling middleware
- [ ] TypeScript interfaces for API responses
- [ ] Environment-based API URLs

**API Client:**
```typescript
// services/api.ts
class ApiClient {
  private baseURL: string;
  private token: string | null;

  async get<T>(endpoint: string): Promise<T>;
  async post<T>(endpoint: string, data: any): Promise<T>;
  async put<T>(endpoint: string, data: any): Promise<T>;
  async delete<T>(endpoint: string): Promise<T>;
}

// services/stockService.ts
export const stockService = {
  searchStocks: (query: string) => Promise<Stock[]>,
  getStockData: (ticker: string) => Promise<StockData>,
  generateReport: (ticker: string) => Promise<Report>
};
```

### Deliverables
1. **React + TypeScript project** with proper configuration
2. **Authentication system** with login/register/logout
3. **Navigation and routing** with protected routes
4. **Dashboard layout** with key components
5. **API client service** ready for backend integration

### Quality Checkpoints
- [ ] TypeScript compilation without errors
- [ ] All components properly typed
- [ ] Responsive design works on mobile/desktop
- [ ] Authentication flow works end-to-end
- [ ] Code follows React best practices

---

## Session C1: Data Pipeline Setup

### Objective
Set up data fetching services for SEC filings, financial data, and market information.

### Duration & Dependencies
- **Time:** 3 hours
- **Dependencies:** None (can start immediately)
- **Subagent:** Data Specialist

### Detailed Tasks

#### C1.1: Research and Test SEC EDGAR API
**Acceptance Criteria:**
- [ ] SEC EDGAR API endpoints identified
- [ ] Rate limiting and authentication understood
- [ ] Test data retrieval for sample companies
- [ ] Error handling for API failures
- [ ] Data parsing and normalization working

**Key Endpoints:**
```python
# SEC EDGAR API endpoints
EDGAR_BASE_URL = "https://data.sec.gov/api/xbrl"
COMPANY_FACTS_URL = f"{EDGAR_BASE_URL}/companyfacts/CIK{cik}.json"
COMPANY_CONCEPT_URL = f"{EDGAR_BASE_URL}/companyconcept/CIK{cik}/us-gaap/{concept}.json"

# Required headers
HEADERS = {
    "User-Agent": "MarketMind Pro contact@marketmind.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}
```

#### C1.2: Set up Alpha Vantage API Integration
**Acceptance Criteria:**
- [ ] Alpha Vantage API key configured
- [ ] Real-time stock price retrieval
- [ ] Financial statement data access
- [ ] Rate limiting handled properly
- [ ] Data caching implemented

**API Functions:**
```python
class AlphaVantageClient:
    def get_stock_quote(self, ticker: str) -> dict
    def get_income_statement(self, ticker: str) -> dict
    def get_balance_sheet(self, ticker: str) -> dict
    def get_cash_flow(self, ticker: str) -> dict
    def get_company_overview(self, ticker: str) -> dict
```

#### C1.3: Create Data Fetching Service
**Acceptance Criteria:**
- [ ] Unified data service interface
- [ ] Multiple data source integration
- [ ] Data validation and cleaning
- [ ] Caching layer implemented
- [ ] Error handling and retries

**Service Architecture:**
```python
class DataFetchingService:
    def __init__(self):
        self.sec_client = SECClient()
        self.alpha_vantage_client = AlphaVantageClient()
        self.cache = RedisCache()
    
    async def get_company_data(self, ticker: str) -> CompanyData:
        # Fetch from multiple sources and combine
        pass
    
    async def get_financial_statements(self, ticker: str) -> FinancialStatements:
        # Get comprehensive financial data
        pass
```

#### C1.4: Design Data Storage Schema
**Acceptance Criteria:**
- [ ] Database schema for raw data storage
- [ ] Data normalization strategy
- [ ] Update frequency planning
- [ ] Data retention policies
- [ ] Performance optimization

**Schema Design:**
```sql
-- Raw financial data storage
CREATE TABLE financial_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- 'income_statement', 'balance_sheet', etc.
    period_end DATE NOT NULL,
    data JSONB NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stock price data
CREATE TABLE stock_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### C1.5: Test Data Retrieval for Sample Stocks
**Acceptance Criteria:**
- [ ] Successfully retrieve data for AAPL, MSFT, GOOGL
- [ ] Data quality validation passes
- [ ] Performance benchmarks met
- [ ] Error scenarios handled gracefully
- [ ] Data consistency checks pass

**Test Cases:**
```python
async def test_data_retrieval():
    service = DataFetchingService()
    
    # Test major stocks
    for ticker in ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']:
        data = await service.get_company_data(ticker)
        assert data is not None
        assert data.ticker == ticker
        assert data.financial_statements is not None
```

### Deliverables
1. **SEC EDGAR integration** with proper rate limiting
2. **Alpha Vantage integration** for real-time data
3. **Unified data service** with caching
4. **Database schema** for data storage
5. **Test suite** validating data retrieval

### Quality Checkpoints
- [ ] All API integrations working reliably
- [ ] Data quality meets requirements
- [ ] Performance targets achieved
- [ ] Error handling comprehensive
- [ ] Code follows data engineering best practices

---

*Continue with remaining session templates...*

## Template Usage Instructions

### For Subagents:
1. **Read the entire session template** before starting
2. **Follow the task order** as dependencies may exist
3. **Check acceptance criteria** for each task before marking complete
4. **Document any deviations** or issues encountered
5. **Update progress** in the task tracking system

### For Integration:
1. **Verify deliverables** meet quality checkpoints
2. **Test integration points** with other sessions
3. **Document any interface changes** needed
4. **Communicate blockers** immediately to other teams

*Last Updated: 2026-01-21*
