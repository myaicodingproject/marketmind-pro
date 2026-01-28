"""Content Parser Service for MarketMind Pro - Parses Kiro CLI output into structured data."""

import re
from typing import List, Dict, Any, Optional
import markdown
from bs4 import BeautifulSoup
from models.enhanced_models import ReportSection, TableData, MetricData, ChartData


class ContentParserService:
    """Parses Kiro CLI output into structured report components."""
    
    def __init__(self):
        self.md = markdown.Markdown(extensions=['tables', 'extra'])
    
    def parse_section(self, content: str) -> ReportSection:
        """Parse content into a structured report section."""
        lines = content.strip().split('\n')
        title = self._extract_title(lines)
        
        return ReportSection(
            title=title,
            content=self.extract_clean_text(content),
            tables=self.extract_tables(content),
            metrics=self.extract_metrics(content),
            charts=self.identify_chart_opportunities(content)
        )
    
    def extract_tables(self, content: str) -> List[TableData]:
        """Extract tables from markdown content."""
        html = self.md.convert(content)
        soup = BeautifulSoup(html, 'html.parser')
        tables = []
        
        for table in soup.find_all('table'):
            headers = [th.get_text().strip() for th in table.find_all('th')]
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip header row
                row = [td.get_text().strip() for td in tr.find_all('td')]
                if row:
                    rows.append(row)
            
            if headers and rows:
                tables.append(TableData(headers=headers, rows=rows))
        
        return tables
    
    def extract_metrics(self, content: str) -> List[MetricData]:
        """Extract financial metrics with pattern matching."""
        metrics = []
        
        # Pattern for currency, percentages, and large numbers
        patterns = [
            (r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*([BM]?)', 'currency'),
            (r'(\d+(?:\.\d+)?)\s*%', 'percentage'),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*([BM])', 'number')
        ]
        
        for pattern, metric_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                value = match.group(1).replace(',', '')
                unit = match.group(2) if len(match.groups()) > 1 else ''
                
                # Convert to float and apply unit multipliers
                try:
                    num_value = float(value)
                    if unit.upper() == 'B':
                        num_value *= 1_000_000_000
                    elif unit.upper() == 'M':
                        num_value *= 1_000_000
                    
                    metrics.append(MetricData(
                        name=self._extract_metric_name(content, match.start()),
                        value=num_value,
                        unit=unit,
                        type=metric_type
                    ))
                except ValueError:
                    continue
        
        return metrics
    
    def identify_chart_opportunities(self, content: str) -> List[ChartData]:
        """Identify opportunities for chart generation."""
        charts = []
        
        # Look for time series indicators
        time_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4})',  # Year ranges
            r'Q[1-4]\s+\d{4}',  # Quarters
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'  # Months
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, content):
                charts.append(ChartData(
                    type='line',
                    title='Time Series Analysis',
                    data_source='time_series'
                ))
                break
        
        # Look for comparison indicators
        comparison_keywords = ['vs', 'versus', 'compared to', 'peer', 'competitor']
        if any(keyword in content.lower() for keyword in comparison_keywords):
            charts.append(ChartData(
                type='bar',
                title='Peer Comparison',
                data_source='comparison'
            ))
        
        # Look for percentage breakdowns
        if len(re.findall(r'\d+(?:\.\d+)?%', content)) >= 3:
            charts.append(ChartData(
                type='pie',
                title='Composition Analysis',
                data_source='breakdown'
            ))
        
        return charts
    
    def extract_clean_text(self, content: str) -> str:
        """Remove markdown symbols and return clean text."""
        # Remove markdown formatting
        clean = re.sub(r'[#*_`~\[\]()]', '', content)
        clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)  # Remove images
        clean = re.sub(r'\|.*?\|', '', clean)  # Remove table separators
        clean = re.sub(r'\n\s*\n', '\n\n', clean)  # Normalize line breaks
        
        return clean.strip()
    
    def _extract_title(self, lines: List[str]) -> str:
        """Extract title from content lines."""
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('#'):
                return line.lstrip('#').strip()
            if line.strip() and len(line.strip()) < 100:
                return line.strip()
        return "Untitled Section"
    
    def _extract_metric_name(self, content: str, position: int) -> str:
        """Extract metric name from context around position."""
        lines = content[:position].split('\n')
        context = lines[-1] if lines else ""
        
        # Look for common metric patterns
        words = context.split()
        if len(words) >= 2:
            return ' '.join(words[-2:])
        
        return "Metric"


# Global instance
content_parser_service = ContentParserService()
