# Data Storage & Management System

## Storage Architecture Overview

### Multi-Tier Storage Strategy
```
User Data (PostgreSQL) → Raw Financial Data (PostgreSQL) → Processed Reports (PostgreSQL + S3) → Cache (Redis)
```

## Database Schema Design

### Core Financial Data Storage

#### Companies Master Table
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    cik VARCHAR(20) UNIQUE, -- SEC Central Index Key
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    employees INTEGER,
    headquarters VARCHAR(255),
    website VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_cik ON companies(cik);
CREATE INDEX idx_companies_sector ON companies(sector, industry);
```

#### SEC Filings Storage
```sql
CREATE TABLE sec_filings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    filing_type VARCHAR(20) NOT NULL, -- '10-K', '10-Q', '8-K', etc.
    filing_date DATE NOT NULL,
    period_end DATE,
    accession_number VARCHAR(50) UNIQUE NOT NULL,
    document_url VARCHAR(500),
    raw_data JSONB, -- Full SEC filing data
    processed_data JSONB, -- Extracted key metrics
    file_size_bytes INTEGER,
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX idx_filings_company_date ON sec_filings(company_id, filing_date DESC);
CREATE INDEX idx_filings_type ON sec_filings(filing_type, filing_date DESC);
CREATE INDEX idx_filings_accession ON sec_filings(accession_number);
CREATE INDEX idx_filings_status ON sec_filings(processing_status);
```

#### Financial Statements Storage
```sql
CREATE TABLE financial_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    statement_type VARCHAR(20) NOT NULL, -- 'income', 'balance', 'cashflow'
    period_type VARCHAR(10) NOT NULL, -- 'annual', 'quarterly'
    period_end DATE NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER, -- NULL for annual
    currency VARCHAR(3) DEFAULT 'USD',
    data JSONB NOT NULL, -- Structured financial data
    source VARCHAR(50) NOT NULL, -- 'sec_edgar', 'alpha_vantage', etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(company_id, statement_type, period_type, period_end)
);

-- Indexes for financial analysis queries
CREATE INDEX idx_financials_company_period ON financial_statements(company_id, period_end DESC);
CREATE INDEX idx_financials_type_period ON financial_statements(statement_type, period_type, period_end DESC);
```

#### Stock Price Data
```sql
CREATE TABLE stock_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    price_date DATE NOT NULL,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    adjusted_close DECIMAL(12,4),
    volume BIGINT,
    dividend_amount DECIMAL(8,4),
    split_coefficient DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(company_id, price_date)
);

-- Partitioning by date for performance
CREATE INDEX idx_prices_company_date ON stock_prices(company_id, price_date DESC);
CREATE INDEX idx_prices_date ON stock_prices(price_date DESC);
```

### Report Storage System

#### Generated Reports Table
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id),
    report_type VARCHAR(50) DEFAULT 'comprehensive', -- 'comprehensive', 'quick', 'custom'
    title VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'generating', -- 'generating', 'completed', 'failed'
    generation_started_at TIMESTAMP DEFAULT NOW(),
    generation_completed_at TIMESTAMP,
    generation_time_seconds INTEGER,
    
    -- Report content
    executive_summary JSONB,
    company_analysis JSONB,
    financial_analysis JSONB,
    market_analysis JSONB,
    valuation_analysis JSONB,
    risk_analysis JSONB,
    charts_data JSONB,
    
    -- Metadata
    data_sources JSONB, -- Track which APIs/sources were used
    kiro_prompts_used JSONB, -- Track which Kiro prompts were executed
    page_count INTEGER,
    word_count INTEGER,
    
    -- File storage
    pdf_file_path VARCHAR(500), -- S3 path to PDF
    pdf_file_size INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for user dashboard and search
CREATE INDEX idx_reports_user_date ON reports(user_id, created_at DESC);
CREATE INDEX idx_reports_company ON reports(company_id, created_at DESC);
CREATE INDEX idx_reports_status ON reports(status, generation_started_at);
```

#### Report Sharing & Access
```sql
CREATE TABLE report_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
    shared_by_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    share_token VARCHAR(64) UNIQUE NOT NULL,
    access_type VARCHAR(20) DEFAULT 'view', -- 'view', 'download'
    password_hash VARCHAR(255), -- Optional password protection
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_shares_token ON report_shares(share_token);
CREATE INDEX idx_shares_report ON report_shares(report_id);
```

### User Data Storage

#### User Report History
```sql
CREATE TABLE user_report_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- 'generated', 'viewed', 'downloaded', 'shared'
    metadata JSONB, -- Additional context about the action
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_history_user_date ON user_report_history(user_id, created_at DESC);
CREATE INDEX idx_history_report ON user_report_history(report_id, created_at DESC);
```

#### User Watchlists
```sql
CREATE TABLE user_watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE watchlist_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id UUID REFERENCES user_watchlists(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    
    UNIQUE(watchlist_id, company_id)
);

CREATE INDEX idx_watchlist_user ON user_watchlists(user_id);
CREATE INDEX idx_watchlist_companies ON watchlist_companies(watchlist_id);
```

## File Storage Strategy

### S3 Storage Structure
```
marketmind-pro-storage/
├── reports/
│   ├── {user_id}/
│   │   ├── {report_id}/
│   │   │   ├── report.pdf
│   │   │   ├── charts/
│   │   │   │   ├── revenue_chart.png
│   │   │   │   ├── valuation_chart.png
│   │   │   │   └── ...
│   │   │   └── raw_data/
│   │   │       ├── sec_filings.json
│   │   │       └── financial_data.json
├── temp/
│   └── {session_id}/
│       └── processing_files/
└── public/
    ├── company_logos/
    └── templates/
```

### File Management Service
```python
import boto3
from botocore.exceptions import ClientError
import os

class S3FileManager:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
    
    async def upload_report_pdf(self, user_id: str, report_id: str, pdf_content: bytes) -> str:
        """Upload generated PDF report to S3"""
        key = f"reports/{user_id}/{report_id}/report.pdf"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=pdf_content,
                ContentType='application/pdf',
                ServerSideEncryption='AES256'
            )
            return f"s3://{self.bucket_name}/{key}"
        except ClientError as e:
            raise Exception(f"Failed to upload PDF: {e}")
    
    async def upload_chart_image(self, user_id: str, report_id: str, chart_name: str, image_content: bytes) -> str:
        """Upload chart image to S3"""
        key = f"reports/{user_id}/{report_id}/charts/{chart_name}.png"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_content,
                ContentType='image/png',
                ServerSideEncryption='AES256'
            )
            return f"s3://{self.bucket_name}/{key}"
        except ClientError as e:
            raise Exception(f"Failed to upload chart: {e}")
    
    async def get_signed_url(self, s3_path: str, expiration: int = 3600) -> str:
        """Generate signed URL for secure file access"""
        key = s3_path.replace(f"s3://{self.bucket_name}/", "")
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate signed URL: {e}")
```

## Caching Strategy

### Redis Cache Structure
```python
import redis
import json
from typing import Optional, Dict, Any

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
    
    # Company data caching
    async def cache_company_data(self, ticker: str, data: Dict[Any, Any], ttl: int = 3600):
        """Cache company financial data"""
        key = f"company_data:{ticker}"
        self.redis_client.setex(key, ttl, json.dumps(data))
    
    async def get_cached_company_data(self, ticker: str) -> Optional[Dict[Any, Any]]:
        """Retrieve cached company data"""
        key = f"company_data:{ticker}"
        cached = self.redis_client.get(key)
        return json.loads(cached) if cached else None
    
    # Report caching
    async def cache_report_progress(self, report_id: str, progress: Dict[Any, Any]):
        """Cache report generation progress"""
        key = f"report_progress:{report_id}"
        self.redis_client.setex(key, 1800, json.dumps(progress))  # 30 min TTL
    
    # Kiro prompt result caching
    async def cache_kiro_result(self, prompt_hash: str, result: Dict[Any, Any], ttl: int = 7200):
        """Cache Kiro prompt results for reuse"""
        key = f"kiro_result:{prompt_hash}"
        self.redis_client.setex(key, ttl, json.dumps(result))
    
    # User session caching
    async def cache_user_session(self, session_id: str, user_data: Dict[Any, Any], ttl: int = 3600):
        """Cache user session data"""
        key = f"user_session:{session_id}"
        self.redis_client.setex(key, ttl, json.dumps(user_data))
```

## Data Backup & Recovery

### Automated Backup Strategy
```python
import subprocess
from datetime import datetime

class BackupManager:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.s3_backup_bucket = os.getenv('S3_BACKUP_BUCKET')
    
    async def create_database_backup(self):
        """Create PostgreSQL database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"marketmind_backup_{timestamp}.sql"
        
        # Create pg_dump backup
        dump_command = [
            'pg_dump',
            f'--host={self.db_host}',
            f'--username={self.db_user}',
            f'--dbname={self.db_name}',
            '--no-password',
            '--format=custom',
            '--compress=9',
            f'--file={backup_filename}'
        ]
        
        subprocess.run(dump_command, check=True)
        
        # Upload to S3
        s3_key = f"database_backups/{backup_filename}"
        await self.upload_to_s3(backup_filename, s3_key)
        
        # Clean up local file
        os.remove(backup_filename)
        
        return s3_key
    
    async def schedule_backups(self):
        """Schedule automated backups"""
        # Daily database backups
        # Weekly full system backups
        # Monthly archive backups
        pass
```

## Data Privacy & Compliance

### GDPR Compliance
```python
class DataPrivacyManager:
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        user_data = {
            'profile': await self.get_user_profile(user_id),
            'reports': await self.get_user_reports(user_id),
            'usage_history': await self.get_usage_history(user_id),
            'preferences': await self.get_user_preferences(user_id)
        }
        return user_data
    
    async def delete_user_data(self, user_id: str):
        """Permanently delete all user data"""
        # Delete from all tables
        # Remove S3 files
        # Clear cache entries
        # Log deletion for audit
        pass
    
    async def anonymize_user_data(self, user_id: str):
        """Anonymize user data while preserving analytics"""
        # Replace PII with anonymous identifiers
        # Maintain data relationships for analytics
        pass
```

*Last Updated: 2026-01-22*
