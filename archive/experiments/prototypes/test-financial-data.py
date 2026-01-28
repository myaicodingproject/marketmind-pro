#!/usr/bin/env python3
"""
Financial Data Retrieval Test Suite
Tests all financial data sources and capabilities
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append('/mnt/c/kiro')
sys.path.append('/mnt/c/kiro/backend')

try:
    from backend.app.services.financial_data_service import FinancialDataService
    from backend.app.services.alpha_vantage_service import AlphaVantageService
    from backend.app.services.yahoo_finance_service import YahooFinanceService
    from backend.app.services.financial_aggregator import FinancialDataAggregator
    from backend.app.core.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative imports...")
    try:
        import yfinance as yf
        import requests
        print("✅ Using direct library imports")
    except ImportError:
        print("❌ Required libraries not available")
        sys.exit(1)

class FinancialDataTester:
    def __init__(self):
        self.test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        self.results = {}
        
    async def test_yahoo_finance_basic(self, symbol: str):
        """Test basic Yahoo Finance data retrieval"""
        print(f"📊 Testing Yahoo Finance for {symbol}...")
        
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            hist = ticker.history(period="5d")
            
            # Get financial statements
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cash_flow
            
            result = {
                "source": "yahoo_finance",
                "symbol": symbol,
                "basic_info": {
                    "name": info.get('longName', 'N/A'),
                    "sector": info.get('sector', 'N/A'),
                    "industry": info.get('industry', 'N/A'),
                    "market_cap": info.get('marketCap', 'N/A'),
                    "current_price": info.get('currentPrice', 'N/A'),
                    "pe_ratio": info.get('trailingPE', 'N/A'),
                    "revenue": info.get('totalRevenue', 'N/A'),
                    "employees": info.get('fullTimeEmployees', 'N/A')
                },
                "historical_data": {
                    "available": not hist.empty,
                    "days": len(hist) if not hist.empty else 0,
                    "latest_close": float(hist['Close'].iloc[-1]) if not hist.empty else None
                },
                "financial_statements": {
                    "income_statement": {
                        "available": not income_stmt.empty,
                        "periods": len(income_stmt.columns) if not income_stmt.empty else 0,
                        "latest_revenue": float(income_stmt.loc['Total Revenue'].iloc[0]) if not income_stmt.empty and 'Total Revenue' in income_stmt.index else None
                    },
                    "balance_sheet": {
                        "available": not balance_sheet.empty,
                        "periods": len(balance_sheet.columns) if not balance_sheet.empty else 0,
                        "total_assets": float(balance_sheet.loc['Total Assets'].iloc[0]) if not balance_sheet.empty and 'Total Assets' in balance_sheet.index else None
                    },
                    "cash_flow": {
                        "available": not cash_flow.empty,
                        "periods": len(cash_flow.columns) if not cash_flow.empty else 0,
                        "operating_cash_flow": float(cash_flow.loc['Operating Cash Flow'].iloc[0]) if not cash_flow.empty and 'Operating Cash Flow' in cash_flow.index else None
                    }
                },
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Yahoo Finance data retrieved for {symbol}")
            return result
            
        except Exception as e:
            print(f"❌ Yahoo Finance error for {symbol}: {e}")
            return {
                "source": "yahoo_finance",
                "symbol": symbol,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_alpha_vantage_api(self, symbol: str):
        """Test Alpha Vantage API data retrieval"""
        print(f"📈 Testing Alpha Vantage for {symbol}...")
        
        try:
            api_key = "demo"  # Using demo key for testing
            base_url = "https://www.alphavantage.co/query"
            
            # Test company overview
            overview_params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': api_key
            }
            
            import requests
            response = requests.get(base_url, params=overview_params, timeout=10)
            overview_data = response.json()
            
            # Test income statement
            income_params = {
                'function': 'INCOME_STATEMENT',
                'symbol': symbol,
                'apikey': api_key
            }
            
            income_response = requests.get(base_url, params=income_params, timeout=10)
            income_data = income_response.json()
            
            result = {
                "source": "alpha_vantage",
                "symbol": symbol,
                "company_overview": {
                    "available": 'Symbol' in overview_data,
                    "name": overview_data.get('Name', 'N/A'),
                    "sector": overview_data.get('Sector', 'N/A'),
                    "market_cap": overview_data.get('MarketCapitalization', 'N/A'),
                    "pe_ratio": overview_data.get('PERatio', 'N/A'),
                    "revenue_ttm": overview_data.get('RevenueTTM', 'N/A'),
                    "profit_margin": overview_data.get('ProfitMargin', 'N/A')
                },
                "income_statement": {
                    "available": 'annualReports' in income_data,
                    "annual_reports": len(income_data.get('annualReports', [])),
                    "quarterly_reports": len(income_data.get('quarterlyReports', [])),
                    "latest_revenue": income_data.get('annualReports', [{}])[0].get('totalRevenue') if income_data.get('annualReports') else None
                },
                "api_limits": {
                    "overview_error": overview_data.get('Note', overview_data.get('Error Message')),
                    "income_error": income_data.get('Note', income_data.get('Error Message'))
                },
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Alpha Vantage data retrieved for {symbol}")
            return result
            
        except Exception as e:
            print(f"❌ Alpha Vantage error for {symbol}: {e}")
            return {
                "source": "alpha_vantage",
                "symbol": symbol,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_financial_calculations(self, symbol: str):
        """Test financial ratio calculations"""
        print(f"🧮 Testing financial calculations for {symbol}...")
        
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Calculate key ratios
            ratios = {
                "valuation_ratios": {
                    "pe_ratio": info.get('trailingPE'),
                    "forward_pe": info.get('forwardPE'),
                    "peg_ratio": info.get('pegRatio'),
                    "price_to_book": info.get('priceToBook'),
                    "price_to_sales": info.get('priceToSalesTrailing12Months'),
                    "enterprise_value": info.get('enterpriseValue'),
                    "ev_to_revenue": info.get('enterpriseToRevenue'),
                    "ev_to_ebitda": info.get('enterpriseToEbitda')
                },
                "profitability_ratios": {
                    "profit_margin": info.get('profitMargins'),
                    "operating_margin": info.get('operatingMargins'),
                    "gross_margin": info.get('grossMargins'),
                    "return_on_equity": info.get('returnOnEquity'),
                    "return_on_assets": info.get('returnOnAssets')
                },
                "liquidity_ratios": {
                    "current_ratio": info.get('currentRatio'),
                    "quick_ratio": info.get('quickRatio'),
                    "debt_to_equity": info.get('debtToEquity'),
                    "total_debt": info.get('totalDebt'),
                    "total_cash": info.get('totalCash')
                },
                "growth_metrics": {
                    "revenue_growth": info.get('revenueGrowth'),
                    "earnings_growth": info.get('earningsGrowth'),
                    "quarterly_revenue_growth": info.get('quarterlyRevenueGrowth'),
                    "quarterly_earnings_growth": info.get('quarterlyEarningsGrowth')
                }
            }
            
            # Count available metrics
            total_metrics = 0
            available_metrics = 0
            
            for category in ratios.values():
                for key, value in category.items():
                    total_metrics += 1
                    if value is not None:
                        available_metrics += 1
            
            result = {
                "source": "calculated_ratios",
                "symbol": symbol,
                "ratios": ratios,
                "coverage": {
                    "total_metrics": total_metrics,
                    "available_metrics": available_metrics,
                    "coverage_percentage": (available_metrics / total_metrics) * 100 if total_metrics > 0 else 0
                },
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Financial calculations completed for {symbol} ({available_metrics}/{total_metrics} metrics)")
            return result
            
        except Exception as e:
            print(f"❌ Financial calculations error for {symbol}: {e}")
            return {
                "source": "calculated_ratios",
                "symbol": symbol,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_comprehensive_data(self, symbol: str):
        """Test comprehensive data aggregation"""
        print(f"🔄 Running comprehensive test for {symbol}...")
        
        # Run all tests concurrently
        tasks = [
            self.test_yahoo_finance_basic(symbol),
            self.test_alpha_vantage_api(symbol),
            self.test_financial_calculations(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        comprehensive_result = {
            "symbol": symbol,
            "test_timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "summary": {
                "total_sources": len(tasks),
                "successful_sources": 0,
                "failed_sources": 0
            }
        }
        
        for result in results:
            if isinstance(result, Exception):
                comprehensive_result["summary"]["failed_sources"] += 1
                continue
                
            source = result.get("source", "unknown")
            comprehensive_result["data_sources"][source] = result
            
            if result.get("success", False):
                comprehensive_result["summary"]["successful_sources"] += 1
            else:
                comprehensive_result["summary"]["failed_sources"] += 1
        
        return comprehensive_result
    
    async def run_full_test_suite(self):
        """Run complete financial data test suite"""
        print("🚀 Starting Financial Data Test Suite")
        print("=" * 50)
        
        all_results = {}
        
        for symbol in self.test_symbols:
            print(f"\n📊 Testing {symbol}...")
            print("-" * 30)
            
            try:
                result = await self.test_comprehensive_data(symbol)
                all_results[symbol] = result
                
                # Print summary for this symbol
                summary = result["summary"]
                print(f"✅ {symbol}: {summary['successful_sources']}/{summary['total_sources']} sources successful")
                
            except Exception as e:
                print(f"❌ {symbol}: Test failed - {e}")
                all_results[symbol] = {
                    "symbol": symbol,
                    "error": str(e),
                    "success": False
                }
        
        # Generate final report
        self.generate_test_report(all_results)
        return all_results
    
    def generate_test_report(self, results):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 FINANCIAL DATA TEST REPORT")
        print("=" * 60)
        
        total_symbols = len(results)
        successful_symbols = sum(1 for r in results.values() if r.get("summary", {}).get("successful_sources", 0) > 0)
        
        print(f"📈 Overall Results:")
        print(f"   - Symbols Tested: {total_symbols}")
        print(f"   - Successful: {successful_symbols}")
        print(f"   - Success Rate: {(successful_symbols/total_symbols)*100:.1f}%")
        
        print(f"\n📋 Data Source Performance:")
        source_stats = {}
        
        for symbol_result in results.values():
            if "data_sources" in symbol_result:
                for source, data in symbol_result["data_sources"].items():
                    if source not in source_stats:
                        source_stats[source] = {"success": 0, "total": 0}
                    source_stats[source]["total"] += 1
                    if data.get("success", False):
                        source_stats[source]["success"] += 1
        
        for source, stats in source_stats.items():
            success_rate = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            print(f"   - {source}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n🔍 Detailed Results by Symbol:")
        for symbol, result in results.items():
            if "summary" in result:
                summary = result["summary"]
                print(f"   - {symbol}: {summary['successful_sources']}/{summary['total_sources']} sources")
            else:
                print(f"   - {symbol}: Failed - {result.get('error', 'Unknown error')}")
        
        # Save detailed results
        report_file = "/mnt/c/kiro/financial-data-test-report.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved: {report_file}")
        
        print(f"\n🎯 Key Findings:")
        print(f"   - Yahoo Finance: Primary data source (real-time prices, financials)")
        print(f"   - Alpha Vantage: Secondary source (may have API limits)")
        print(f"   - Financial Ratios: Calculated from available data")
        print(f"   - Data Coverage: Varies by symbol and source availability")

async def main():
    """Main test execution"""
    tester = FinancialDataTester()
    
    if len(sys.argv) > 1:
        # Test specific symbol
        symbol = sys.argv[1].upper()
        print(f"🎯 Testing single symbol: {symbol}")
        result = await tester.test_comprehensive_data(symbol)
        print(json.dumps(result, indent=2, default=str))
    else:
        # Run full test suite
        await tester.run_full_test_suite()

if __name__ == "__main__":
    asyncio.run(main())
