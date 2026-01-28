#!/usr/bin/env python3

import asyncio
import sys
from agents.financial_valuation_agent import FinancialValuationAgent

async def main():
    if len(sys.argv) != 2:
        print("Usage: python run_financial_valuation.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    agent = FinancialValuationAgent()
    
    print(f"🔍 Generating Financial & Valuation Analysis for {ticker}...")
    print("📊 Fetching financial data...")
    
    try:
        # Generate comprehensive 7-page analysis
        analysis = await agent.generate_combined_analysis(ticker)
        
        print("✅ Analysis Complete!")
        print(f"📈 Price Target: ${analysis['price_target']['price_target']:.2f}")
        print(f"📊 Current Price: ${analysis['price_target']['current_price']:.2f}")
        print(f"🎯 Upside: {analysis['price_target']['upside_potential']:.1%}")
        print(f"💡 Recommendation: {analysis['price_target']['recommendation']}")
        
        # Save results
        with open(f"reports/{ticker}_financial_valuation_analysis.json", "w") as f:
            import json
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"💾 Report saved to reports/{ticker}_financial_valuation_analysis.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())