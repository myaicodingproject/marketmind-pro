import yfinance as yf
import requests
import asyncio
import asyncpg
from typing import Dict, List, Optional
from datetime import datetime
import json

class DataCollector:
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.sec_headers = {'User-Agent': 'MarketMind Pro research@marketmind.com'}
    
    async def collect_company_data(self, ticker: str) -> Dict:
        """Collect comprehensive company data from multiple sources"""
        yahoo_data = await self._get_yahoo_data(ticker)
        sec_data = await self._get_sec_data(ticker)
        
        company_data = {
            'ticker': ticker.upper(),
            'name': yahoo_data.get('longName', ''),
            'sector': yahoo_data.get('sector', ''),
            'industry': yahoo_data.get('industry', ''),
            'market_cap': yahoo_data.get('marketCap'),
            'employees': yahoo_data.get('fullTimeEmployees'),
            'headquarters': f"{yahoo_data.get('city', '')}, {yahoo_data.get('state', '')}",
            'revenue': yahoo_data.get('totalRevenue'),
            'net_income': yahoo_data.get('netIncomeToCommon'),
            'total_assets': yahoo_data.get('totalAssets'),
            'total_debt': yahoo_data.get('totalDebt'),
            'cash': yahoo_data.get('totalCash'),
            'pe_ratio': yahoo_data.get('trailingPE'),
            'pb_ratio': yahoo_data.get('priceToBook'),
            'roe': yahoo_data.get('returnOnEquity')
        }
        
        await self._store_company_data(company_data)
        return company_data
    
    async def collect_market_data(self, ticker: str) -> Dict:
        """Collect market and competitive data"""
        yahoo_data = await self._get_yahoo_data(ticker)
        competitors = await self._get_competitors(ticker)
        
        market_data = {
            'ticker': ticker.upper(),
            'competitors': json.dumps(competitors),
            'current_price': yahoo_data.get('currentPrice'),
            'day_change': yahoo_data.get('regularMarketChangePercent'),
            'volume': yahoo_data.get('volume'),
            'avg_volume': yahoo_data.get('averageVolume'),
            'analyst_rating': yahoo_data.get('recommendationKey'),
            'price_target': yahoo_data.get('targetMeanPrice')
        }
        
        await self._store_market_data(market_data)
        return market_data
    
    async def _get_yahoo_data(self, ticker: str) -> Dict:
        """Fetch data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info
        except Exception as e:
            print(f"Yahoo Finance error for {ticker}: {e}")
            return {}
    
    async def _get_sec_data(self, ticker: str) -> Dict:
        """Fetch SEC filing data"""
        try:
            url = f"https://data.sec.gov/submissions/CIK{await self._get_cik(ticker)}.json"
            response = requests.get(url, headers=self.sec_headers)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            print(f"SEC data error for {ticker}: {e}")
            return {}
    
    async def _get_cik(self, ticker: str) -> str:
        """Get CIK number for SEC filings"""
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.sec_headers)
            data = response.json()
            
            for entry in data.values():
                if entry['ticker'].upper() == ticker.upper():
                    return str(entry['cik_str']).zfill(10)
            return ""
        except:
            return ""
    
    async def _get_competitors(self, ticker: str) -> List[str]:
        """Get competitor list (simplified implementation)"""
        # This would typically use industry classification APIs
        # For now, return empty list - can be enhanced with real competitor data
        return []
    
    async def _store_company_data(self, data: Dict):
        """Store company data in database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO company_data (ticker, name, sector, industry, market_cap, 
                                        employees, headquarters, revenue, net_income, 
                                        total_assets, total_debt, cash, pe_ratio, pb_ratio, roe)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (ticker) DO UPDATE SET
                    name = EXCLUDED.name,
                    sector = EXCLUDED.sector,
                    industry = EXCLUDED.industry,
                    market_cap = EXCLUDED.market_cap,
                    employees = EXCLUDED.employees,
                    headquarters = EXCLUDED.headquarters,
                    revenue = EXCLUDED.revenue,
                    net_income = EXCLUDED.net_income,
                    total_assets = EXCLUDED.total_assets,
                    total_debt = EXCLUDED.total_debt,
                    cash = EXCLUDED.cash,
                    pe_ratio = EXCLUDED.pe_ratio,
                    pb_ratio = EXCLUDED.pb_ratio,
                    roe = EXCLUDED.roe,
                    last_updated = CURRENT_TIMESTAMP
            """, *[data.get(k) for k in ['ticker', 'name', 'sector', 'industry', 'market_cap',
                                       'employees', 'headquarters', 'revenue', 'net_income',
                                       'total_assets', 'total_debt', 'cash', 'pe_ratio', 'pb_ratio', 'roe']])
    
    async def _store_market_data(self, data: Dict):
        """Store market data in database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO market_data (ticker, competitors, current_price, day_change,
                                       volume, avg_volume, analyst_rating, price_target)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (ticker) DO UPDATE SET
                    competitors = EXCLUDED.competitors,
                    current_price = EXCLUDED.current_price,
                    day_change = EXCLUDED.day_change,
                    volume = EXCLUDED.volume,
                    avg_volume = EXCLUDED.avg_volume,
                    analyst_rating = EXCLUDED.analyst_rating,
                    price_target = EXCLUDED.price_target,
                    last_updated = CURRENT_TIMESTAMP
            """, *[data.get(k) for k in ['ticker', 'competitors', 'current_price', 'day_change',
                                       'volume', 'avg_volume', 'analyst_rating', 'price_target']])

class DataValidator:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def validate_data_consistency(self, ticker: str) -> List[Dict]:
        """Run consistency checks on collected data"""
        checks = []
        
        async with self.db_pool.acquire() as conn:
            # Check if basic data exists
            company = await conn.fetchrow("SELECT * FROM company_data WHERE ticker = $1", ticker)
            market = await conn.fetchrow("SELECT * FROM market_data WHERE ticker = $1", ticker)
            
            if not company:
                checks.append(self._create_check(ticker, "company_data_missing", "failed", 
                                               {"message": "Company data not found"}))
            
            if not market:
                checks.append(self._create_check(ticker, "market_data_missing", "failed",
                                               {"message": "Market data not found"}))
            
            # Validate financial ratios
            if company and company['pe_ratio'] and (company['pe_ratio'] < 0 or company['pe_ratio'] > 1000):
                checks.append(self._create_check(ticker, "pe_ratio_outlier", "warning",
                                               {"pe_ratio": float(company['pe_ratio'])}))
            
            # Store validation results
            for check in checks:
                await self._store_check(conn, check)
        
        return checks
    
    def _create_check(self, ticker: str, check_type: str, status: str, details: Dict) -> Dict:
        return {
            'ticker': ticker,
            'check_type': check_type,
            'status': status,
            'details': json.dumps(details)
        }
    
    async def _store_check(self, conn, check: Dict):
        await conn.execute("""
            INSERT INTO consistency_checks (ticker, check_type, status, details)
            VALUES ($1, $2, $3, $4)
        """, check['ticker'], check['check_type'], check['status'], check['details'])

# Usage example
async def main():
    db_pool = await asyncpg.create_pool("postgresql://user:pass@localhost/marketmind_pro")
    
    collector = DataCollector(db_pool)
    validator = DataValidator(db_pool)
    
    # Collect data for a ticker
    ticker = "AAPL"
    await collector.collect_company_data(ticker)
    await collector.collect_market_data(ticker)
    
    # Validate data consistency
    checks = await validator.validate_data_consistency(ticker)
    print(f"Validation checks: {len(checks)} issues found")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(main())