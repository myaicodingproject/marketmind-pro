"""
SEC Filing Parser with Advanced PDF/HTML Processing

This module handles complex SEC filing formats including:
- HTML-based EDGAR filings
- PDF document processing
- XBRL data extraction
- Financial table parsing
- Regulatory text processing
"""

import asyncio
import re
import io
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from pathlib import Path

import httpx
import pandas as pd
from bs4 import BeautifulSoup, NavigableString
import PyPDF2
from lxml import etree, html
import json

logger = logging.getLogger(__name__)

class SECFilingParser:
    """Advanced SEC filing parser for complex document formats"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "User-Agent": "MarketMind-Pro/1.0 (SEC Filing Parser) contact@marketmind.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate"
            }
        )
        
        # SEC-specific patterns for section identification
        self.sec_section_patterns = {
            "10-K": {
                "business": [
                    r"item\s*1\s*[\.\-\s]*business",
                    r"part\s*i\s*[\.\-\s]*item\s*1\s*[\.\-\s]*business"
                ],
                "risk_factors": [
                    r"item\s*1a\s*[\.\-\s]*risk\s*factors",
                    r"part\s*i\s*[\.\-\s]*item\s*1a\s*[\.\-\s]*risk\s*factors"
                ],
                "properties": [
                    r"item\s*2\s*[\.\-\s]*properties"
                ],
                "legal_proceedings": [
                    r"item\s*3\s*[\.\-\s]*legal\s*proceedings"
                ],
                "management_discussion": [
                    r"item\s*7\s*[\.\-\s]*management['\s]*s\s*discussion",
                    r"md&a"
                ],
                "financial_statements": [
                    r"item\s*8\s*[\.\-\s]*financial\s*statements",
                    r"consolidated\s*statements"
                ],
                "controls_procedures": [
                    r"item\s*9a\s*[\.\-\s]*controls\s*and\s*procedures"
                ]
            },
            "10-Q": {
                "financial_statements": [
                    r"part\s*i\s*[\.\-\s]*financial\s*information",
                    r"item\s*1\s*[\.\-\s]*financial\s*statements"
                ],
                "management_discussion": [
                    r"item\s*2\s*[\.\-\s]*management['\s]*s\s*discussion",
                    r"md&a"
                ],
                "legal_proceedings": [
                    r"item\s*1\s*[\.\-\s]*legal\s*proceedings"
                ],
                "controls_procedures": [
                    r"item\s*4\s*[\.\-\s]*controls\s*and\s*procedures"
                ]
            },
            "8-K": {
                "current_report": [
                    r"item\s*\d+\.\d+",
                    r"section\s*\d+"
                ]
            }
        }
        
        # Financial statement patterns
        self.financial_table_patterns = {
            "income_statement": [
                r"consolidated\s*statements?\s*of\s*(income|operations|earnings)",
                r"statements?\s*of\s*(income|operations|earnings)",
                r"income\s*statements?"
            ],
            "balance_sheet": [
                r"consolidated\s*balance\s*sheets?",
                r"statements?\s*of\s*financial\s*position",
                r"balance\s*sheets?"
            ],
            "cash_flow": [
                r"consolidated\s*statements?\s*of\s*cash\s*flows?",
                r"statements?\s*of\s*cash\s*flows?",
                r"cash\s*flow\s*statements?"
            ],
            "equity": [
                r"consolidated\s*statements?\s*of\s*(equity|stockholders|shareholders)",
                r"statements?\s*of\s*(equity|stockholders|shareholders)"
            ]
        }
    
    async def parse_sec_filing(self, filing_url: str, filing_metadata: Dict) -> Dict[str, Any]:
        """Parse SEC filing from URL"""
        logger.info(f"Parsing SEC filing: {filing_url}")
        
        try:
            # Fetch the filing content
            content = await self._fetch_filing_content(filing_url)
            
            # Determine content type and parse accordingly
            if filing_url.endswith('.pdf'):
                parsed_data = await self._parse_pdf_filing(content, filing_metadata)
            elif 'htm' in filing_url or 'html' in filing_url:
                parsed_data = await self._parse_html_filing(content, filing_metadata)
            else:
                # Try to parse as HTML first, then as text
                try:
                    parsed_data = await self._parse_html_filing(content, filing_metadata)
                except:
                    parsed_data = await self._parse_text_filing(content, filing_metadata)
            
            return parsed_data
        
        except Exception as e:
            logger.error(f"Failed to parse SEC filing {filing_url}: {e}")
            raise
    
    async def _fetch_filing_content(self, url: str) -> bytes:
        """Fetch filing content with proper SEC compliance"""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to fetch filing content from {url}: {e}")
            raise
    
    async def _parse_html_filing(self, content: bytes, metadata: Dict) -> Dict[str, Any]:
        """Parse HTML-based SEC filing"""
        try:
            # Decode content
            html_content = content.decode('utf-8', errors='ignore')
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic information
            parsed_data = {
                "filing_type": metadata.get("form", "Unknown"),
                "raw_html": html_content,
                "text_content": "",
                "sections": {},
                "financial_tables": [],
                "metadata": metadata,
                "parsing_method": "html"
            }
            
            # Clean and extract text
            parsed_data["text_content"] = self._extract_clean_text(soup)
            
            # Extract sections based on filing type
            form_type = metadata.get("form", "").upper()
            if form_type in self.sec_section_patterns:
                parsed_data["sections"] = self._extract_sections(
                    parsed_data["text_content"], 
                    self.sec_section_patterns[form_type]
                )
            
            # Extract financial tables
            parsed_data["financial_tables"] = self._extract_html_tables(soup)
            
            # Extract XBRL data if present
            xbrl_data = self._extract_xbrl_data(soup)
            if xbrl_data:
                parsed_data["xbrl_data"] = xbrl_data
            
            logger.info(f"Parsed HTML filing: {len(parsed_data['sections'])} sections, {len(parsed_data['financial_tables'])} tables")
            return parsed_data
        
        except Exception as e:
            logger.error(f"Failed to parse HTML filing: {e}")
            raise
    
    async def _parse_pdf_filing(self, content: bytes, metadata: Dict) -> Dict[str, Any]:
        """Parse PDF-based SEC filing"""
        try:
            # Create PDF reader
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            parsed_data = {
                "filing_type": metadata.get("form", "Unknown"),
                "text_content": text_content,
                "sections": {},
                "financial_tables": [],
                "metadata": metadata,
                "parsing_method": "pdf",
                "page_count": len(pdf_reader.pages)
            }
            
            # Extract sections
            form_type = metadata.get("form", "").upper()
            if form_type in self.sec_section_patterns:
                parsed_data["sections"] = self._extract_sections(
                    text_content, 
                    self.sec_section_patterns[form_type]
                )
            
            # Extract financial tables from text
            parsed_data["financial_tables"] = self._extract_text_tables(text_content)
            
            logger.info(f"Parsed PDF filing: {len(pdf_reader.pages)} pages, {len(parsed_data['sections'])} sections")
            return parsed_data
        
        except Exception as e:
            logger.error(f"Failed to parse PDF filing: {e}")
            raise
    
    async def _parse_text_filing(self, content: bytes, metadata: Dict) -> Dict[str, Any]:
        """Parse plain text SEC filing"""
        try:
            text_content = content.decode('utf-8', errors='ignore')
            
            parsed_data = {
                "filing_type": metadata.get("form", "Unknown"),
                "text_content": text_content,
                "sections": {},
                "financial_tables": [],
                "metadata": metadata,
                "parsing_method": "text"
            }
            
            # Extract sections
            form_type = metadata.get("form", "").upper()
            if form_type in self.sec_section_patterns:
                parsed_data["sections"] = self._extract_sections(
                    text_content, 
                    self.sec_section_patterns[form_type]
                )
            
            # Extract financial tables
            parsed_data["financial_tables"] = self._extract_text_tables(text_content)
            
            logger.info(f"Parsed text filing: {len(parsed_data['sections'])} sections")
            return parsed_data
        
        except Exception as e:
            logger.error(f"Failed to parse text filing: {e}")
            raise
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML soup"""
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        # Remove XBRL tags but keep content
        for xbrl_tag in soup.find_all(re.compile(r'^(ix:|xbrl:|us-gaap:|dei:)')):
            xbrl_tag.unwrap()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace and formatting
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text
    
    def _extract_sections(self, text: str, section_patterns: Dict[str, List[str]]) -> Dict[str, str]:
        """Extract sections from text using patterns"""
        sections = {}
        text_lower = text.lower()
        
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text_lower, re.IGNORECASE | re.MULTILINE))
                
                if matches:
                    # Use the first match
                    match = matches[0]
                    start_pos = match.start()
                    
                    # Find the end of this section (next section or reasonable cutoff)
                    end_pos = self._find_section_end(text_lower, start_pos, section_patterns)
                    
                    # Extract section content
                    section_content = text[start_pos:end_pos].strip()
                    
                    # Clean up section content
                    section_content = self._clean_section_content(section_content)
                    
                    if len(section_content) > 100:  # Only include substantial sections
                        sections[section_name] = section_content
                    
                    break  # Use first matching pattern
        
        return sections
    
    def _find_section_end(self, text: str, start_pos: int, all_patterns: Dict[str, List[str]]) -> int:
        """Find the end position of a section"""
        # Look for the next section header
        next_section_pos = len(text)
        
        # Check all patterns for next section
        for patterns in all_patterns.values():
            for pattern in patterns:
                matches = re.finditer(pattern, text[start_pos + 100:], re.IGNORECASE)
                for match in matches:
                    pos = start_pos + 100 + match.start()
                    if pos < next_section_pos:
                        next_section_pos = pos
                    break  # Only check first match per pattern
        
        # If no next section found, limit to reasonable size
        if next_section_pos == len(text):
            next_section_pos = min(start_pos + 10000, len(text))
        
        return next_section_pos
    
    def _clean_section_content(self, content: str) -> str:
        """Clean section content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Remove page numbers and headers/footers
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip likely page numbers
            if re.match(r'^\d+$', line):
                continue
            
            # Skip very short lines that are likely formatting artifacts
            if len(line) < 3:
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_html_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract financial tables from HTML"""
        tables = []
        html_tables = soup.find_all('table')
        
        for i, table in enumerate(html_tables):
            try:
                # Skip very small tables
                rows = table.find_all('tr')
                if len(rows) < 3:
                    continue
                
                # Convert to pandas DataFrame
                df = pd.read_html(str(table))[0]
                
                # Skip tables that are too small or too large
                if df.shape[0] < 2 or df.shape[1] < 2 or df.shape[0] > 1000:
                    continue
                
                # Check if it's a financial table
                table_type = self._classify_table(table, df)
                
                if table_type != "unknown":
                    table_data = {
                        "table_id": f"table_{i}",
                        "table_type": table_type,
                        "data": df.to_dict('records'),
                        "columns": df.columns.tolist(),
                        "shape": df.shape,
                        "html": str(table)[:1000]  # First 1000 chars for reference
                    }
                    tables.append(table_data)
            
            except Exception as e:
                logger.debug(f"Failed to parse HTML table {i}: {e}")
                continue
        
        return tables
    
    def _extract_text_tables(self, text: str) -> List[Dict[str, Any]]:
        """Extract tables from plain text"""
        tables = []
        
        # Look for table-like structures in text
        lines = text.split('\n')
        current_table = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            # Check if line looks like a table row (multiple columns separated by spaces/tabs)
            if self._is_table_row(line):
                current_table.append(line)
                in_table = True
            else:
                if in_table and len(current_table) > 2:
                    # Process the table
                    table_data = self._process_text_table(current_table, len(tables))
                    if table_data:
                        tables.append(table_data)
                
                current_table = []
                in_table = False
        
        # Process final table if exists
        if in_table and len(current_table) > 2:
            table_data = self._process_text_table(current_table, len(tables))
            if table_data:
                tables.append(table_data)
        
        return tables
    
    def _is_table_row(self, line: str) -> bool:
        """Check if a line looks like a table row"""
        # Look for multiple numeric values or structured data
        if len(line) < 10:
            return False
        
        # Count numeric patterns
        numeric_patterns = re.findall(r'[\d,]+\.?\d*', line)
        if len(numeric_patterns) >= 2:
            return True
        
        # Look for consistent spacing/tabs
        if '\t' in line and len(line.split('\t')) >= 3:
            return True
        
        # Look for multiple dollar amounts
        dollar_patterns = re.findall(r'\$[\d,]+\.?\d*', line)
        if len(dollar_patterns) >= 2:
            return True
        
        return False
    
    def _process_text_table(self, table_lines: List[str], table_id: int) -> Optional[Dict[str, Any]]:
        """Process extracted text table"""
        try:
            # Try to parse as structured data
            rows = []
            for line in table_lines:
                # Split by tabs first, then by multiple spaces
                if '\t' in line:
                    row = [cell.strip() for cell in line.split('\t')]
                else:
                    row = [cell.strip() for cell in re.split(r'\s{2,}', line) if cell.strip()]
                
                if len(row) >= 2:
                    rows.append(row)
            
            if len(rows) < 2:
                return None
            
            # Create DataFrame
            df = pd.DataFrame(rows[1:], columns=rows[0] if len(rows[0]) == len(rows[1]) else None)
            
            # Classify table type
            table_type = self._classify_text_table(table_lines)
            
            return {
                "table_id": f"text_table_{table_id}",
                "table_type": table_type,
                "data": df.to_dict('records'),
                "columns": df.columns.tolist() if df.columns is not None else [],
                "shape": df.shape,
                "raw_lines": table_lines[:10]  # First 10 lines for reference
            }
        
        except Exception as e:
            logger.debug(f"Failed to process text table: {e}")
            return None
    
    def _classify_table(self, table_element, df: pd.DataFrame) -> str:
        """Classify HTML table type"""
        # Get table context (surrounding text)
        table_text = str(table_element).lower()
        
        # Check for financial statement patterns
        for table_type, patterns in self.financial_table_patterns.items():
            for pattern in patterns:
                if re.search(pattern, table_text, re.IGNORECASE):
                    return table_type
        
        # Check column headers
        if hasattr(df, 'columns'):
            columns_text = ' '.join(str(col).lower() for col in df.columns)
            
            if any(term in columns_text for term in ['revenue', 'income', 'expense', 'earnings']):
                return 'income_statement'
            elif any(term in columns_text for term in ['assets', 'liabilities', 'equity']):
                return 'balance_sheet'
            elif any(term in columns_text for term in ['cash', 'operating', 'investing', 'financing']):
                return 'cash_flow'
        
        # Check if it contains financial data
        sample_text = str(df.head()).lower()
        if any(term in sample_text for term in ['$', 'million', 'thousand', 'revenue', 'income']):
            return 'financial_data'
        
        return 'unknown'
    
    def _classify_text_table(self, table_lines: List[str]) -> str:
        """Classify text table type"""
        table_text = ' '.join(table_lines).lower()
        
        # Check for financial statement patterns
        for table_type, patterns in self.financial_table_patterns.items():
            for pattern in patterns:
                if re.search(pattern, table_text, re.IGNORECASE):
                    return table_type
        
        # Check for financial keywords
        if any(term in table_text for term in ['revenue', 'income', 'expense', 'earnings']):
            return 'income_statement'
        elif any(term in table_text for term in ['assets', 'liabilities', 'equity']):
            return 'balance_sheet'
        elif any(term in table_text for term in ['cash', 'operating', 'investing', 'financing']):
            return 'cash_flow'
        elif any(term in table_text for term in ['$', 'million', 'thousand']):
            return 'financial_data'
        
        return 'unknown'
    
    def _extract_xbrl_data(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract XBRL data from HTML filing"""
        xbrl_data = {}
        
        # Find XBRL tags
        xbrl_tags = soup.find_all(re.compile(r'^(ix:|xbrl:|us-gaap:|dei:)'))
        
        if not xbrl_tags:
            return None
        
        for tag in xbrl_tags:
            tag_name = tag.name
            tag_text = tag.get_text(strip=True)
            
            # Extract attributes
            attributes = dict(tag.attrs)
            
            if tag_text and tag_name:
                xbrl_data[tag_name] = {
                    "value": tag_text,
                    "attributes": attributes
                }
        
        return xbrl_data if xbrl_data else None
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()

# Test function
async def test_sec_parser():
    """Test SEC filing parser"""
    parser = SECFilingParser()
    
    # Test with a sample SEC filing URL
    test_url = "https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230930.htm"
    test_metadata = {
        "form": "10-K",
        "filing_date": "2023-11-03",
        "ticker": "AAPL"
    }
    
    try:
        result = await parser.parse_sec_filing(test_url, test_metadata)
        print(f"Parsed filing: {len(result['sections'])} sections, {len(result['financial_tables'])} tables")
        print(f"Text length: {len(result['text_content'])} characters")
        
        # Print section names
        print("Sections found:", list(result['sections'].keys()))
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        await parser.cleanup()

if __name__ == "__main__":
    asyncio.run(test_sec_parser())