"""
SEC EDGAR Service - Real regulatory filings integration
"""
import asyncio
import logging
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
import pandas as pd
from sec_edgar_downloader import Downloader
from ..core.config import settings

logger = logging.getLogger(__name__)

class SECEdgarService:
    def __init__(self):
        self.user_agent = settings.SEC_EDGAR_USER_AGENT
        self.base_url = "https://data.sec.gov"
        self.session = None
        self.downloader = Downloader("MarketMind", "info@marketmind.com")
        
    async def _get_session(self):
        if not self.session:
            headers = {
                'User-Agent': self.user_agent,
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'data.sec.gov'
            }
            self.session = httpx.AsyncClient(headers=headers, timeout=30.0)
        return self.session
    
    async def get_company_cik(self, symbol: str) -> Optional[str]:
        """Get CIK (Central Index Key) for a company symbol"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/submissions/CIK{symbol.zfill(10)}.json"
            
            # Try direct CIK lookup first
            try:
                response = await session.get(url)
                if response.status_code == 200:
                    return symbol.zfill(10)
            except:
                pass
            
            # Search by ticker symbol
            tickers_url = f"{self.base_url}/files/company_tickers.json"
            response = await session.get(tickers_url)
            response.raise_for_status()
            
            tickers_data = response.json()
            for entry in tickers_data.values():
                if entry.get('ticker', '').upper() == symbol.upper():
                    return str(entry['cik_str']).zfill(10)
            
            return None
        except Exception as e:
            logger.error(f"Error getting CIK for {symbol}: {e}")
            return None

    async def get_company_submissions(self, symbol: str) -> Dict:
        """Get all submissions for a company"""
        try:
            cik = await self.get_company_cik(symbol)
            if not cik:
                raise ValueError(f"Could not find CIK for symbol {symbol}")
            
            session = await self._get_session()
            url = f"{self.base_url}/submissions/CIK{cik}.json"
            
            response = await session.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting submissions for {symbol}: {e}")
            raise

    async def get_recent_filings(self, symbol: str, filing_types: List[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent filings for a company"""
        if filing_types is None:
            filing_types = ['10-K', '10-Q', '8-K', 'DEF 14A']
        
        try:
            submissions = await self.get_company_submissions(symbol)
            recent_filings = submissions.get('filings', {}).get('recent', {})
            
            filings = []
            forms = recent_filings.get('form', [])
            filing_dates = recent_filings.get('filingDate', [])
            accession_numbers = recent_filings.get('accessionNumber', [])
            primary_documents = recent_filings.get('primaryDocument', [])
            
            for i, form in enumerate(forms[:limit * 3]):  # Get more to filter
                if form in filing_types and len(filings) < limit:
                    filing = {
                        'symbol': symbol,
                        'form': form,
                        'filing_date': filing_dates[i] if i < len(filing_dates) else None,
                        'accession_number': accession_numbers[i] if i < len(accession_numbers) else None,
                        'primary_document': primary_documents[i] if i < len(primary_documents) else None,
                        'url': self._build_filing_url(accession_numbers[i], primary_documents[i]) if i < len(accession_numbers) and i < len(primary_documents) else None
                    }
                    filings.append(filing)
            
            return filings
        except Exception as e:
            logger.error(f"Error getting recent filings for {symbol}: {e}")
            return []

    async def get_filing_content(self, accession_number: str, primary_document: str) -> str:
        """Get the content of a specific filing"""
        try:
            session = await self._get_session()
            url = self._build_filing_url(accession_number, primary_document)
            
            response = await session.get(url)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            logger.error(f"Error getting filing content: {e}")
            return ""

    async def parse_10k_filing(self, symbol: str) -> Dict:
        """Parse the most recent 10-K filing for key information"""
        try:
            filings = await self.get_recent_filings(symbol, ['10-K'], 1)
            if not filings:
                return {}
            
            filing = filings[0]
            content = await self.get_filing_content(
                filing['accession_number'], 
                filing['primary_document']
            )
            
            if not content:
                return {}
            
            # Parse HTML content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract key sections
            parsed_data = {
                'symbol': symbol,
                'filing_date': filing['filing_date'],
                'accession_number': filing['accession_number'],
                'business_overview': self._extract_business_section(soup),
                'risk_factors': self._extract_risk_factors(soup),
                'financial_highlights': self._extract_financial_highlights(soup),
                'management_discussion': self._extract_md_a(soup)
            }
            
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing 10-K for {symbol}: {e}")
            return {}

    async def get_financial_statements(self, symbol: str) -> Dict:
        """Extract financial statements from recent filings"""
        try:
            filings = await self.get_recent_filings(symbol, ['10-K', '10-Q'], 5)
            
            financial_data = {
                'symbol': symbol,
                'statements': [],
                'last_updated': datetime.now().isoformat()
            }
            
            for filing in filings:
                content = await self.get_filing_content(
                    filing['accession_number'], 
                    filing['primary_document']
                )
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    statements = self._extract_financial_tables(soup)
                    
                    financial_data['statements'].append({
                        'filing_date': filing['filing_date'],
                        'form_type': filing['form'],
                        'statements': statements
                    })
            
            return financial_data
        except Exception as e:
            logger.error(f"Error getting financial statements for {symbol}: {e}")
            return {}

    def _build_filing_url(self, accession_number: str, primary_document: str) -> str:
        """Build URL for accessing filing document"""
        accession_clean = accession_number.replace('-', '')
        return f"{self.base_url}/Archives/edgar/data/{accession_clean[:10]}/{accession_number}/{primary_document}"

    def _extract_business_section(self, soup: BeautifulSoup) -> str:
        """Extract business overview section from 10-K"""
        # Look for Item 1 - Business
        business_patterns = [
            'item 1', 'item1', 'business', 'our business',
            'item 1 business', 'item 1. business'
        ]
        
        for pattern in business_patterns:
            elements = soup.find_all(text=lambda text: text and pattern in text.lower())
            if elements:
                # Get the parent element and extract surrounding text
                for element in elements:
                    parent = element.parent
                    if parent:
                        # Extract next few paragraphs
                        text_content = []
                        current = parent.next_sibling
                        count = 0
                        while current and count < 10:
                            if hasattr(current, 'get_text'):
                                text = current.get_text().strip()
                                if text and len(text) > 50:
                                    text_content.append(text)
                                    count += 1
                            current = current.next_sibling
                        
                        if text_content:
                            return ' '.join(text_content)[:2000]  # Limit length
        
        return ""

    def _extract_risk_factors(self, soup: BeautifulSoup) -> List[str]:
        """Extract risk factors from 10-K"""
        risk_patterns = [
            'risk factors', 'item 1a', 'item1a', 'risks',
            'item 1a risk factors', 'item 1a. risk factors'
        ]
        
        risks = []
        for pattern in risk_patterns:
            elements = soup.find_all(text=lambda text: text and pattern in text.lower())
            if elements:
                for element in elements:
                    parent = element.parent
                    if parent:
                        # Look for bullet points or numbered lists
                        risk_items = parent.find_all(['li', 'p'])
                        for item in risk_items[:10]:  # Limit to first 10 risks
                            text = item.get_text().strip()
                            if len(text) > 100:  # Only substantial risk descriptions
                                risks.append(text[:500])  # Limit length
                        
                        if risks:
                            break
        
        return risks

    def _extract_financial_highlights(self, soup: BeautifulSoup) -> Dict:
        """Extract key financial metrics from filing"""
        # This is a simplified extraction - in production you'd use more sophisticated parsing
        highlights = {}
        
        # Look for common financial terms in tables
        financial_terms = [
            'revenue', 'net income', 'total assets', 'stockholders equity',
            'cash and cash equivalents', 'total debt'
        ]
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text().strip().lower()
                    for term in financial_terms:
                        if term in label:
                            try:
                                value = cells[1].get_text().strip()
                                # Clean up the value (remove $ and commas)
                                value = value.replace('$', '').replace(',', '').replace('(', '-').replace(')', '')
                                highlights[term] = value
                            except:
                                pass
        
        return highlights

    def _extract_md_a(self, soup: BeautifulSoup) -> str:
        """Extract Management Discussion and Analysis section"""
        md_a_patterns = [
            'management discussion', 'md&a', 'item 2', 'item2',
            'management\'s discussion and analysis'
        ]
        
        for pattern in md_a_patterns:
            elements = soup.find_all(text=lambda text: text and pattern in text.lower())
            if elements:
                for element in elements:
                    parent = element.parent
                    if parent:
                        # Extract surrounding paragraphs
                        text_content = []
                        current = parent.next_sibling
                        count = 0
                        while current and count < 5:
                            if hasattr(current, 'get_text'):
                                text = current.get_text().strip()
                                if text and len(text) > 100:
                                    text_content.append(text)
                                    count += 1
                            current = current.next_sibling
                        
                        if text_content:
                            return ' '.join(text_content)[:1500]  # Limit length
        
        return ""

    def _extract_financial_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract financial statement tables"""
        statements = []
        
        # Look for tables that might contain financial data
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 3:  # Must have header + data rows
                table_data = []
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = [cell.get_text().strip() for cell in cells]
                        table_data.append(row_data)
                
                if table_data:
                    statements.append({
                        'table_data': table_data[:20],  # Limit rows
                        'row_count': len(table_data)
                    })
        
        return statements[:5]  # Limit number of tables

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.aclose()

# Global instance
sec_edgar_service = SECEdgarService()