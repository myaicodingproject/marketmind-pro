#!/usr/bin/env python3
"""
Section 5 Integration Service
Integrates the competitive advantages agent with the main report generation system
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .section5_competitive_advantages_agent import Section5CompetitiveAdvantagesAgent

logger = logging.getLogger(__name__)

class Section5IntegrationService:
    """Integration service for Section 5 competitive advantages analysis"""
    
    def __init__(self, kiro_engine=None, data_service=None):
        self.agent = Section5CompetitiveAdvantagesAgent(kiro_engine, data_service)
        self.cache = {}  # Simple in-memory cache
        
    async def generate_section5_for_report(
        self, 
        ticker: str, 
        company_data: Dict[str, Any],
        report_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate Section 5 analysis for inclusion in comprehensive report
        
        Args:
            ticker: Stock ticker symbol
            company_data: Company information and financial data
            report_context: Additional context from other report sections
            
        Returns:
            Section 5 analysis formatted for report integration
        """
        try:
            logger.info(f"Generating Section 5 for comprehensive report: {ticker}")
            
            # Check cache first
            cache_key = f"section5_{ticker}_{datetime.now().strftime('%Y%m%d')}"
            if cache_key in self.cache:
                logger.info(f"Using cached Section 5 analysis for {ticker}")
                return self.cache[cache_key]
            
            # Enhance company data with report context
            enhanced_data = self._enhance_company_data(company_data, report_context)
            
            # Generate analysis
            analysis = await self.agent.generate_analysis(ticker, enhanced_data)
            
            # Format for report integration
            formatted_analysis = self._format_for_report(analysis, ticker)
            
            # Cache results
            self.cache[cache_key] = formatted_analysis
            
            logger.info(f"Completed Section 5 generation for {ticker}")
            return formatted_analysis
            
        except Exception as e:
            logger.error(f"Error generating Section 5 for {ticker}: {str(e)}")
            raise
    
    async def get_competitive_summary(self, ticker: str) -> Dict[str, Any]:
        """
        Get executive summary of competitive advantages for dashboard/overview
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Competitive advantages summary
        """
        try:
            # Generate quick analysis or fetch from cache
            company_data = {"ticker": ticker}
            
            # Get key competitive metrics
            moats = await self.agent._analyze_competitive_moats(ticker, company_data)
            porters = await self.agent._assess_porters_five_forces(ticker, company_data)
            
            # Create summary
            summary = {
                "ticker": ticker,
                "competitive_strength": self._calculate_competitive_strength(moats, porters),
                "key_moats": self._extract_key_moats(moats),
                "industry_attractiveness": porters.overall_attractiveness if hasattr(porters, 'overall_attractiveness') else 75,
                "competitive_position": self._assess_competitive_position(moats, porters),
                "generated_at": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating competitive summary for {ticker}: {str(e)}")
            raise
    
    def _enhance_company_data(
        self, 
        company_data: Dict[str, Any], 
        report_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhance company data with additional context from other report sections"""
        
        enhanced_data = company_data.copy()
        
        if report_context:
            # Add financial context from Section 4
            if "financial_analysis" in report_context:
                enhanced_data["financial_metrics"] = report_context["financial_analysis"]
            
            # Add business model context from Section 3
            if "business_model" in report_context:
                enhanced_data["business_model"] = report_context["business_model"]
            
            # Add market context from Section 2
            if "market_analysis" in report_context:
                enhanced_data["market_context"] = report_context["market_analysis"]
        
        return enhanced_data
    
    def _format_for_report(self, analysis: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Format analysis for integration into comprehensive report"""
        
        return {
            "section_info": {
                "section_number": 5,
                "section_title": "Competitive Advantages Analysis",
                "page_count": 4,
                "ticker": ticker
            },
            "executive_summary": self._create_executive_summary(analysis),
            "detailed_analysis": analysis["content"],
            "key_insights": self._extract_key_insights(analysis),
            "visualizations": analysis["content"].get("visualizations", {}),
            "metadata": analysis.get("metadata", {}),
            "report_integration": {
                "cross_references": self._generate_cross_references(analysis),
                "supporting_data": self._extract_supporting_data(analysis)
            }
        }
    
    def _create_executive_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary of competitive advantages"""
        
        content = analysis.get("content", {})
        
        # Extract key metrics
        moats_strength = self._calculate_moats_strength(content.get("competitive_moats", {}))
        industry_attractiveness = 75  # Default
        
        if "porters_five_forces" in content:
            porters = content["porters_five_forces"]
            if hasattr(porters, 'overall_attractiveness'):
                industry_attractiveness = porters.overall_attractiveness
        
        return {
            "overall_competitive_strength": moats_strength,
            "industry_attractiveness": industry_attractiveness,
            "key_competitive_advantages": self._identify_key_advantages(content),
            "primary_threats": self._identify_primary_threats(content),
            "strategic_recommendations": self._extract_strategic_recommendations(content)
        }
    
    def _extract_key_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract key insights from the analysis"""
        
        insights = []
        content = analysis.get("content", {})
        
        # Moats insights
        if "competitive_moats" in content:
            moats = content["competitive_moats"]
            strongest_moat = max(moats.items(), key=lambda x: x[1].get("strength", 0) if isinstance(x[1], dict) else 0)
            insights.append(f"Strongest competitive moat: {strongest_moat[0].replace('_', ' ').title()}")
        
        # Porter's insights
        if "porters_five_forces" in content:
            porters = content["porters_five_forces"]
            if hasattr(porters, 'overall_attractiveness'):
                if porters.overall_attractiveness > 70:
                    insights.append("Industry structure is highly attractive for profitability")
                elif porters.overall_attractiveness < 50:
                    insights.append("Industry faces significant competitive pressures")
        
        # Sustainability insights
        if "competitive_sustainability" in content:
            sustainability = content["competitive_sustainability"]
            if isinstance(sustainability, dict) and "sustainability_assessment" in sustainability:
                assessment = sustainability["sustainability_assessment"]
                if "short_term" in assessment and assessment["short_term"].get("score", 0) > 80:
                    insights.append("Strong short-term competitive position sustainability")
        
        return insights
    
    def _calculate_competitive_strength(self, moats: Dict[str, Any], porters) -> float:
        """Calculate overall competitive strength score"""
        
        moats_score = self._calculate_moats_strength(moats)
        industry_score = porters.overall_attractiveness if hasattr(porters, 'overall_attractiveness') else 75
        
        # Weighted average (60% moats, 40% industry)
        return (moats_score * 0.6) + (industry_score * 0.4)
    
    def _calculate_moats_strength(self, moats: Dict[str, Any]) -> float:
        """Calculate average moats strength"""
        
        if not moats:
            return 50.0
        
        strengths = []
        for moat_data in moats.values():
            if isinstance(moat_data, dict) and "strength" in moat_data:
                strengths.append(moat_data["strength"])
        
        return sum(strengths) / len(strengths) if strengths else 50.0
    
    def _extract_key_moats(self, moats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract top 3 competitive moats"""
        
        if not moats:
            return []
        
        moat_list = []
        for moat_type, data in moats.items():
            if isinstance(data, dict) and "strength" in data:
                moat_list.append({
                    "type": moat_type.replace("_", " ").title(),
                    "strength": data["strength"],
                    "sustainability": data.get("sustainability", "moderate")
                })
        
        # Sort by strength and return top 3
        moat_list.sort(key=lambda x: x["strength"], reverse=True)
        return moat_list[:3]
    
    def _assess_competitive_position(self, moats: Dict[str, Any], porters) -> str:
        """Assess overall competitive position"""
        
        strength = self._calculate_competitive_strength(moats, porters)
        
        if strength >= 80:
            return "Very Strong"
        elif strength >= 70:
            return "Strong"
        elif strength >= 60:
            return "Moderate"
        elif strength >= 50:
            return "Weak"
        else:
            return "Very Weak"
    
    def _identify_key_advantages(self, content: Dict[str, Any]) -> List[str]:
        """Identify key competitive advantages"""
        advantages = []
        
        if "competitive_moats" in content:
            moats = content["competitive_moats"]
            for moat_type, data in moats.items():
                if isinstance(data, dict) and data.get("strength", 0) > 75:
                    advantages.append(moat_type.replace("_", " ").title())
        
        return advantages[:3]  # Top 3
    
    def _identify_primary_threats(self, content: Dict[str, Any]) -> List[str]:
        """Identify primary competitive threats"""
        threats = []
        
        if "competitive_moats" in content:
            moats = content["competitive_moats"]
            for data in moats.values():
                if isinstance(data, dict) and "threats" in data:
                    threats.extend(data["threats"][:2])  # Top 2 per moat
        
        return list(set(threats))[:3]  # Unique top 3
    
    def _extract_strategic_recommendations(self, content: Dict[str, Any]) -> List[str]:
        """Extract strategic recommendations"""
        recommendations = []
        
        if "competitive_sustainability" in content:
            sustainability = content["competitive_sustainability"]
            if isinstance(sustainability, dict) and "strategic_recommendations" in sustainability:
                recs = sustainability["strategic_recommendations"]
                if isinstance(recs, dict):
                    for category, items in recs.items():
                        if isinstance(items, list):
                            recommendations.extend(items[:2])  # Top 2 per category
        
        return recommendations[:3]  # Top 3 overall
    
    def _generate_cross_references(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cross-references to other report sections"""
        return {
            "section_3_business_model": "Competitive moats support business model sustainability",
            "section_4_financial_analysis": "Strong moats enable premium pricing and margins",
            "section_6_risk_assessment": "Competitive threats identified in risk analysis"
        }
    
    def _extract_supporting_data(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract supporting data for other sections"""
        return {
            "competitive_metrics": analysis.get("content", {}).get("competitive_moats", {}),
            "industry_structure": analysis.get("content", {}).get("porters_five_forces", {}),
            "sustainability_outlook": analysis.get("content", {}).get("competitive_sustainability", {})
        }