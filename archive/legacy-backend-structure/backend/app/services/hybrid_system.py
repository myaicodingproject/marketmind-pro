"""
Hybrid PDF System - Phase 1: Foundation Setup
Combines AI-powered content enhancement with rule-based fallbacks
"""

import asyncio
import logging
import re
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)

class IssueType(str, Enum):
    FORMATTING = "formatting"
    CONTENT_QUALITY = "content_quality"
    STRUCTURE = "structure"
    DATA_ACCURACY = "data_accuracy"

class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PDFIssue(BaseModel):
    type: IssueType
    severity: IssueSeverity
    description: str
    location: str
    suggested_fix: Optional[str] = None

class EnhancedSection(BaseModel):
    title: str
    content: str
    quality_score: float = Field(ge=0.0, le=1.0)
    issues_fixed: List[PDFIssue] = Field(default_factory=list)
    enhancement_applied: bool = False

class HybridPDFSystem:
    """Core system for AI-enhanced PDF content processing with rule-based fallbacks"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_client = AsyncOpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        self.max_retries = 3
        self.timeout = 30
        
    async def detect_issues(self, content: str, section_type: str = "general") -> List[PDFIssue]:
        """Detect content issues using AI with rule-based fallbacks"""
        issues = []
        
        try:
            # AI-powered detection
            ai_issues = await self._ai_detect_issues(content, section_type)
            issues.extend(ai_issues)
        except Exception as e:
            logger.warning(f"AI issue detection failed: {e}")
            
        # Rule-based fallback detection
        rule_issues = self._rule_based_detection(content)
        issues.extend(rule_issues)
        
        return self._deduplicate_issues(issues)
    
    async def fix_content(self, content: str, issues: List[PDFIssue]) -> str:
        """Fix content issues using AI with rule-based fallbacks"""
        if not issues:
            return content
            
        try:
            # Try AI-powered fixing first
            return await self._ai_fix_content(content, issues)
        except Exception as e:
            logger.warning(f"AI content fixing failed: {e}")
            # Fallback to rule-based fixing
            return self._rule_based_fixing(content, issues)
    
    async def calculate_quality_score(self, content: str, section_type: str = "general") -> float:
        """Calculate content quality score (0.0-1.0)"""
        try:
            return await self._ai_quality_score(content, section_type)
        except Exception as e:
            logger.warning(f"AI quality scoring failed: {e}")
            return self._rule_based_quality_score(content)
    
    async def enhance_section(self, title: str, content: str, section_type: str = "general") -> EnhancedSection:
        """Main method to enhance a PDF section"""
        try:
            # Detect issues
            issues = await self.detect_issues(content, section_type)
            
            # Fix content
            enhanced_content = await self.fix_content(content, issues)
            
            # Calculate quality score
            quality_score = await self.calculate_quality_score(enhanced_content, section_type)
            
            return EnhancedSection(
                title=title,
                content=enhanced_content,
                quality_score=quality_score,
                issues_fixed=issues,
                enhancement_applied=enhanced_content != content
            )
            
        except Exception as e:
            logger.error(f"Section enhancement failed: {e}")
            # Return original with basic cleanup
            cleaned_content = self._basic_cleanup(content)
            return EnhancedSection(
                title=title,
                content=cleaned_content,
                quality_score=0.5,
                issues_fixed=[],
                enhancement_applied=cleaned_content != content
            )
    
    async def _ai_detect_issues(self, content: str, section_type: str) -> List[PDFIssue]:
        """AI-powered issue detection"""
        prompt = f"""Analyze this {section_type} content for issues. Return JSON array of issues:
        
Content: {content[:1000]}...

Format: [{{"type": "formatting|content_quality|structure|data_accuracy", "severity": "low|medium|high|critical", "description": "issue description", "location": "specific location", "suggested_fix": "how to fix"}}]"""

        response = await asyncio.wait_for(
            self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            ),
            timeout=self.timeout
        )
        
        try:
            import json
            issues_data = json.loads(response.choices[0].message.content)
            return [PDFIssue(**issue) for issue in issues_data]
        except:
            return []
    
    async def _ai_fix_content(self, content: str, issues: List[PDFIssue]) -> str:
        """AI-powered content fixing"""
        issues_desc = "\n".join([f"- {issue.description}: {issue.suggested_fix}" for issue in issues])
        
        prompt = f"""Fix these issues in the content:

Issues to fix:
{issues_desc}

Content:
{content}

Return only the fixed content, no explanations."""

        response = await asyncio.wait_for(
            self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            ),
            timeout=self.timeout
        )
        
        return response.choices[0].message.content.strip()
    
    async def _ai_quality_score(self, content: str, section_type: str) -> float:
        """AI-powered quality scoring"""
        prompt = f"""Rate this {section_type} content quality from 0.0 to 1.0. Consider clarity, completeness, accuracy, formatting.

Content: {content[:800]}...

Return only the numeric score (e.g., 0.85)"""

        response = await asyncio.wait_for(
            self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            ),
            timeout=self.timeout
        )
        
        try:
            score = float(response.choices[0].message.content.strip())
            return max(0.0, min(1.0, score))
        except:
            return 0.5
    
    def _rule_based_detection(self, content: str) -> List[PDFIssue]:
        """Rule-based issue detection fallback"""
        issues = []
        
        # Check for common formatting issues
        if len(re.findall(r'\n\s*\n\s*\n', content)) > 5:
            issues.append(PDFIssue(
                type=IssueType.FORMATTING,
                severity=IssueSeverity.LOW,
                description="Excessive blank lines",
                location="throughout document",
                suggested_fix="Remove extra blank lines"
            ))
        
        # Check for incomplete sentences
        if content.count('.') < len(content.split('\n')) * 0.3:
            issues.append(PDFIssue(
                type=IssueType.CONTENT_QUALITY,
                severity=IssueSeverity.MEDIUM,
                description="Possible incomplete sentences",
                location="various paragraphs",
                suggested_fix="Complete sentence fragments"
            ))
        
        return issues
    
    def _rule_based_fixing(self, content: str, issues: List[PDFIssue]) -> str:
        """Rule-based content fixing fallback"""
        fixed_content = content
        
        for issue in issues:
            if issue.type == IssueType.FORMATTING and "blank lines" in issue.description:
                fixed_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', fixed_content)
        
        return self._basic_cleanup(fixed_content)
    
    def _rule_based_quality_score(self, content: str) -> float:
        """Rule-based quality scoring fallback"""
        score = 0.5  # Base score
        
        # Length factor
        if 100 <= len(content) <= 5000:
            score += 0.1
        
        # Structure factor
        if content.count('\n') > 2:
            score += 0.1
        
        # Completeness factor
        if content.count('.') > len(content.split('\n')) * 0.5:
            score += 0.2
        
        return min(1.0, score)
    
    def _basic_cleanup(self, content: str) -> str:
        """Basic content cleaning"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        # Fix line breaks
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        # Trim
        return content.strip()
    
    def _deduplicate_issues(self, issues: List[PDFIssue]) -> List[PDFIssue]:
        """Remove duplicate issues"""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            key = (issue.type, issue.description)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues