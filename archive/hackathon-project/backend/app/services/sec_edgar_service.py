"""
SEC EDGAR Service - SEC filings and regulatory data
"""

import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import re

class SECEdgarService:
    def __init__(self):
        self.base_url = "https://data.sec.gov"
        self.headers = {
            'User-Agent': 'MarketMind Pro research@marketmind.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
    
    async def get_latest_filings(self, ticker: str) -> Dict[str, Any]:
        """Get latest SEC filings for comprehensive analysis"""
        try:
            # Get company CIK first
            cik = await self._get_company_cik(ticker)
            if not cik:
                return {'error': f'Could not find CIK for {ticker}'}
            
            # Get recent filings
            filings = await self._get_company_filings(cik)
            
            # Process key filing types
            processed_filings = {
                '10-K': await self._process_10k_filings(filings),
                '10-Q': await self._process_10q_filings(filings),
                '8-K': await self._process_8k_filings(filings),
                'DEF 14A': await self._process_proxy_filings(filings)
            }
            
            return {
                'cik': cik,
                'ticker': ticker,
                'filings': processed_filings,
                'filing_summary': self._create_filing_summary(processed_filings),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_company_cik(self, ticker: str) -> Optional[str]:
        """Get company CIK from ticker"""
        try:
            url = f"{self.base_url}/submissions/CIK{ticker.upper()}.json"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('cik')
                    
                    # Try company tickers endpoint
                    tickers_url = f"{self.base_url}/files/company_tickers.json"
                    async with session.get(tickers_url) as ticker_response:
                        if ticker_response.status == 200:
                            tickers_data = await ticker_response.json()
                            for company in tickers_data.values():
                                if company.get('ticker') == ticker.upper():
                                    return str(company.get('cik_str')).zfill(10)
            return None
        except:
            return None
    
    async def _get_company_filings(self, cik: str) -> List[Dict]:
        """Get company filings from SEC"""
        try:
            url = f"{self.base_url}/submissions/CIK{cik.zfill(10)}.json"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        recent_filings = data.get('filings', {}).get('recent', {})
                        
                        # Convert to list of filing dictionaries
                        filings = []
                        forms = recent_filings.get('form', [])
                        filing_dates = recent_filings.get('filingDate', [])
                        accession_numbers = recent_filings.get('accessionNumber', [])
                        
                        for i in range(min(len(forms), 50)):  # Last 50 filings
                            filings.append({
                                'form': forms[i],
                                'filing_date': filing_dates[i],
                                'accession_number': accession_numbers[i]
                            })
                        
                        return filings
            return []
        except:
            return []
    
    async def _process_10k_filings(self, filings: List[Dict]) -> List[Dict]:
        """Process 10-K annual reports"""
        ten_k_filings = [f for f in filings if f['form'] == '10-K'][:2]  # Last 2 years
        
        processed = []
        for filing in ten_k_filings:
            processed.append({
                'form': filing['form'],
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'key_sections': {
                    'business_overview': 'Item 1. Business',
                    'risk_factors': 'Item 1A. Risk Factors',
                    'financial_statements': 'Item 8. Financial Statements',
                    'management_discussion': 'Item 7. Management Discussion'
                }
            })
        
        return processed
    
    async def _process_10q_filings(self, filings: List[Dict]) -> List[Dict]:
        """Process 10-Q quarterly reports"""
        ten_q_filings = [f for f in filings if f['form'] == '10-Q'][:4]  # Last 4 quarters
        
        processed = []
        for filing in ten_q_filings:
            processed.append({
                'form': filing['form'],
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'quarter': self._determine_quarter(filing['filing_date'])
            })
        
        return processed
    
    async def _process_8k_filings(self, filings: List[Dict]) -> List[Dict]:
        """Process 8-K current reports (material events)"""
        eight_k_filings = [f for f in filings if f['form'] == '8-K'][:10]  # Last 10 events
        
        processed = []
        for filing in eight_k_filings:
            processed.append({
                'form': filing['form'],
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'event_type': 'Material Event'  # Would parse actual event type
            })
        
        return processed
    
    async def _process_proxy_filings(self, filings: List[Dict]) -> List[Dict]:
        """Process DEF 14A proxy statements"""
        proxy_filings = [f for f in filings if 'DEF 14A' in f['form']][:2]
        
        processed = []
        for filing in proxy_filings:
            processed.append({
                'form': filing['form'],
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'content_type': 'Proxy Statement'
            })
        
        return processed
    
    def _determine_quarter(self, filing_date: str) -> str:
        """Determine quarter from filing date"""
        try:
            date = datetime.strptime(filing_date, '%Y-%m-%d')
            month = date.month
            year = date.year
            
            if month <= 3:
                return f"Q1 {year}"
            elif month <= 6:
                return f"Q2 {year}"
            elif month <= 9:
                return f"Q3 {year}"
            else:
                return f"Q4 {year}"
        except:
            return "Unknown"
    
    def _create_filing_summary(self, processed_filings: Dict) -> Dict[str, Any]:
        """Create summary of filing activity"""
        summary = {
            'total_filings': 0,
            'recent_10k_count': len(processed_filings.get('10-K', [])),
            'recent_10q_count': len(processed_filings.get('10-Q', [])),
            'recent_8k_count': len(processed_filings.get('8-K', [])),
            'last_annual_report': None,
            'last_quarterly_report': None
        }
        
        # Get most recent filing dates
        if processed_filings.get('10-K'):
            summary['last_annual_report'] = processed_filings['10-K'][0]['filing_date']
        
        if processed_filings.get('10-Q'):
            summary['last_quarterly_report'] = processed_filings['10-Q'][0]['filing_date']
        
        summary['total_filings'] = sum(len(filings) for filings in processed_filings.values())
        
        return summary