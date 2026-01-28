#!/usr/bin/env python3
"""
Detailed Financial Statements Test
Shows exactly what Balance Sheet, Income Statement, and Cash Flow data we can retrieve
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime

def test_detailed_financial_statements(symbol: str):
    """Test detailed financial statements extraction"""
    print(f"📊 DETAILED FINANCIAL STATEMENTS TEST: {symbol}")
    print("=" * 60)
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get all financial statements
        income_stmt = ticker.income_stmt
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cash_flow
        quarterly_income = ticker.quarterly_income_stmt
        quarterly_balance = ticker.quarterly_balance_sheet
        quarterly_cashflow = ticker.quarterly_cash_flow
        
        results = {
            "symbol": symbol,
            "test_timestamp": datetime.now().isoformat(),
            "financial_statements": {}
        }
        
        # 1. INCOME STATEMENT ANALYSIS
        print(f"\n💰 INCOME STATEMENT")
        print("-" * 30)
        
        if not income_stmt.empty:
            income_data = {}
            latest_year = income_stmt.columns[0]
            
            # Key income statement items
            income_items = [
                'Total Revenue', 'Cost Of Revenue', 'Gross Profit',
                'Operating Expense', 'Operating Income', 'Net Income',
                'EBITDA', 'Basic EPS', 'Diluted EPS'
            ]
            
            print(f"📅 Latest Year: {latest_year}")
            print(f"📊 Available Periods: {len(income_stmt.columns)}")
            print(f"📋 Available Items: {len(income_stmt.index)}")
            
            for item in income_items:
                if item in income_stmt.index:
                    value = income_stmt.loc[item, latest_year]
                    income_data[item] = float(value) if pd.notna(value) else None
                    print(f"   - {item}: ${value:,.0f}" if pd.notna(value) else f"   - {item}: N/A")
                else:
                    income_data[item] = None
                    print(f"   - {item}: Not Available")
            
            results["financial_statements"]["income_statement"] = {
                "available": True,
                "periods": len(income_stmt.columns),
                "latest_period": str(latest_year),
                "data": income_data,
                "all_items": list(income_stmt.index)
            }
        else:
            print("❌ Income Statement not available")
            results["financial_statements"]["income_statement"] = {"available": False}
        
        # 2. BALANCE SHEET ANALYSIS
        print(f"\n🏦 BALANCE SHEET")
        print("-" * 30)
        
        if not balance_sheet.empty:
            balance_data = {}
            latest_year = balance_sheet.columns[0]
            
            # Key balance sheet items
            balance_items = [
                'Total Assets', 'Current Assets', 'Cash And Cash Equivalents',
                'Total Liabilities', 'Current Liabilities', 'Total Debt',
                'Stockholders Equity', 'Retained Earnings', 'Working Capital'
            ]
            
            print(f"📅 Latest Year: {latest_year}")
            print(f"📊 Available Periods: {len(balance_sheet.columns)}")
            print(f"📋 Available Items: {len(balance_sheet.index)}")
            
            for item in balance_items:
                if item in balance_sheet.index:
                    value = balance_sheet.loc[item, latest_year]
                    balance_data[item] = float(value) if pd.notna(value) else None
                    print(f"   - {item}: ${value:,.0f}" if pd.notna(value) else f"   - {item}: N/A")
                else:
                    balance_data[item] = None
                    print(f"   - {item}: Not Available")
            
            results["financial_statements"]["balance_sheet"] = {
                "available": True,
                "periods": len(balance_sheet.columns),
                "latest_period": str(latest_year),
                "data": balance_data,
                "all_items": list(balance_sheet.index)
            }
        else:
            print("❌ Balance Sheet not available")
            results["financial_statements"]["balance_sheet"] = {"available": False}
        
        # 3. CASH FLOW ANALYSIS
        print(f"\n💸 CASH FLOW STATEMENT")
        print("-" * 30)
        
        if not cash_flow.empty:
            cashflow_data = {}
            latest_year = cash_flow.columns[0]
            
            # Key cash flow items
            cashflow_items = [
                'Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow',
                'Free Cash Flow', 'Capital Expenditure', 'Depreciation And Amortization'
            ]
            
            print(f"📅 Latest Year: {latest_year}")
            print(f"📊 Available Periods: {len(cash_flow.columns)}")
            print(f"📋 Available Items: {len(cash_flow.index)}")
            
            for item in cashflow_items:
                if item in cash_flow.index:
                    value = cash_flow.loc[item, latest_year]
                    cashflow_data[item] = float(value) if pd.notna(value) else None
                    print(f"   - {item}: ${value:,.0f}" if pd.notna(value) else f"   - {item}: N/A")
                else:
                    cashflow_data[item] = None
                    print(f"   - {item}: Not Available")
            
            results["financial_statements"]["cash_flow"] = {
                "available": True,
                "periods": len(cash_flow.columns),
                "latest_period": str(latest_year),
                "data": cashflow_data,
                "all_items": list(cash_flow.index)
            }
        else:
            print("❌ Cash Flow Statement not available")
            results["financial_statements"]["cash_flow"] = {"available": False}
        
        # 4. QUARTERLY DATA AVAILABILITY
        print(f"\n📅 QUARTERLY DATA AVAILABILITY")
        print("-" * 30)
        
        quarterly_data = {
            "income_statement": {
                "available": not quarterly_income.empty,
                "periods": len(quarterly_income.columns) if not quarterly_income.empty else 0
            },
            "balance_sheet": {
                "available": not quarterly_balance.empty,
                "periods": len(quarterly_balance.columns) if not quarterly_balance.empty else 0
            },
            "cash_flow": {
                "available": not quarterly_cashflow.empty,
                "periods": len(quarterly_cashflow.columns) if not quarterly_cashflow.empty else 0
            }
        }
        
        for statement, data in quarterly_data.items():
            status = "✅" if data["available"] else "❌"
            print(f"   {status} {statement.replace('_', ' ').title()}: {data['periods']} quarters")
        
        results["quarterly_data"] = quarterly_data
        
        # 5. DATA QUALITY SUMMARY
        print(f"\n📊 DATA QUALITY SUMMARY")
        print("-" * 30)
        
        total_statements = 3
        available_statements = sum([
            1 if results["financial_statements"]["income_statement"]["available"] else 0,
            1 if results["financial_statements"]["balance_sheet"]["available"] else 0,
            1 if results["financial_statements"]["cash_flow"]["available"] else 0
        ])
        
        print(f"   - Annual Statements: {available_statements}/{total_statements} available")
        print(f"   - Quarterly Data: {sum(1 for d in quarterly_data.values() if d['available'])}/3 available")
        print(f"   - Data Completeness: {(available_statements/total_statements)*100:.1f}%")
        
        results["data_quality"] = {
            "annual_statements_available": available_statements,
            "total_statements": total_statements,
            "quarterly_available": sum(1 for d in quarterly_data.values() if d['available']),
            "completeness_percentage": (available_statements/total_statements)*100
        }
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing {symbol}: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "success": False
        }

def main():
    """Test multiple symbols for financial statements"""
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    
    print("🚀 COMPREHENSIVE FINANCIAL STATEMENTS TEST")
    print("=" * 80)
    
    all_results = {}
    
    for symbol in symbols:
        print(f"\n\n🎯 TESTING {symbol}")
        print("=" * 80)
        
        result = test_detailed_financial_statements(symbol)
        all_results[symbol] = result
        
        if result.get("data_quality"):
            quality = result["data_quality"]
            print(f"\n✅ {symbol} Summary: {quality['completeness_percentage']:.1f}% data completeness")
    
    # Save detailed results
    with open("/mnt/c/kiro/detailed-financial-statements-test.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n\n📊 FINAL SUMMARY")
    print("=" * 50)
    
    for symbol, result in all_results.items():
        if result.get("data_quality"):
            quality = result["data_quality"]
            print(f"   - {symbol}: {quality['annual_statements_available']}/3 annual, {quality['quarterly_available']}/3 quarterly")
        else:
            print(f"   - {symbol}: Test failed")
    
    print(f"\n💾 Detailed results saved: /mnt/c/kiro/detailed-financial-statements-test.json")

if __name__ == "__main__":
    main()
