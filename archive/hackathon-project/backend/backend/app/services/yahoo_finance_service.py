"""
Yahoo Finance Service - Comprehensive market data integration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class YahooFinanceService:
    def __init__(self):
        self.session = None
        
    async def get_ticker_info(self, symbol: str) -> Dict:
        """Get comprehensive ticker information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName')),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
                'profit_margins': info.get('profitMargins'),
                'operating_margins': info.get('operatingMargins'),
                'return_on_assets': info.get('returnOnAssets'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'current_ratio': info.get('currentRatio'),
                'debt_to_equity': info.get('debtToEquity'),
                'gross_margins': info.get('grossMargins'),
                'ebitda_margins': info.get('ebitdaMargins'),
                'operating_cash_flow': info.get('operatingCashflow'),
                'free_cash_flow': info.get('freeCashflow'),
                'total_cash': info.get('totalCash'),
                'total_debt': info.get('totalDebt'),
                'total_revenue': info.get('totalRevenue'),
                'revenue_per_share': info.get('revenuePerShare'),
                'earnings_per_share': info.get('trailingEps'),
                'book_value': info.get('bookValue'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares'),
                'held_percent_insiders': info.get('heldPercentInsiders'),
                'held_percent_institutions': info.get('heldPercentInstitutions'),
                'short_ratio': info.get('shortRatio'),
                'short_percent_of_float': info.get('shortPercentOfFloat'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                '50_day_average': info.get('fiftyDayAverage'),
                '200_day_average': info.get('twoHundredDayAverage'),
                'dividend_rate': info.get('dividendRate'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'ex_dividend_date': info.get('exDividendDate'),
                'last_dividend_date': info.get('lastDividendDate'),
                'target_high_price': info.get('targetHighPrice'),
                'target_low_price': info.get('targetLowPrice'),
                'target_mean_price': info.get('targetMeanPrice'),
                'recommendation_mean': info.get('recommendationMean'),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting ticker info for {symbol}: {e}")
            raise

    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get historical price data with various intervals"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                raise ValueError(f"No historical data found for {symbol}")
            
            # Add technical indicators
            hist = self._add_technical_indicators(hist)
            
            return hist
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            raise

    async def get_financial_statements(self, symbol: str) -> Dict:
        """Get all financial statements"""
        try:
            ticker = yf.Ticker(symbol)
            
            return {
                'symbol': symbol,
                'income_statement': {
                    'annual': ticker.financials.to_dict() if not ticker.financials.empty else {},
                    'quarterly': ticker.quarterly_financials.to_dict() if not ticker.quarterly_financials.empty else {}
                },
                'balance_sheet': {
                    'annual': ticker.balance_sheet.to_dict() if not ticker.balance_sheet.empty else {},
                    'quarterly': ticker.quarterly_balance_sheet.to_dict() if not ticker.quarterly_balance_sheet.empty else {}
                },
                'cash_flow': {
                    'annual': ticker.cashflow.to_dict() if not ticker.cashflow.empty else {},
                    'quarterly': ticker.quarterly_cashflow.to_dict() if not ticker.quarterly_cashflow.empty else {}
                },
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting financial statements for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_earnings_data(self, symbol: str) -> Dict:
        """Get earnings data and estimates"""
        try:
            ticker = yf.Ticker(symbol)
            
            return {
                'symbol': symbol,
                'earnings': ticker.earnings.to_dict() if not ticker.earnings.empty else {},
                'quarterly_earnings': ticker.quarterly_earnings.to_dict() if not ticker.quarterly_earnings.empty else {},
                'earnings_dates': ticker.earnings_dates.to_dict() if hasattr(ticker, 'earnings_dates') and not ticker.earnings_dates.empty else {},
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting earnings data for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_analyst_recommendations(self, symbol: str) -> Dict:
        """Get analyst recommendations and price targets"""
        try:
            ticker = yf.Ticker(symbol)
            
            recommendations = {}
            if hasattr(ticker, 'recommendations') and ticker.recommendations is not None:
                recommendations = ticker.recommendations.to_dict()
            
            upgrades_downgrades = {}
            if hasattr(ticker, 'upgrades_downgrades') and ticker.upgrades_downgrades is not None:
                upgrades_downgrades = ticker.upgrades_downgrades.to_dict()
            
            return {
                'symbol': symbol,
                'recommendations': recommendations,
                'upgrades_downgrades': upgrades_downgrades,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting analyst recommendations for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_institutional_holders(self, symbol: str) -> Dict:
        """Get institutional and mutual fund holders"""
        try:
            ticker = yf.Ticker(symbol)
            
            return {
                'symbol': symbol,
                'institutional_holders': ticker.institutional_holders.to_dict() if not ticker.institutional_holders.empty else {},
                'mutualfund_holders': ticker.mutualfund_holders.to_dict() if not ticker.mutualfund_holders.empty else {},
                'major_holders': ticker.major_holders.to_dict() if not ticker.major_holders.empty else {},
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting institutional holders for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_options_data(self, symbol: str) -> Dict:
        """Get options chain data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            
            options_data = {
                'symbol': symbol,
                'expiration_dates': list(expirations),
                'chains': {},
                'last_updated': datetime.now().isoformat()
            }
            
            # Get options chain for next 3 expiration dates
            for exp_date in expirations[:3]:
                try:
                    opt_chain = ticker.option_chain(exp_date)
                    options_data['chains'][exp_date] = {
                        'calls': opt_chain.calls.to_dict() if not opt_chain.calls.empty else {},
                        'puts': opt_chain.puts.to_dict() if not opt_chain.puts.empty else {}
                    }
                except:
                    continue
            
            return options_data
        except Exception as e:
            logger.error(f"Error getting options data for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_dividend_history(self, symbol: str) -> Dict:
        """Get dividend payment history"""
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            
            if dividends.empty:
                return {'symbol': symbol, 'dividends': {}, 'last_updated': datetime.now().isoformat()}
            
            return {
                'symbol': symbol,
                'dividends': dividends.to_dict(),
                'dividend_summary': {
                    'total_dividends_last_year': float(dividends.last('365D').sum()),
                    'average_dividend': float(dividends.mean()),
                    'dividend_growth_rate': self._calculate_dividend_growth(dividends),
                    'last_dividend': float(dividends.iloc[-1]) if len(dividends) > 0 else 0,
                    'last_dividend_date': dividends.index[-1].isoformat() if len(dividends) > 0 else None
                },
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting dividend history for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_stock_splits(self, symbol: str) -> Dict:
        """Get stock split history"""
        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits
            
            return {
                'symbol': symbol,
                'splits': splits.to_dict() if not splits.empty else {},
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting stock splits for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_market_data_summary(self, symbol: str) -> Dict:
        """Get comprehensive market data summary"""
        try:
            # Run multiple data fetches concurrently
            tasks = [
                self.get_ticker_info(symbol),
                self.get_historical_data(symbol, "1y"),
                self.get_earnings_data(symbol),
                self.get_analyst_recommendations(symbol),
                self.get_dividend_history(symbol)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            ticker_info = results[0] if not isinstance(results[0], Exception) else {}
            historical_data = results[1] if not isinstance(results[1], Exception) else pd.DataFrame()
            earnings_data = results[2] if not isinstance(results[2], Exception) else {}
            analyst_data = results[3] if not isinstance(results[3], Exception) else {}
            dividend_data = results[4] if not isinstance(results[4], Exception) else {}
            
            # Calculate additional metrics
            summary = {
                'symbol': symbol,
                'basic_info': ticker_info,
                'price_performance': self._calculate_price_performance(historical_data),
                'volatility_metrics': self._calculate_volatility_metrics(historical_data),
                'earnings_summary': earnings_data,
                'analyst_summary': analyst_data,
                'dividend_summary': dividend_data,
                'last_updated': datetime.now().isoformat()
            }
            
            return summary
        except Exception as e:
            logger.error(f"Error getting market data summary for {symbol}: {e}")
            raise

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to historical data"""
        try:
            # Simple Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
            
            return df
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return df

    def _calculate_price_performance(self, df: pd.DataFrame) -> Dict:
        """Calculate price performance metrics"""
        if df.empty:
            return {}
        
        try:
            current_price = df['Close'].iloc[-1]
            
            performance = {
                '1_day': self._calculate_return(df, 1),
                '1_week': self._calculate_return(df, 7),
                '1_month': self._calculate_return(df, 30),
                '3_months': self._calculate_return(df, 90),
                '6_months': self._calculate_return(df, 180),
                '1_year': self._calculate_return(df, 365),
                'ytd': self._calculate_ytd_return(df),
                '52_week_high': float(df['High'].max()),
                '52_week_low': float(df['Low'].min()),
                'current_price': float(current_price)
            }
            
            return performance
        except Exception as e:
            logger.error(f"Error calculating price performance: {e}")
            return {}

    def _calculate_volatility_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate volatility and risk metrics"""
        if df.empty:
            return {}
        
        try:
            returns = df['Close'].pct_change().dropna()
            
            volatility = {
                'daily_volatility': float(returns.std()),
                'annualized_volatility': float(returns.std() * np.sqrt(252)),
                'sharpe_ratio': self._calculate_sharpe_ratio(returns),
                'max_drawdown': self._calculate_max_drawdown(df['Close']),
                'var_95': float(returns.quantile(0.05)),
                'var_99': float(returns.quantile(0.01))
            }
            
            return volatility
        except Exception as e:
            logger.error(f"Error calculating volatility metrics: {e}")
            return {}

    def _calculate_return(self, df: pd.DataFrame, days: int) -> Optional[float]:
        """Calculate return over specified number of days"""
        try:
            if len(df) < days:
                return None
            
            current_price = df['Close'].iloc[-1]
            past_price = df['Close'].iloc[-days]
            return float((current_price - past_price) / past_price * 100)
        except:
            return None

    def _calculate_ytd_return(self, df: pd.DataFrame) -> Optional[float]:
        """Calculate year-to-date return"""
        try:
            current_year = datetime.now().year
            ytd_data = df[df.index.year == current_year]
            
            if ytd_data.empty:
                return None
            
            start_price = ytd_data['Close'].iloc[0]
            current_price = ytd_data['Close'].iloc[-1]
            return float((current_price - start_price) / start_price * 100)
        except:
            return None

    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        try:
            excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
            return float(excess_returns.mean() / excess_returns.std() * np.sqrt(252))
        except:
            return 0.0

    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            peak = prices.expanding().max()
            drawdown = (prices - peak) / peak
            return float(drawdown.min() * 100)
        except:
            return 0.0

    def _calculate_dividend_growth(self, dividends: pd.Series) -> Optional[float]:
        """Calculate dividend growth rate"""
        try:
            if len(dividends) < 2:
                return None
            
            # Get annual dividend totals
            annual_dividends = dividends.groupby(dividends.index.year).sum()
            
            if len(annual_dividends) < 2:
                return None
            
            # Calculate compound annual growth rate
            years = len(annual_dividends) - 1
            start_div = annual_dividends.iloc[0]
            end_div = annual_dividends.iloc[-1]
            
            if start_div <= 0:
                return None
            
            growth_rate = (end_div / start_div) ** (1 / years) - 1
            return float(growth_rate * 100)
        except:
            return None

# Global instance
yahoo_finance_service = YahooFinanceService()