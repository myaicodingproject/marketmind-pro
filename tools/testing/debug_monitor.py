#!/usr/bin/env python3
"""
Real-time Debugging Monitor for Hybrid PDF System
Live monitoring and debugging capabilities
"""

import asyncio
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any
import logging

class RealTimeDebugMonitor:
    """Real-time monitoring and debugging for hybrid system"""
    
    def __init__(self):
        self.monitoring = False
        self.debug_data = {}
        self.setup_logging()
    
    def setup_logging(self):
        """Setup real-time logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('realtime_debug.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('RealTimeMonitor')
    
    async def monitor_openai_calls(self):
        """Monitor OpenAI API calls in real-time"""
        print("📡 Monitoring OpenAI API calls...")
        
        try:
            from openai import AsyncOpenAI
            
            # Create a wrapper to monitor calls
            original_create = AsyncOpenAI.chat.completions.create
            
            async def monitored_create(self, **kwargs):
                start_time = time.time()
                self.logger.info(f"🔄 OpenAI API Call Started")
                self.logger.info(f"   Model: {kwargs.get('model', 'unknown')}")
                self.logger.info(f"   Messages: {len(kwargs.get('messages', []))}")
                self.logger.info(f"   Max tokens: {kwargs.get('max_tokens', 'unlimited')}")
                
                try:
                    response = await original_create(**kwargs)
                    duration = time.time() - start_time
                    
                    self.logger.info(f"✅ OpenAI API Call Completed")
                    self.logger.info(f"   Duration: {duration:.2f}s")
                    self.logger.info(f"   Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
                    self.logger.info(f"   Response length: {len(response.choices[0].message.content)}")
                    
                    return response
                    
                except Exception as e:
                    duration = time.time() - start_time
                    self.logger.error(f"❌ OpenAI API Call Failed")
                    self.logger.error(f"   Duration: {duration:.2f}s")
                    self.logger.error(f"   Error: {str(e)}")
                    raise
            
            # Monkey patch for monitoring
            AsyncOpenAI.chat.completions.create = monitored_create
            
        except Exception as e:
            self.logger.error(f"Failed to setup OpenAI monitoring: {e}")
    
    async def monitor_pdf_generation(self):
        """Monitor PDF generation process"""
        print("📄 Monitoring PDF generation...")
        
        # Monitor PDF files being created
        pdf_dir = "/mnt/c/kiro"
        known_pdfs = set()
        
        while self.monitoring:
            try:
                current_pdfs = {f for f in os.listdir(pdf_dir) if f.endswith('.pdf')}
                new_pdfs = current_pdfs - known_pdfs
                
                for pdf in new_pdfs:
                    pdf_path = os.path.join(pdf_dir, pdf)
                    file_size = os.path.getsize(pdf_path)
                    self.logger.info(f"📄 New PDF created: {pdf} ({file_size:,} bytes)")
                
                known_pdfs = current_pdfs
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"PDF monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def monitor_system_health(self):
        """Monitor system health metrics"""
        print("💓 Monitoring system health...")
        
        import requests
        
        while self.monitoring:
            try:
                start_time = time.time()
                response = requests.get("http://localhost:8000/health", timeout=5)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.logger.info(f"💓 System Health: OK ({response_time:.2f}s)")
                    
                    # Log key metrics
                    if 'performance' in health_data:
                        perf = health_data['performance']
                        self.logger.info(f"   Active connections: {perf.get('active_connections', 0)}")
                else:
                    self.logger.warning(f"⚠️  System Health: {response.status_code}")
                
            except Exception as e:
                self.logger.error(f"❌ System Health: Unreachable - {e}")
            
            await asyncio.sleep(10)
    
    def debug_content_step_by_step(self, content: str):
        """Debug content enhancement step by step"""
        print(f"\n🔍 STEP-BY-STEP CONTENT DEBUG")
        print("=" * 40)
        
        # Step 1: Analyze input
        print(f"📥 INPUT ANALYSIS:")
        issues = {
            "debug_messages": "Searching for symbols" in content,
            "line_numbers": any(f"+ {i}:" in content for i in range(1, 50)),
            "git_errors": "git/objects" in content,
            "markdown_headers": "> #" in content,
            "excessive_newlines": "\n\n\n" in content
        }
        
        for issue, present in issues.items():
            status = "❌ FOUND" if present else "✅ CLEAN"
            print(f"   {issue.replace('_', ' ').title()}: {status}")
        
        print(f"   Content length: {len(content)} characters")
        print(f"   Content preview: {content[:100]}...")
        
        # Step 2: Show what needs fixing
        print(f"\n🔧 FIXES NEEDED:")
        fixes_needed = [issue for issue, present in issues.items() if present]
        
        if fixes_needed:
            for fix in fixes_needed:
                print(f"   • {fix.replace('_', ' ').title()}")
        else:
            print(f"   ✅ No fixes needed - content is clean")
        
        return issues
    
    async def debug_enhancement_live(self, content: str):
        """Debug enhancement process live"""
        print(f"\n🔄 LIVE ENHANCEMENT DEBUG")
        print("=" * 40)
        
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Step 1: Pre-enhancement analysis
            pre_issues = self.debug_content_step_by_step(content)
            
            # Step 2: Call OpenAI with monitoring
            print(f"\n🤖 CALLING OPENAI...")
            start_time = time.time()
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Clean financial report content. Remove debug messages, line numbers, system errors. Fix formatting. Preserve financial data."
                    },
                    {
                        "role": "user",
                        "content": f"Clean this content:\n{content}"
                    }
                ],
                max_tokens=500
            )
            
            duration = time.time() - start_time
            enhanced_content = response.choices[0].message.content
            
            print(f"✅ OpenAI response received ({duration:.2f}s)")
            print(f"   Tokens used: {response.usage.total_tokens}")
            print(f"   Response length: {len(enhanced_content)}")
            
            # Step 3: Post-enhancement analysis
            print(f"\n📤 OUTPUT ANALYSIS:")
            post_issues = self.debug_content_step_by_step(enhanced_content)
            
            # Step 4: Compare before/after
            print(f"\n📊 ENHANCEMENT RESULTS:")
            for issue in pre_issues:
                before = pre_issues[issue]
                after = post_issues[issue]
                
                if before and not after:
                    print(f"   ✅ Fixed: {issue.replace('_', ' ').title()}")
                elif before and after:
                    print(f"   ❌ Not fixed: {issue.replace('_', ' ').title()}")
                elif not before:
                    print(f"   ➖ N/A: {issue.replace('_', ' ').title()}")
            
            print(f"\n📝 Enhanced content preview:")
            print(f"   {enhanced_content[:200]}...")
            
            return enhanced_content
            
        except Exception as e:
            print(f"❌ Live enhancement debug failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        print("🚀 STARTING REAL-TIME DEBUG MONITORING")
        print("=" * 50)
        
        self.monitoring = True
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self.monitor_openai_calls()),
            asyncio.create_task(self.monitor_pdf_generation()),
            asyncio.create_task(self.monitor_system_health())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped by user")
            self.monitoring = False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False

# Quick debug functions
async def quick_debug_openai():
    """Quick OpenAI debug test"""
    print("⚡ QUICK OPENAI DEBUG")
    print("=" * 30)
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        start_time = time.time()
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test: Clean this text: + 7: Hello world"}],
            max_tokens=20
        )
        duration = time.time() - start_time
        
        print(f"✅ OpenAI working ({duration:.2f}s)")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        return False

def debug_environment():
    """Debug environment setup"""
    print("🔍 ENVIRONMENT DEBUG")
    print("=" * 30)
    
    checks = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
        "Working Directory": os.getcwd(),
        "Python Version": sys.version.split()[0]
    }
    
    for key, value in checks.items():
        if value:
            print(f"✅ {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
        else:
            print(f"❌ {key}: Not set")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid System Debugger")
    parser.add_argument("--mode", choices=["full", "monitor", "quick", "env"], default="full")
    parser.add_argument("--content", help="Content to debug")
    
    args = parser.parse_args()
    
    if args.mode == "env":
        debug_environment()
    elif args.mode == "quick":
        asyncio.run(quick_debug_openai())
    elif args.mode == "monitor":
        monitor = RealTimeDebugMonitor()
        asyncio.run(monitor.start_monitoring())
    elif args.mode == "full":
        from debug_hybrid_system import HybridSystemDebugger
        debugger = HybridSystemDebugger()
        asyncio.run(debugger.run_full_debug())
    
    if args.content:
        monitor = RealTimeDebugMonitor()
        asyncio.run(monitor.debug_enhancement_live(args.content))
