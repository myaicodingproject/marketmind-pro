#!/usr/bin/env python3
"""
Section Agents Quality Audit - Direct File Analysis
Analyzes section agents and quality gates without imports
"""

import json
import re
from pathlib import Path
from datetime import datetime

class SectionAgentAnalyzer:
    def __init__(self):
        self.project_root = Path("/mnt/c/kiro")
        self.results = {}
    
    def analyze_section_agent(self, agent_file: Path) -> dict:
        """Analyze a section agent file"""
        print(f"🔍 Analyzing {agent_file.name}...")
        
        try:
            content = agent_file.read_text()
            
            analysis = {
                "file": agent_file.name,
                "path": str(agent_file),
                "size_bytes": len(content),
                "lines": len(content.split('\n')),
                "analysis": {}
            }
            
            # Check class definition
            class_match = re.search(r'class\s+(\w+Agent)\s*\([^)]*\):', content)
            if class_match:
                analysis["analysis"]["class_name"] = class_match.group(1)
                analysis["analysis"]["has_class"] = True
            else:
                analysis["analysis"]["has_class"] = False
            
            # Check required methods
            methods = {
                "generate_content": bool(re.search(r'def\s+generate_content\s*\(', content)),
                "_prepare_kiro_context": bool(re.search(r'def\s+_prepare_kiro_context\s*\(', content)),
                "__init__": bool(re.search(r'def\s+__init__\s*\(', content))
            }
            analysis["analysis"]["methods"] = methods
            
            # Check prompt configurations
            has_prompt_configs = bool(re.search(r'self\.prompt_configs\s*=', content))
            analysis["analysis"]["has_prompt_configs"] = has_prompt_configs
            
            # Extract prompt files mentioned
            prompt_files = re.findall(r'[\'"]([^\'\"]*\.md)[\'"]', content)
            analysis["analysis"]["prompt_files"] = list(set(prompt_files))
            
            # Check error handling
            has_try_catch = bool(re.search(r'try:', content)) and bool(re.search(r'except', content))
            analysis["analysis"]["has_error_handling"] = has_try_catch
            
            # Check logging
            has_logging = bool(re.search(r'logger\.|logging\.', content))
            analysis["analysis"]["has_logging"] = has_logging
            
            # Check async/await usage
            has_async = bool(re.search(r'async\s+def', content))
            has_await = bool(re.search(r'await\s+', content))
            analysis["analysis"]["async_support"] = has_async and has_await
            
            # Check docstrings
            docstring_count = len(re.findall(r'"""[^"]*"""', content, re.DOTALL))
            analysis["analysis"]["docstring_count"] = docstring_count
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(analysis["analysis"])
            analysis["quality_score"] = quality_score
            
            print(f"✅ {agent_file.name}: Quality score {quality_score}/100")
            return analysis
            
        except Exception as e:
            print(f"❌ {agent_file.name}: Analysis failed - {e}")
            return {
                "file": agent_file.name,
                "error": str(e),
                "quality_score": 0
            }
    
    def _calculate_quality_score(self, analysis: dict) -> int:
        """Calculate quality score based on analysis"""
        score = 0
        
        # Basic structure (30 points)
        if analysis.get("has_class"):
            score += 10
        if analysis.get("methods", {}).get("__init__"):
            score += 5
        if analysis.get("methods", {}).get("generate_content"):
            score += 10
        if analysis.get("methods", {}).get("_prepare_kiro_context"):
            score += 5
        
        # Configuration (20 points)
        if analysis.get("has_prompt_configs"):
            score += 10
        if len(analysis.get("prompt_files", [])) > 0:
            score += 10
        
        # Code quality (30 points)
        if analysis.get("has_error_handling"):
            score += 10
        if analysis.get("has_logging"):
            score += 10
        if analysis.get("async_support"):
            score += 10
        
        # Documentation (20 points)
        docstring_count = analysis.get("docstring_count", 0)
        if docstring_count >= 3:
            score += 20
        elif docstring_count >= 1:
            score += 10
        
        return min(score, 100)
    
    def analyze_quality_system(self) -> dict:
        """Analyze the quality system"""
        print(f"🔍 Analyzing Quality System...")
        
        quality_files = [
            "app/services/quality_system.py",
            "app/api/quality_endpoints.py",
            "app/quality/models.py"
        ]
        
        quality_analysis = {
            "files_found": [],
            "files_missing": [],
            "total_quality_score": 0
        }
        
        for file_path in quality_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                quality_analysis["files_found"].append(file_path)
                
                # Analyze quality file
                content = full_path.read_text()
                
                # Check for key quality components
                has_validators = bool(re.search(r'class\s+\w*Validator', content))
                has_quality_tiers = bool(re.search(r'QualityTier|Tier[123]', content))
                has_orchestrator = bool(re.search(r'QualityOrchestrator', content))
                
                file_score = 0
                if has_validators:
                    file_score += 30
                if has_quality_tiers:
                    file_score += 30
                if has_orchestrator:
                    file_score += 40
                
                quality_analysis["total_quality_score"] += file_score
                
            else:
                quality_analysis["files_missing"].append(file_path)
        
        # Calculate overall quality system score
        max_possible = len(quality_files) * 100
        quality_analysis["quality_system_score"] = min(
            (quality_analysis["total_quality_score"] / max_possible) * 100 if max_possible > 0 else 0,
            100
        )
        
        return quality_analysis
    
    def check_prompt_files(self, prompt_files: list) -> dict:
        """Check if prompt files exist"""
        print(f"🔍 Checking Prompt Files...")
        
        prompts_dir = self.project_root / ".kiro" / "prompts"
        
        prompt_analysis = {
            "prompts_dir_exists": prompts_dir.exists(),
            "found_prompts": [],
            "missing_prompts": [],
            "total_prompts": len(set(prompt_files))
        }
        
        if prompts_dir.exists():
            for prompt_file in set(prompt_files):
                prompt_path = prompts_dir / prompt_file
                if prompt_path.exists():
                    prompt_analysis["found_prompts"].append(prompt_file)
                else:
                    prompt_analysis["missing_prompts"].append(prompt_file)
        else:
            prompt_analysis["missing_prompts"] = list(set(prompt_files))
        
        prompt_analysis["prompt_coverage"] = (
            len(prompt_analysis["found_prompts"]) / prompt_analysis["total_prompts"] * 100
            if prompt_analysis["total_prompts"] > 0 else 0
        )
        
        return prompt_analysis
    
    def run_comprehensive_audit(self) -> dict:
        """Run comprehensive audit of all section agents"""
        print("🚀 SECTION AGENTS COMPREHENSIVE AUDIT")
        print("=" * 60)
        
        # Find all section agent files
        section_files = list(self.project_root.glob("**/section*_kiro_agent.py"))
        
        audit_results = {
            "audit_timestamp": datetime.now().isoformat(),
            "total_agents": len(section_files),
            "agents": {},
            "summary": {},
            "quality_system": {},
            "prompt_analysis": {}
        }
        
        all_prompt_files = []
        total_quality_score = 0
        
        # Analyze each section agent
        for agent_file in sorted(section_files):
            analysis = self.analyze_section_agent(agent_file)
            audit_results["agents"][agent_file.stem] = analysis
            
            # Collect prompt files
            if "analysis" in analysis:
                all_prompt_files.extend(analysis["analysis"].get("prompt_files", []))
            
            # Add to total quality score
            total_quality_score += analysis.get("quality_score", 0)
        
        # Calculate summary
        audit_results["summary"] = {
            "average_quality_score": total_quality_score / len(section_files) if section_files else 0,
            "high_quality_agents": len([a for a in audit_results["agents"].values() if a.get("quality_score", 0) >= 80]),
            "medium_quality_agents": len([a for a in audit_results["agents"].values() if 60 <= a.get("quality_score", 0) < 80]),
            "low_quality_agents": len([a for a in audit_results["agents"].values() if a.get("quality_score", 0) < 60])
        }
        
        # Analyze quality system
        audit_results["quality_system"] = self.analyze_quality_system()
        
        # Check prompt files
        audit_results["prompt_analysis"] = self.check_prompt_files(all_prompt_files)
        
        return audit_results

def main():
    """Run the audit"""
    analyzer = SectionAgentAnalyzer()
    results = analyzer.run_comprehensive_audit()
    
    # Print summary
    print(f"\n📊 AUDIT SUMMARY")
    print("=" * 40)
    
    summary = results["summary"]
    print(f"Total Agents: {results['total_agents']}")
    print(f"Average Quality Score: {summary['average_quality_score']:.1f}/100")
    print(f"High Quality (80+): {summary['high_quality_agents']}")
    print(f"Medium Quality (60-79): {summary['medium_quality_agents']}")
    print(f"Low Quality (<60): {summary['low_quality_agents']}")
    
    quality_system = results["quality_system"]
    print(f"\nQuality System Score: {quality_system['quality_system_score']:.1f}/100")
    print(f"Quality Files Found: {len(quality_system['files_found'])}")
    print(f"Quality Files Missing: {len(quality_system['files_missing'])}")
    
    prompt_analysis = results["prompt_analysis"]
    print(f"\nPrompt Coverage: {prompt_analysis['prompt_coverage']:.1f}%")
    print(f"Found Prompts: {len(prompt_analysis['found_prompts'])}")
    print(f"Missing Prompts: {len(prompt_analysis['missing_prompts'])}")
    
    # Detailed agent scores
    print(f"\n📋 AGENT QUALITY SCORES")
    print("-" * 30)
    for agent_name, analysis in results["agents"].items():
        score = analysis.get("quality_score", 0)
        status = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        print(f"{status} {agent_name}: {score}/100")
    
    # Save detailed results
    with open("/mnt/c/kiro/section-agents-comprehensive-audit.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Comprehensive audit saved: /mnt/c/kiro/section-agents-comprehensive-audit.json")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS")
    print("-" * 20)
    
    if summary["average_quality_score"] >= 80:
        print("✅ Excellent: Section agents are high quality and production-ready")
    elif summary["average_quality_score"] >= 60:
        print("⚠️ Good: Section agents are functional but need improvements")
    else:
        print("❌ Poor: Section agents need significant improvements")
    
    if quality_system["quality_system_score"] >= 80:
        print("✅ Quality system is well implemented")
    else:
        print("⚠️ Quality system needs enhancement")
    
    if prompt_analysis["prompt_coverage"] >= 80:
        print("✅ Prompt files are well covered")
    else:
        print("⚠️ Missing prompt files need to be created")

if __name__ == "__main__":
    main()
