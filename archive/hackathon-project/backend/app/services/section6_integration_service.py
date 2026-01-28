#!/usr/bin/env python3
"""
Section 6 Integration Service
Integrates Market Size & Growth Analysis with the main MarketMind Pro system
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .section6_market_analysis_agent import Section6MarketAnalysisAgent
from .kiro_prompt_service import KiroPromptService

logger = logging.getLogger(__name__)

class Section6IntegrationService:
    """Integration service for Section 6 Market Analysis"""
    
    def __init__(self):
        self.market_agent = Section6MarketAnalysisAgent()
        self.kiro_service = KiroPromptService()
        
    async def generate_section6_report(self, ticker: str, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Section 6 market analysis report with Kiro enhancement"""
        try:
            logger.info(f"Starting Section 6 market analysis for {ticker}")
            
            # Step 1: Generate base market analysis
            base_analysis = await self.market_agent.generate_market_analysis(ticker)
            
            # Step 2: Enhance with Kiro analysis if available
            if context_data:
                enhanced_analysis = await self._enhance_with_kiro(ticker, base_analysis, context_data)
            else:
                enhanced_analysis = base_analysis
            
            # Step 3: Format for PDF generation
            formatted_report = await self._format_for_pdf(enhanced_analysis)
            
            logger.info(f"Section 6 analysis completed for {ticker}")
            return formatted_report
            
        except Exception as e:
            logger.error(f"Error in Section 6 integration for {ticker}: {str(e)}")
            return self._create_error_response(ticker, str(e))
    
    async def _enhance_with_kiro(self, ticker: str, base_analysis: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance analysis using Kiro prompts"""
        try:
            # Prepare context for Kiro
            kiro_context = {
                'ticker': ticker,
                'base_analysis': base_analysis,
                'company_data': context_data.get('company_data', {}),
                'financial_data': context_data.get('financial_data', {}),
                'industry_data': context_data.get('industry_data', {})
            }
            
            # Use Kiro to enhance market analysis
            kiro_enhancement = await self.kiro_service.execute_prompt(
                'section6-market-size-growth-analysis',
                kiro_context
            )
            
            # Merge Kiro insights with base analysis
            enhanced_analysis = self._merge_analyses(base_analysis, kiro_enhancement)
            
            return enhanced_analysis
            
        except Exception as e:
            logger.warning(f"Kiro enhancement failed for {ticker}: {str(e)}")
            return base_analysis
    
    def _merge_analyses(self, base_analysis: Dict[str, Any], kiro_enhancement: Dict[str, Any]) -> Dict[str, Any]:
        """Merge base analysis with Kiro enhancements"""
        try:
            merged = base_analysis.copy()
            
            if 'section_6_market_analysis' in kiro_enhancement:
                kiro_data = kiro_enhancement['section_6_market_analysis']
                base_data = merged.get('section_6_market_analysis', {})
                
                # Enhance TAM analysis
                if 'tam_analysis' in kiro_data:
                    base_data['tam_analysis'].update(kiro_data['tam_analysis'])
                
                # Enhance growth forecasts
                if 'growth_forecasts' in kiro_data:
                    base_data['growth_forecasts'].update(kiro_data['growth_forecasts'])
                
                # Add Kiro insights
                base_data['kiro_insights'] = kiro_data.get('insights', [])
                base_data['enhanced_at'] = datetime.now().isoformat()
            
            return merged
            
        except Exception as e:
            logger.error(f"Error merging analyses: {str(e)}")
            return base_analysis
    
    async def _format_for_pdf(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis for PDF generation"""
        try:
            section_data = analysis.get('section_6_market_analysis', {})
            
            formatted = {
                'section_6': {
                    'title': 'Market Size & Growth Potential',
                    'pages': 4,
                    'content': {
                        'tam_analysis': {
                            'title': 'Total Addressable Market Analysis',
                            'market_size': section_data.get('tam_analysis', {}).get('total_market_size_usd_billions', 0),
                            'growth_rate': section_data.get('tam_analysis', {}).get('historical_growth_cagr', 0),
                            'segments': section_data.get('tam_analysis', {}).get('key_segments', []),
                            'geography': section_data.get('tam_analysis', {}).get('geographic_breakdown', {})
                        },
                        'sam_analysis': {
                            'title': 'Serviceable Addressable Market',
                            'market_size': section_data.get('sam_analysis', {}).get('serviceable_market_size', 0),
                            'market_share': section_data.get('sam_analysis', {}).get('company_market_share', 0),
                            'position': section_data.get('sam_analysis', {}).get('competitive_position', '')
                        },
                        'growth_forecasts': {
                            'title': 'Growth Forecasts & Market Trends',
                            'cagr': section_data.get('growth_forecasts', {}).get('five_year_cagr', 0),
                            'drivers': section_data.get('growth_forecasts', {}).get('growth_drivers', []),
                            'catalysts': section_data.get('growth_forecasts', {}).get('market_catalysts', []),
                            'risks': section_data.get('growth_forecasts', {}).get('risk_factors', [])
                        },
                        'strategic_roadmap': {
                            'title': 'Strategic Expansion Roadmap',
                            'priorities': section_data.get('strategic_roadmap', {}).get('expansion_priorities', []),
                            'investments': section_data.get('strategic_roadmap', {}).get('investment_requirements', {}),
                            'timeline': section_data.get('strategic_roadmap', {}).get('timeline_milestones', []),
                            'metrics': section_data.get('strategic_roadmap', {}).get('success_metrics', [])
                        }
                    },
                    'charts': section_data.get('charts', []),
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'ticker': section_data.get('metadata', {}).get('ticker', ''),
                        'confidence': section_data.get('metadata', {}).get('analysis_confidence', 'Medium')
                    }
                }
            }
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting for PDF: {str(e)}")
            return {'section_6': {'error': str(e)}}
    
    def _create_error_response(self, ticker: str, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'section_6': {
                'title': 'Market Size & Growth Potential',
                'error': error_message,
                'ticker': ticker,
                'generated_at': datetime.now().isoformat(),
                'status': 'error'
            }
        }
    
    async def get_section_status(self, ticker: str) -> Dict[str, Any]:
        """Get status of Section 6 analysis"""
        return {
            'section': 6,
            'name': 'Market Size & Growth Potential',
            'status': 'ready',
            'estimated_time': '2-3 minutes',
            'dependencies': ['company_data', 'industry_data']
        }

# Example usage
async def main():
    service = Section6IntegrationService()
    result = await service.generate_section6_report('AAPL')
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())