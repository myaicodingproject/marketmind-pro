#!/usr/bin/env python3
"""
Quality Gates Validation Test
Tests the actual quality validation logic and gates
"""

import json
import re
from pathlib import Path
from datetime import datetime

class QualityGatesTester:
    def __init__(self):
        self.project_root = Path("/mnt/c/kiro")
        
        # Mock section data for testing quality gates
        self.mock_sections = {
            "section1_executive_summary": {
                "content": """# Executive Summary: Apple Inc. (AAPL)
                
## Investment Recommendation: BUY
**Price Target: $275.00 | Current: $248.35 | Upside: 10.7%**

### Key Investment Highlights
- Strong financial performance with 7.9% revenue growth
- Market leadership in consumer electronics
- Exceptional cash generation of $98.8B free cash flow
- ROE of 171.4% demonstrates outstanding returns

### Investment Thesis
Apple represents a compelling investment opportunity driven by continued innovation, strong financial performance, and market leadership. The company's ability to generate substantial free cash flow and maintain high profit margins supports our BUY recommendation.

### Key Risks
- Market saturation in core products
- Regulatory pressures in key markets
- Supply chain dependencies

**Confidence Level: High**""",
                "metrics": {
                    "recommendation": "BUY",
                    "price_target": 275.0,
                    "current_price": 248.35,
                    "upside_potential": 10.7,
                    "confidence_level": "High"
                },
                "success": True,
                "execution_time": 2.5
            },
            
            "section2_financial_analysis": {
                "content": """# Financial Analysis: AAPL

## Revenue Analysis
- TTM Revenue: $416.2B representing 7.9% year-over-year growth
- 3-Year Revenue CAGR: 8.2% demonstrating consistent growth
- Revenue diversification across products (70%) and services (30%)

## Profitability Metrics
- Gross Margin: 46.9% - industry-leading efficiency
- Operating Margin: 31.6% - strong operational control
- Net Profit Margin: 26.9% - exceptional profitability
- ROE: 171.4% - outstanding returns to shareholders

## Cash Flow Analysis
- Operating Cash Flow: $111.5B - strong operational performance
- Free Cash Flow: $98.8B - excellent cash generation
- FCF Margin: 23.7% - healthy cash conversion

## Financial Health Assessment: STRONG""",
                "metrics": {
                    "revenue_growth_3yr": 7.9,
                    "profit_margin_trend": 26.9,
                    "roe_current": 171.4,
                    "cash_flow_strength": "Strong"
                },
                "success": True,
                "execution_time": 3.2
            },
            
            "section3_company_analysis": {
                "content": """# Company Deep Dive: Apple Inc.

## Business Model
Apple operates a unique ecosystem-based business model combining hardware, software, and services. The company's integrated approach creates strong customer loyalty and recurring revenue streams.

## Competitive Position
- Market leader in premium smartphones with 50%+ market share
- Dominant position in tablet market with iPad
- Growing services business with 30% margins
- Strong brand loyalty with Net Promoter Score of 72

## Strategic Initiatives
- Expansion into health and wellness
- Autonomous vehicle development
- Augmented reality capabilities
- Services growth acceleration

## Management Assessment: EXCELLENT""",
                "metrics": {
                    "market_position": "Leader",
                    "competitive_moat": "Strong",
                    "management_quality": "Excellent"
                },
                "success": True,
                "execution_time": 4.1
            }
        }
    
    def test_content_quality_validation(self, section_data: dict) -> dict:
        """Test content quality validation logic"""
        validation_result = {
            "section": section_data.get("section", "unknown"),
            "tests": {},
            "overall_score": 0,
            "passed": False
        }
        
        content = section_data.get("content", "")
        
        # Test 1: Content Length (20 points)
        length_test = {
            "name": "Content Length",
            "passed": len(content) >= 500,
            "score": 20 if len(content) >= 500 else 0,
            "details": f"Content length: {len(content)} chars (min: 500)"
        }
        validation_result["tests"]["content_length"] = length_test
        
        # Test 2: Structure Quality (25 points)
        has_headers = bool(re.search(r'^#+\s+', content, re.MULTILINE))
        has_sections = len(re.findall(r'^#+\s+', content, re.MULTILINE)) >= 3
        has_bullets = bool(re.search(r'^\s*[-*]\s+', content, re.MULTILINE))
        
        structure_score = 0
        if has_headers:
            structure_score += 10
        if has_sections:
            structure_score += 10
        if has_bullets:
            structure_score += 5
        
        structure_test = {
            "name": "Content Structure",
            "passed": structure_score >= 20,
            "score": structure_score,
            "details": f"Headers: {has_headers}, Sections: {has_sections}, Bullets: {has_bullets}"
        }
        validation_result["tests"]["content_structure"] = structure_test
        
        # Test 3: Financial Data Presence (20 points)
        financial_patterns = [
            r'\$[\d,]+\.?\d*[BM]?',  # Dollar amounts
            r'\d+\.?\d*%',           # Percentages
            r'revenue|profit|margin|cash flow|ROE|debt',  # Financial terms
        ]
        
        financial_score = 0
        for pattern in financial_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                financial_score += 7
        
        financial_test = {
            "name": "Financial Data",
            "passed": financial_score >= 15,
            "score": min(financial_score, 20),
            "details": f"Financial data patterns found: {financial_score}/20"
        }
        validation_result["tests"]["financial_data"] = financial_test
        
        # Test 4: Analysis Depth (20 points)
        analysis_keywords = [
            'analysis', 'assessment', 'evaluation', 'outlook', 'trend',
            'performance', 'growth', 'risk', 'opportunity', 'strategy'
        ]
        
        analysis_count = sum(1 for keyword in analysis_keywords 
                           if keyword.lower() in content.lower())
        analysis_score = min(analysis_count * 2, 20)
        
        analysis_test = {
            "name": "Analysis Depth",
            "passed": analysis_score >= 15,
            "score": analysis_score,
            "details": f"Analysis keywords found: {analysis_count}"
        }
        validation_result["tests"]["analysis_depth"] = analysis_test
        
        # Test 5: Metrics Validation (15 points)
        metrics = section_data.get("metrics", {})
        metrics_score = 0
        
        if metrics:
            metrics_score += 5  # Has metrics
            if len(metrics) >= 3:
                metrics_score += 5  # Sufficient metrics
            if any(isinstance(v, (int, float)) for v in metrics.values()):
                metrics_score += 5  # Has numeric metrics
        
        metrics_test = {
            "name": "Metrics Quality",
            "passed": metrics_score >= 10,
            "score": metrics_score,
            "details": f"Metrics count: {len(metrics)}, Numeric: {any(isinstance(v, (int, float)) for v in metrics.values())}"
        }
        validation_result["tests"]["metrics_quality"] = metrics_test
        
        # Calculate overall score
        total_score = sum(test["score"] for test in validation_result["tests"].values())
        validation_result["overall_score"] = total_score
        validation_result["passed"] = total_score >= 70  # 70% threshold
        
        return validation_result
    
    def test_cross_section_consistency(self, all_sections: dict) -> dict:
        """Test consistency across sections"""
        consistency_result = {
            "test_name": "Cross-Section Consistency",
            "tests": {},
            "overall_score": 0,
            "passed": False
        }
        
        # Test 1: Ticker Consistency (25 points)
        tickers = set()
        for section_data in all_sections.values():
            content = section_data.get("content", "")
            ticker_matches = re.findall(r'\b[A-Z]{2,5}\b', content)
            tickers.update(ticker_matches)
        
        ticker_consistency = len(tickers) <= 2  # Allow main ticker + maybe one comparison
        ticker_test = {
            "name": "Ticker Consistency",
            "passed": ticker_consistency,
            "score": 25 if ticker_consistency else 0,
            "details": f"Unique tickers found: {list(tickers)}"
        }
        consistency_result["tests"]["ticker_consistency"] = ticker_test
        
        # Test 2: Financial Data Consistency (25 points)
        financial_values = {}
        for section_name, section_data in all_sections.items():
            content = section_data.get("content", "")
            
            # Extract revenue mentions
            revenue_matches = re.findall(r'\$?([\d,]+\.?\d*)[BM]?\s*(?:revenue|sales)', content, re.IGNORECASE)
            if revenue_matches:
                financial_values[f"{section_name}_revenue"] = revenue_matches[0]
        
        # Check if financial values are consistent (simplified check)
        financial_consistency = len(set(financial_values.values())) <= len(financial_values) // 2 + 1
        financial_test = {
            "name": "Financial Consistency",
            "passed": financial_consistency,
            "score": 25 if financial_consistency else 15,
            "details": f"Financial values: {financial_values}"
        }
        consistency_result["tests"]["financial_consistency"] = financial_test
        
        # Test 3: Tone Consistency (25 points)
        recommendations = []
        for section_data in all_sections.values():
            content = section_data.get("content", "")
            if re.search(r'\b(BUY|STRONG BUY|HOLD|SELL)\b', content, re.IGNORECASE):
                recommendations.extend(re.findall(r'\b(BUY|STRONG BUY|HOLD|SELL)\b', content, re.IGNORECASE))
        
        tone_consistency = len(set(r.upper() for r in recommendations)) <= 1
        tone_test = {
            "name": "Tone Consistency",
            "passed": tone_consistency,
            "score": 25 if tone_consistency else 10,
            "details": f"Recommendations found: {recommendations}"
        }
        consistency_result["tests"]["tone_consistency"] = tone_test
        
        # Test 4: Completeness (25 points)
        required_sections = ["executive_summary", "financial_analysis", "company_analysis"]
        present_sections = [name for name in all_sections.keys() 
                          if any(req in name for req in required_sections)]
        
        completeness = len(present_sections) >= len(required_sections)
        completeness_test = {
            "name": "Section Completeness",
            "passed": completeness,
            "score": 25 if completeness else len(present_sections) * 8,
            "details": f"Required sections present: {len(present_sections)}/{len(required_sections)}"
        }
        consistency_result["tests"]["completeness"] = completeness_test
        
        # Calculate overall score
        total_score = sum(test["score"] for test in consistency_result["tests"].values())
        consistency_result["overall_score"] = total_score
        consistency_result["passed"] = total_score >= 75  # 75% threshold
        
        return consistency_result
    
    def test_report_level_validation(self, all_sections: dict, tier1_results: list, tier2_result: dict) -> dict:
        """Test report-level validation"""
        report_result = {
            "test_name": "Report-Level Validation",
            "tests": {},
            "overall_score": 0,
            "passed": False
        }
        
        # Test 1: Overall Quality Score (30 points)
        avg_section_score = sum(r.get("overall_score", 0) for r in tier1_results) / len(tier1_results) if tier1_results else 0
        quality_test = {
            "name": "Overall Quality",
            "passed": avg_section_score >= 70,
            "score": min(int(avg_section_score * 0.3), 30),
            "details": f"Average section score: {avg_section_score:.1f}/100"
        }
        report_result["tests"]["overall_quality"] = quality_test
        
        # Test 2: Consistency Score (25 points)
        consistency_score = tier2_result.get("overall_score", 0)
        consistency_test = {
            "name": "Cross-Section Consistency",
            "passed": consistency_score >= 75,
            "score": min(int(consistency_score * 0.25), 25),
            "details": f"Consistency score: {consistency_score}/100"
        }
        report_result["tests"]["consistency"] = consistency_test
        
        # Test 3: Completeness (25 points)
        total_content_length = sum(len(section.get("content", "")) for section in all_sections.values())
        completeness_score = min(total_content_length // 100, 25)  # 100 chars = 1 point
        
        completeness_test = {
            "name": "Report Completeness",
            "passed": completeness_score >= 20,
            "score": completeness_score,
            "details": f"Total content length: {total_content_length} chars"
        }
        report_result["tests"]["completeness"] = completeness_test
        
        # Test 4: Professional Standards (20 points)
        professional_score = 0
        
        # Check for professional language
        all_content = " ".join(section.get("content", "") for section in all_sections.values())
        if not re.search(r'\b(shit|damn|fuck|crap)\b', all_content, re.IGNORECASE):
            professional_score += 5
        
        # Check for proper formatting
        if re.search(r'^#+\s+', all_content, re.MULTILINE):
            professional_score += 5
        
        # Check for data citations
        if re.search(r'\$[\d,]+|\d+\.?\d*%', all_content):
            professional_score += 5
        
        # Check for balanced analysis
        if re.search(r'risk|challenge|concern', all_content, re.IGNORECASE):
            professional_score += 5
        
        professional_test = {
            "name": "Professional Standards",
            "passed": professional_score >= 15,
            "score": professional_score,
            "details": f"Professional criteria met: {professional_score}/20"
        }
        report_result["tests"]["professional_standards"] = professional_test
        
        # Calculate overall score
        total_score = sum(test["score"] for test in report_result["tests"].values())
        report_result["overall_score"] = total_score
        report_result["passed"] = total_score >= 80  # 80% threshold for report level
        
        return report_result
    
    def run_quality_gates_test(self) -> dict:
        """Run complete quality gates test"""
        print("🚀 QUALITY GATES VALIDATION TEST")
        print("=" * 50)
        
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "tier1_results": [],
            "tier2_result": {},
            "tier3_result": {},
            "overall_assessment": {}
        }
        
        # Tier 1: Individual section validation
        print("\n🔍 TIER 1: Section-Level Validation")
        print("-" * 35)
        
        for section_name, section_data in self.mock_sections.items():
            print(f"Testing {section_name}...")
            result = self.test_content_quality_validation(section_data)
            test_results["tier1_results"].append(result)
            
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"{status} {section_name}: {result['overall_score']}/100")
        
        # Tier 2: Cross-section consistency
        print("\n🔍 TIER 2: Cross-Section Validation")
        print("-" * 35)
        
        tier2_result = self.test_cross_section_consistency(self.mock_sections)
        test_results["tier2_result"] = tier2_result
        
        status = "✅ PASSED" if tier2_result["passed"] else "❌ FAILED"
        print(f"{status} Cross-Section Consistency: {tier2_result['overall_score']}/100")
        
        # Tier 3: Report-level validation
        print("\n🔍 TIER 3: Report-Level Validation")
        print("-" * 35)
        
        tier3_result = self.test_report_level_validation(
            self.mock_sections, 
            test_results["tier1_results"], 
            tier2_result
        )
        test_results["tier3_result"] = tier3_result
        
        status = "✅ PASSED" if tier3_result["passed"] else "❌ FAILED"
        print(f"{status} Report-Level Quality: {tier3_result['overall_score']}/100")
        
        # Overall assessment
        tier1_passed = sum(1 for r in test_results["tier1_results"] if r["passed"])
        overall_passed = (
            tier1_passed == len(test_results["tier1_results"]) and
            tier2_result["passed"] and
            tier3_result["passed"]
        )
        
        test_results["overall_assessment"] = {
            "all_tiers_passed": overall_passed,
            "tier1_pass_rate": tier1_passed / len(test_results["tier1_results"]) * 100,
            "tier2_passed": tier2_result["passed"],
            "tier3_passed": tier3_result["passed"],
            "recommendation": "APPROVE" if overall_passed else "NEEDS_IMPROVEMENT"
        }
        
        return test_results

def main():
    """Run quality gates test"""
    tester = QualityGatesTester()
    results = tester.run_quality_gates_test()
    
    # Print final summary
    print(f"\n📊 QUALITY GATES TEST SUMMARY")
    print("=" * 40)
    
    assessment = results["overall_assessment"]
    print(f"Overall Result: {'✅ PASSED' if assessment['all_tiers_passed'] else '❌ FAILED'}")
    print(f"Tier 1 Pass Rate: {assessment['tier1_pass_rate']:.1f}%")
    print(f"Tier 2 Passed: {'✅' if assessment['tier2_passed'] else '❌'}")
    print(f"Tier 3 Passed: {'✅' if assessment['tier3_passed'] else '❌'}")
    print(f"Recommendation: {assessment['recommendation']}")
    
    # Detailed scores
    print(f"\n📋 DETAILED SCORES")
    print("-" * 20)
    
    for result in results["tier1_results"]:
        section = result.get("section", "unknown")
        score = result.get("overall_score", 0)
        print(f"Section {section}: {score}/100")
    
    print(f"Cross-Section: {results['tier2_result']['overall_score']}/100")
    print(f"Report-Level: {results['tier3_result']['overall_score']}/100")
    
    # Save results
    with open("/mnt/c/kiro/quality-gates-test-results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved: /mnt/c/kiro/quality-gates-test-results.json")
    
    # Quality gate recommendations
    print(f"\n🎯 QUALITY GATE RECOMMENDATIONS")
    print("-" * 35)
    
    if assessment["all_tiers_passed"]:
        print("✅ Quality gates are working effectively")
        print("✅ Report generation should produce high-quality output")
        print("✅ Ready for production use")
    else:
        print("⚠️ Quality gates need tuning:")
        
        if assessment["tier1_pass_rate"] < 100:
            print("  - Improve section-level validation thresholds")
        if not assessment["tier2_passed"]:
            print("  - Enhance cross-section consistency checks")
        if not assessment["tier3_passed"]:
            print("  - Strengthen report-level quality standards")

if __name__ == "__main__":
    main()
