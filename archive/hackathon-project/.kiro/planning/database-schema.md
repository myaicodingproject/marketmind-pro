# Complete Database Schema Design

## Database Architecture Overview

### Multi-Database Strategy
- **Primary Database:** PostgreSQL (ACID compliance, complex queries)
- **Vector Database:** ChromaDB (RAG embeddings and similarity search)
- **Cache Database:** Redis (session data, temporary storage)
- **File Storage:** AWS S3 (PDFs, charts, documents)

## Core Database Schema (PostgreSQL)

### 1. User Management Schema

#### Users Table
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Subscription management
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'elite')),
    subscription_status VARCHAR(20) DEFAULT 'active' CHECK (subscription_status IN ('active', 'cancelled', 'expired', 'suspended')),
    subscription_started_at TIMESTAMP,
    subscription_expires_at TIMESTAMP,
    stripe_customer_id VARCHAR(100),
    
    -- Account verification
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    email_verification_expires TIMESTAMP,
    
    -- Password reset
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier, subscription_status);
CREATE INDEX idx_users_verification_token ON users(email_verification_token) WHERE email_verification_token IS NOT NULL;
CREATE INDEX idx_users_reset_token ON users(password_reset_token) WHERE password_reset_token IS NOT NULL;
CREATE INDEX idx_users_active ON users(is_active, subscription_status);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token_hash VARCHAR(255) NOT NULL,
    
    -- Session metadata
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    location_info JSONB,
    
    -- Session lifecycle
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active, expires_at);

-- Auto-cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (would be called by cron job)
```

#### User Preferences Table
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Preferences stored as JSONB for flexibility
    preferences JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_preferences_content ON user_preferences USING GIN (preferences);

-- Example preferences structure:
/*
{
  "dashboard": {
    "default_view": "recent_reports",
    "charts_per_page": 10,
    "theme": "light"
  },
  "reports": {
    "default_sections": ["executive_summary", "financials", "valuation"],
    "chart_style": "professional",
    "export_format": "pdf",
    "include_disclaimers": true
  },
  "notifications": {
    "email_reports": true,
    "price_alerts": false,
    "weekly_digest": true
  },
  "privacy": {
    "share_usage_data": false,
    "marketing_emails": true
  }
}
*/

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. Company & Financial Data Schema

#### Companies Master Table
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    
    -- SEC identifiers
    cik VARCHAR(20) UNIQUE, -- Central Index Key
    cusip VARCHAR(9),
    isin VARCHAR(12),
    
    -- Company classification
    sector VARCHAR(100),
    industry VARCHAR(100),
    sub_industry VARCHAR(100),
    gics_code VARCHAR(8),
    
    -- Company details
    market_cap BIGINT,
    employees INTEGER,
    headquarters VARCHAR(255),
    website VARCHAR(255),
    phone VARCHAR(50),
    description TEXT,
    
    -- Exchange information
    exchange VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'USD',
    country VARCHAR(2) DEFAULT 'US',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    delisted_date DATE,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_data_update TIMESTAMP
);

-- Indexes
CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_cik ON companies(cik) WHERE cik IS NOT NULL;
CREATE INDEX idx_companies_sector ON companies(sector, industry);
CREATE INDEX idx_companies_active ON companies(is_active);
CREATE INDEX idx_companies_exchange ON companies(exchange);

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### SEC Filings Table
```sql
CREATE TABLE sec_filings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Filing identification
    accession_number VARCHAR(50) UNIQUE NOT NULL,
    filing_type VARCHAR(20) NOT NULL, -- '10-K', '10-Q', '8-K', etc.
    filing_date DATE NOT NULL,
    period_end DATE,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER, -- 1-4 for quarterly filings
    
    -- Document details
    document_url VARCHAR(500),
    html_url VARCHAR(500),
    xml_url VARCHAR(500),
    file_size_bytes INTEGER,
    
    -- Content storage
    raw_content TEXT, -- Full filing text
    processed_sections JSONB, -- Extracted sections
    key_metrics JSONB, -- Extracted financial metrics
    
    -- Processing status
    processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    processing_error TEXT,
    processed_at TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_filings_company_date ON sec_filings(company_id, filing_date DESC);
CREATE INDEX idx_filings_accession ON sec_filings(accession_number);
CREATE INDEX idx_filings_type_date ON sec_filings(filing_type, filing_date DESC);
CREATE INDEX idx_filings_status ON sec_filings(processing_status);
CREATE INDEX idx_filings_period ON sec_filings(company_id, period_end DESC);

-- Partitioning by filing_date for performance (optional for large datasets)
-- CREATE TABLE sec_filings_y2024 PARTITION OF sec_filings FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TRIGGER update_sec_filings_updated_at BEFORE UPDATE ON sec_filings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Financial Statements Table
```sql
CREATE TABLE financial_statements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Statement identification
    statement_type VARCHAR(20) NOT NULL CHECK (statement_type IN ('income', 'balance', 'cashflow', 'equity')),
    period_type VARCHAR(10) NOT NULL CHECK (period_type IN ('annual', 'quarterly')),
    period_end DATE NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER, -- NULL for annual statements
    
    -- Data details
    currency VARCHAR(3) DEFAULT 'USD',
    units VARCHAR(20) DEFAULT 'USD', -- 'USD', 'thousands', 'millions'
    
    -- Financial data stored as JSONB for flexibility
    data JSONB NOT NULL,
    
    -- Data source and quality
    source VARCHAR(50) NOT NULL, -- 'sec_edgar', 'alpha_vantage', 'manual'
    data_quality_score DECIMAL(3,2), -- 0.00 to 1.00
    has_restatements BOOLEAN DEFAULT FALSE,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(company_id, statement_type, period_type, period_end)
);

-- Indexes for financial analysis queries
CREATE INDEX idx_financials_company_period ON financial_statements(company_id, period_end DESC);
CREATE INDEX idx_financials_type_period ON financial_statements(statement_type, period_type, period_end DESC);
CREATE INDEX idx_financials_fiscal ON financial_statements(company_id, fiscal_year DESC, fiscal_quarter DESC);
CREATE INDEX idx_financials_data ON financial_statements USING GIN (data);

CREATE TRIGGER update_financial_statements_updated_at BEFORE UPDATE ON financial_statements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Stock Prices Table
```sql
CREATE TABLE stock_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Price data
    price_date DATE NOT NULL,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    adjusted_close DECIMAL(12,4),
    volume BIGINT,
    
    -- Corporate actions
    dividend_amount DECIMAL(8,4),
    split_coefficient DECIMAL(8,4),
    
    -- Data source
    source VARCHAR(50) NOT NULL DEFAULT 'alpha_vantage',
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(company_id, price_date)
);

-- Indexes for price analysis
CREATE INDEX idx_prices_company_date ON stock_prices(company_id, price_date DESC);
CREATE INDEX idx_prices_date ON stock_prices(price_date DESC);
CREATE INDEX idx_prices_volume ON stock_prices(company_id, volume DESC);

-- Partitioning by date for large datasets
-- CREATE TABLE stock_prices_y2024 PARTITION OF stock_prices FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 3. Report Management Schema

#### Reports Table
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id),
    
    -- Report metadata
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) DEFAULT 'comprehensive' CHECK (report_type IN ('comprehensive', 'quick', 'custom', 'update')),
    
    -- Generation tracking
    status VARCHAR(20) DEFAULT 'generating' CHECK (status IN ('generating', 'completed', 'failed', 'cancelled')),
    generation_started_at TIMESTAMP DEFAULT NOW(),
    generation_completed_at TIMESTAMP,
    generation_time_seconds INTEGER,
    generation_error TEXT,
    
    -- Report content (stored as JSONB for flexibility)
    executive_summary JSONB,
    company_analysis JSONB,
    financial_analysis JSONB,
    market_analysis JSONB,
    valuation_analysis JSONB,
    risk_analysis JSONB,
    charts_data JSONB,
    
    -- Report metadata
    data_sources JSONB, -- Track which APIs/sources were used
    kiro_prompts_used JSONB, -- Track which Kiro prompts were executed
    rag_context_used JSONB, -- Track RAG context that was used
    
    -- Report statistics
    page_count INTEGER,
    word_count INTEGER,
    chart_count INTEGER,
    
    -- File storage
    pdf_file_path VARCHAR(500), -- S3 path to PDF
    pdf_file_size INTEGER,
    
    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    share_token VARCHAR(64) UNIQUE,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for user dashboard and search
CREATE INDEX idx_reports_user_date ON reports(user_id, created_at DESC);
CREATE INDEX idx_reports_company ON reports(company_id, created_at DESC);
CREATE INDEX idx_reports_status ON reports(status, generation_started_at);
CREATE INDEX idx_reports_share_token ON reports(share_token) WHERE share_token IS NOT NULL;
CREATE INDEX idx_reports_public ON reports(is_public, created_at DESC) WHERE is_public = TRUE;

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Report Shares Table
```sql
CREATE TABLE report_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    shared_by_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Share configuration
    share_token VARCHAR(64) UNIQUE NOT NULL,
    access_type VARCHAR(20) DEFAULT 'view' CHECK (access_type IN ('view', 'download', 'full')),
    password_hash VARCHAR(255), -- Optional password protection
    
    -- Access control
    expires_at TIMESTAMP,
    max_access_count INTEGER,
    allowed_domains TEXT[], -- Array of allowed domains
    
    -- Usage tracking
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    last_accessed_ip INET,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_shares_token ON report_shares(share_token);
CREATE INDEX idx_shares_report ON report_shares(report_id);
CREATE INDEX idx_shares_user ON report_shares(shared_by_user_id);
CREATE INDEX idx_shares_expires ON report_shares(expires_at) WHERE expires_at IS NOT NULL;
```

### 4. User Activity & Analytics Schema

#### User Activity Log
```sql
CREATE TABLE user_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Activity details
    activity_type VARCHAR(50) NOT NULL, -- 'login', 'report_generated', 'report_viewed', 'report_downloaded', etc.
    resource_type VARCHAR(50), -- 'report', 'company', 'user_profile'
    resource_id UUID,
    
    -- Activity metadata
    metadata JSONB,
    
    -- Request details
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    
    -- Timing
    duration_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX idx_activity_user_date ON user_activity_log(user_id, created_at DESC);
CREATE INDEX idx_activity_type_date ON user_activity_log(activity_type, created_at DESC);
CREATE INDEX idx_activity_resource ON user_activity_log(resource_type, resource_id);

-- Partitioning by date for large datasets
-- CREATE TABLE user_activity_log_y2024 PARTITION OF user_activity_log FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

#### Usage Tracking Table
```sql
CREATE TABLE user_usage_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Usage metrics
    usage_type VARCHAR(50) NOT NULL, -- 'report_generation', 'storage_used', 'api_calls'
    usage_amount INTEGER NOT NULL,
    usage_date DATE NOT NULL,
    
    -- Usage context
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, usage_type, usage_date)
);

-- Indexes for usage analysis
CREATE INDEX idx_usage_user_date ON user_usage_tracking(user_id, usage_date DESC);
CREATE INDEX idx_usage_type_date ON user_usage_tracking(usage_type, usage_date DESC);
```

### 5. System Configuration & Monitoring

#### System Configuration Table
```sql
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_config_key ON system_config(config_key);
CREATE INDEX idx_config_active ON system_config(is_active);

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### Error Logs Table
```sql
CREATE TABLE error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Error details
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    
    -- Context
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    request_id UUID,
    endpoint VARCHAR(255),
    http_method VARCHAR(10),
    
    -- Request details
    ip_address INET,
    user_agent TEXT,
    request_body JSONB,
    
    -- System state
    server_instance VARCHAR(100),
    memory_usage_mb INTEGER,
    cpu_usage_percent DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_errors_type_date ON error_logs(error_type, created_at DESC);
CREATE INDEX idx_errors_user ON error_logs(user_id, created_at DESC);
CREATE INDEX idx_errors_date ON error_logs(created_at DESC);
```

## Database Views for Common Queries

### User Dashboard View
```sql
CREATE VIEW user_dashboard_view AS
SELECT 
    u.id as user_id,
    u.email,
    u.first_name,
    u.last_name,
    u.subscription_tier,
    u.subscription_expires_at,
    
    -- Report statistics
    COUNT(r.id) as total_reports,
    COUNT(CASE WHEN r.created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as reports_last_30_days,
    MAX(r.created_at) as last_report_date,
    
    -- Usage statistics
    COALESCE(SUM(CASE WHEN ut.usage_type = 'report_generation' AND ut.usage_date >= DATE_TRUNC('month', NOW()) THEN ut.usage_amount END), 0) as reports_this_month,
    
    u.created_at as member_since
FROM users u
LEFT JOIN reports r ON u.id = r.user_id AND r.status = 'completed'
LEFT JOIN user_usage_tracking ut ON u.id = ut.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.email, u.first_name, u.last_name, u.subscription_tier, u.subscription_expires_at, u.created_at;
```

### Company Financial Summary View
```sql
CREATE VIEW company_financial_summary AS
SELECT 
    c.id as company_id,
    c.ticker,
    c.company_name,
    c.sector,
    c.industry,
    c.market_cap,
    
    -- Latest financial data
    fs_income.data->>'revenue' as latest_revenue,
    fs_income.data->>'net_income' as latest_net_income,
    fs_income.period_end as latest_financial_date,
    
    -- Latest stock price
    sp.close_price as latest_stock_price,
    sp.price_date as latest_price_date,
    
    -- Report count
    COUNT(r.id) as total_reports_generated
    
FROM companies c
LEFT JOIN financial_statements fs_income ON c.id = fs_income.company_id 
    AND fs_income.statement_type = 'income' 
    AND fs_income.period_end = (
        SELECT MAX(period_end) 
        FROM financial_statements 
        WHERE company_id = c.id AND statement_type = 'income'
    )
LEFT JOIN stock_prices sp ON c.id = sp.company_id 
    AND sp.price_date = (
        SELECT MAX(price_date) 
        FROM stock_prices 
        WHERE company_id = c.id
    )
LEFT JOIN reports r ON c.id = r.company_id AND r.status = 'completed'
WHERE c.is_active = TRUE
GROUP BY c.id, c.ticker, c.company_name, c.sector, c.industry, c.market_cap, 
         fs_income.data, fs_income.period_end, sp.close_price, sp.price_date;
```

## Database Maintenance & Performance

### Automated Cleanup Procedures
```sql
-- Clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    -- Remove expired sessions
    DELETE FROM user_sessions WHERE expires_at < NOW();
    
    -- Remove expired password reset tokens
    UPDATE users SET 
        password_reset_token = NULL,
        password_reset_expires = NULL
    WHERE password_reset_expires < NOW();
    
    -- Remove expired email verification tokens
    UPDATE users SET 
        email_verification_token = NULL,
        email_verification_expires = NULL
    WHERE email_verification_expires < NOW();
    
    -- Archive old activity logs (older than 1 year)
    DELETE FROM user_activity_log WHERE created_at < NOW() - INTERVAL '1 year';
    
    -- Archive old error logs (older than 6 months)
    DELETE FROM error_logs WHERE created_at < NOW() - INTERVAL '6 months';
    
END;
$$ LANGUAGE plpgsql;

-- Schedule this to run daily via cron or pg_cron extension
```

### Performance Monitoring Queries
```sql
-- Monitor table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Monitor slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

*Last Updated: 2026-01-22*
