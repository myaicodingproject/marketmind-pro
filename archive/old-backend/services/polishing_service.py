"""
OpenAI Polishing Service - GPT-4o-mini for content enhancement
Parallel implementation alongside existing system
"""

import openai
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from enhanced_models import SectionPolishRequest, SectionPolishResponse, SectionType

logger = logging.getLogger(__name__)

class OpenAIPolishingService:
    def __init__(self, api_key: Optional[str] = None):
        try:
            self.client = openai.AsyncOpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"
            self.enabled = True
            logger.info("✅ OpenAI polishing service initialized")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI polishing service disabled: {e}")
            self.client = None
            self.enabled = False
        
        # Section-specific prompts for professional polishing
        self.section_prompts = {
            SectionType.EXECUTIVE_SUMMARY: """
Polish this executive summary for an institutional investment research report. Make it:
- Professional and concise
- Include clear investment recommendation (BUY/HOLD/SELL)
- Highlight key financial metrics and price targets
- Use institutional language and terminology
- Ensure logical flow and compelling narrative
""",
            SectionType.COMPANY_ANALYSIS: """
Polish this company analysis section for institutional investors. Ensure:
- Comprehensive business model explanation
- Competitive positioning analysis
- Management quality assessment
- Growth drivers and strategic initiatives
- Professional tone with specific details
""",
            SectionType.FINANCIAL_ANALYSIS: """
Polish this financial analysis for institutional research. Include:
- Clear presentation of historical performance
- Forward-looking projections with assumptions
- Key financial ratios and metrics
- Cash flow analysis
- Professional financial terminology
""",
            SectionType.VALUATION_ANALYSIS: """
Polish this valuation analysis for institutional investors. Ensure:
- Multiple valuation methodologies (DCF, multiples, etc.)
- Clear assumptions and sensitivity analysis
- Peer comparison framework
- Price target derivation
- Professional valuation language
""",
            SectionType.RISK_ASSESSMENT: """
Polish this risk assessment for institutional research. Include:
- Comprehensive risk identification
- Impact and probability assessment
- Mitigation strategies
- Regulatory and market risks
- Professional risk management terminology
""",
            SectionType.MARKET_ANALYSIS: """
Polish this market analysis for institutional investors. Ensure:
- Industry trends and dynamics
- Market size and growth projections
- Competitive landscape analysis
- Regulatory environment
- Professional market research language
""",
            SectionType.TECHNICAL_ANALYSIS: """
Polish this technical analysis for institutional research. Include:
- Chart pattern analysis
- Technical indicators interpretation
- Support and resistance levels
- Trading volume analysis
- Professional technical terminology
""",
            SectionType.INVESTMENT_THESIS: """
Polish this investment thesis for institutional investors. Ensure:
- Clear and compelling investment case
- Risk-reward analysis
- Catalyst identification
- Timeline expectations
- Professional investment language
"""
        }
    
    async def polish_section(self, request: SectionPolishRequest) -> SectionPolishResponse:
        """Polish a single section using GPT-4o-mini"""
        start_time = time.time()
        
        if not self.enabled:
            # Return original content if OpenAI is not available
            logger.warning(f"⚠️ OpenAI disabled, returning raw content for {request.section_type.value}")
            return SectionPolishResponse(
                polished_content=request.raw_content,
                quality_score=0.5,  # Default score
                word_count=len(request.raw_content.split()),
                processing_time_seconds=int(time.time() - start_time)
            )
        
        try:
            # Get section-specific prompt
            section_prompt = self.section_prompts.get(
                request.section_type, 
                "Polish this content for professional institutional investment research."
            )
            
            # Create full prompt
            full_prompt = f"""
{section_prompt}

TARGET: {request.target_pages} pages of professional content for {request.ticker} stock analysis.

ORIGINAL CONTENT:
{request.raw_content}

INSTRUCTIONS:
1. Maintain all factual information and data points
2. Enhance language for institutional audience
3. Improve structure and flow
4. Add professional terminology where appropriate
5. Ensure content meets target length of approximately {request.target_pages} pages
6. Keep the analysis objective and data-driven

POLISHED CONTENT:
"""
            
            # Call GPT-4o-mini
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional financial analyst creating institutional-quality investment research reports. Polish content to meet Wall Street standards while preserving all factual information."
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=4000   # Sufficient for detailed sections
            )
            
            polished_content = response.choices[0].message.content.strip()
            processing_time = int(time.time() - start_time)
            
            # Calculate quality score based on improvement metrics
            quality_score = self._calculate_quality_score(
                request.raw_content, 
                polished_content, 
                request.target_pages
            )
            
            word_count = len(polished_content.split())
            
            logger.info(f"✨ Polished {request.section_type.value} - {word_count} words, quality: {quality_score:.2f}")
            
            return SectionPolishResponse(
                polished_content=polished_content,
                quality_score=quality_score,
                word_count=word_count,
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Polishing failed for {request.section_type.value}: {e}")
            # Return original content with low quality score on failure
            return SectionPolishResponse(
                polished_content=request.raw_content,
                quality_score=0.3,
                word_count=len(request.raw_content.split()),
                processing_time_seconds=int(time.time() - start_time)
            )
    
    def _calculate_quality_score(self, raw_content: str, polished_content: str, target_pages: int) -> float:
        """Calculate quality score based on improvement metrics"""
        try:
            raw_words = len(raw_content.split())
            polished_words = len(polished_content.split())
            target_words = target_pages * 250  # Approximate words per page
            
            # Length appropriateness (0-0.3)
            length_score = min(0.3, polished_words / target_words * 0.3)
            
            # Content improvement (0-0.4)
            improvement_ratio = polished_words / max(raw_words, 1)
            improvement_score = min(0.4, (improvement_ratio - 0.8) * 2 * 0.4) if improvement_ratio > 0.8 else 0.2
            
            # Professional language indicators (0-0.3)
            professional_terms = [
                'analysis', 'valuation', 'dcf', 'ebitda', 'revenue', 'margin',
                'growth', 'risk', 'investment', 'recommendation', 'target',
                'institutional', 'financial', 'market', 'competitive'
            ]
            
            professional_count = sum(1 for term in professional_terms if term.lower() in polished_content.lower())
            professional_score = min(0.3, professional_count / len(professional_terms) * 0.3)
            
            total_score = length_score + improvement_score + professional_score
            return min(1.0, max(0.1, total_score))  # Clamp between 0.1 and 1.0
            
        except Exception:
            return 0.5  # Default score on calculation error
    
    async def generate_embedding(self, content: str) -> List[float]:
        """Generate embedding for RAG using OpenAI"""
        if not self.enabled:
            return []  # Return empty embedding if OpenAI is not available
            
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=content
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            return []

# Global polishing service instance
polishing_service = OpenAIPolishingService()
