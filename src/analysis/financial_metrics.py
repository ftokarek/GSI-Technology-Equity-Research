"""
Financial Metrics Calculator for GSI Technology Equity Analysis
Calculates comprehensive financial ratios and metrics for investment analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class FinancialMetricsCalculator:
    """
    Comprehensive financial metrics calculator for equity analysis
    """
    
    def __init__(self, income_data: pd.DataFrame, balance_data: pd.DataFrame, 
                 market_data: Optional[pd.DataFrame] = None):
        """
        Initialize with financial data
        
        Args:
            income_data: Income statement data
            balance_data: Balance sheet data  
            market_data: Market data (optional)
        """
        self.income = income_data.copy()
        self.balance = balance_data.copy()
        self.market = market_data.copy() if market_data is not None else None
        
        # Ensure data is sorted by year
        self.income = self.income.sort_values('year').reset_index(drop=True)
        self.balance = self.balance.sort_values('year').reset_index(drop=True)
        
    def calculate_growth_metrics(self) -> pd.DataFrame:
        """
        Calculate revenue and profitability growth metrics
        """
        metrics = []
        
        for i, row in self.income.iterrows():
            year = int(row['year'])
            revenue = row.get('revenue', np.nan)
            
            # Revenue growth
            if i > 0:
                prev_revenue = self.income.iloc[i-1].get('revenue', np.nan)
                if pd.notna(prev_revenue) and prev_revenue > 0:
                    revenue_growth = ((revenue - prev_revenue) / prev_revenue) * 100
                else:
                    revenue_growth = np.nan
            else:
                revenue_growth = np.nan
            
            # 3-year CAGR
            if i >= 2:
                revenue_3y_ago = self.income.iloc[i-2].get('revenue', np.nan)
                if pd.notna(revenue_3y_ago) and revenue_3y_ago > 0:
                    cagr_3y = ((revenue / revenue_3y_ago) ** (1/3) - 1) * 100
                else:
                    cagr_3y = np.nan
            else:
                cagr_3y = np.nan
            
            # 5-year CAGR
            if i >= 4:
                revenue_5y_ago = self.income.iloc[i-4].get('revenue', np.nan)
                if pd.notna(revenue_5y_ago) and revenue_5y_ago > 0:
                    cagr_5y = ((revenue / revenue_5y_ago) ** (1/5) - 1) * 100
                else:
                    cagr_5y = np.nan
            else:
                cagr_5y = np.nan
            
            # 10-year CAGR
            if i >= 9:
                revenue_10y_ago = self.income.iloc[i-9].get('revenue', np.nan)
                if pd.notna(revenue_10y_ago) and revenue_10y_ago > 0:
                    cagr_10y = ((revenue / revenue_10y_ago) ** (1/10) - 1) * 100
                else:
                    cagr_10y = np.nan
            else:
                cagr_10y = np.nan
            
            metrics.append({
                'year': year,
                'revenue': revenue,
                'revenue_growth_yoy': revenue_growth,
                'revenue_cagr_3y': cagr_3y,
                'revenue_cagr_5y': cagr_5y,
                'revenue_cagr_10y': cagr_10y
            })
        
        return pd.DataFrame(metrics)
    
    def calculate_profitability_metrics(self) -> pd.DataFrame:
        """
        Calculate profitability margins and ratios
        """
        metrics = []
        
        for i, row in self.income.iterrows():
            year = int(row['year'])
            revenue = row.get('revenue', np.nan)
            gross_profit = row.get('gross_profit', np.nan)
            operating_expenses = row.get('operating_expenses', np.nan)
            net_income = row.get('net_income', np.nan)
            
            if pd.notna(gross_profit) and pd.notna(operating_expenses):
                ebit = gross_profit - operating_expenses
            else:
                ebit = np.nan
            
            # Note: We don't have depreciation data, so EBITDA ≈ EBIT
            ebitda = ebit
            
            # Margins
            gross_margin = (gross_profit / revenue * 100) if pd.notna(gross_profit) and pd.notna(revenue) and revenue > 0 else np.nan
            operating_margin = (ebit / revenue * 100) if pd.notna(ebit) and pd.notna(revenue) and revenue > 0 else np.nan
            net_margin = (net_income / revenue * 100) if pd.notna(net_income) and pd.notna(revenue) and revenue > 0 else np.nan
            
            metrics.append({
                'year': year,
                'revenue': revenue,
                'gross_profit': gross_profit,
                'ebit': ebit,
                'ebitda': ebitda,
                'net_income': net_income,
                'gross_margin': gross_margin,
                'operating_margin': operating_margin,
                'net_margin': net_margin
            })
        
        return pd.DataFrame(metrics)
    
    def calculate_balance_sheet_metrics(self) -> pd.DataFrame:
        """
        Calculate balance sheet ratios and metrics
        """
        metrics = []
        
        for i, row in self.balance.iterrows():
            year = int(row['year'])
            total_assets = row.get('total_assets', np.nan)
            total_liabilities = row.get('total_liabilities', np.nan)
            stockholders_equity = row.get('stockholders_equity', np.nan)
            cash = row.get('cash_and_equivalents', np.nan)
            current_assets = row.get('current_assets', np.nan)
            current_liabilities = row.get('current_liabilities', np.nan)
            long_term_debt = row.get('long_term_debt', np.nan)
            short_term_debt = row.get('short_term_debt', np.nan)
            
            # Debt ratios
            total_debt = 0
            if pd.notna(long_term_debt):
                total_debt += long_term_debt
            if pd.notna(short_term_debt):
                total_debt += short_term_debt
            
            debt_to_equity = (total_debt / stockholders_equity) if pd.notna(total_debt) and pd.notna(stockholders_equity) and stockholders_equity > 0 else np.nan
            debt_to_assets = (total_debt / total_assets) if pd.notna(total_debt) and pd.notna(total_assets) and total_assets > 0 else np.nan
            
            # Liquidity ratios
            current_ratio = (current_assets / current_liabilities) if pd.notna(current_assets) and pd.notna(current_liabilities) and current_liabilities > 0 else np.nan
            
            # Quick ratio (approximation - using cash as liquid assets)
            quick_ratio = (cash / current_liabilities) if pd.notna(cash) and pd.notna(current_liabilities) and current_liabilities > 0 else np.nan
            
            # Net debt
            net_debt = total_debt - cash if pd.notna(total_debt) and pd.notna(cash) else np.nan
            
            metrics.append({
                'year': year,
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'stockholders_equity': stockholders_equity,
                'cash': cash,
                'total_debt': total_debt,
                'net_debt': net_debt,
                'debt_to_equity': debt_to_equity,
                'debt_to_assets': debt_to_assets,
                'current_ratio': current_ratio,
                'quick_ratio': quick_ratio
            })
        
        return pd.DataFrame(metrics)
    
    def calculate_returns_metrics(self) -> pd.DataFrame:
        """
        Calculate return metrics (ROE, ROA, ROIC)
        """
        metrics = []
        
        for i, row in self.income.iterrows():
            year = int(row['year'])
            net_income = row.get('net_income', np.nan)
            
            balance_row = self.balance[self.balance['year'] == year]
            if len(balance_row) > 0:
                balance_row = balance_row.iloc[0]
                total_assets = balance_row.get('total_assets', np.nan)
                stockholders_equity = balance_row.get('stockholders_equity', np.nan)
            else:
                total_assets = np.nan
                stockholders_equity = np.nan
            
            # ROE
            roe = (net_income / stockholders_equity * 100) if pd.notna(net_income) and pd.notna(stockholders_equity) and stockholders_equity > 0 else np.nan
            
            # ROA
            roa = (net_income / total_assets * 100) if pd.notna(net_income) and pd.notna(total_assets) and total_assets > 0 else np.nan
            
            # ROIC (approximation using EBIT)
            ebit = row.get('ebit', np.nan)
            if pd.isna(ebit):
                gross_profit = row.get('gross_profit', np.nan)
                operating_expenses = row.get('operating_expenses', np.nan)
                if pd.notna(gross_profit) and pd.notna(operating_expenses):
                    ebit = gross_profit - operating_expenses
            
            # Invested capital approximation (Stockholders' Equity + Total Debt)
            total_debt = 0
            if len(balance_row) > 0:
                long_term_debt = balance_row.get('long_term_debt', np.nan)
                short_term_debt = balance_row.get('short_term_debt', np.nan)
                if pd.notna(long_term_debt):
                    total_debt += long_term_debt
                if pd.notna(short_term_debt):
                    total_debt += short_term_debt
            
            invested_capital = stockholders_equity + total_debt if pd.notna(stockholders_equity) and pd.notna(total_debt) else np.nan
            roic = (ebit / invested_capital * 100) if pd.notna(ebit) and pd.notna(invested_capital) and invested_capital > 0 else np.nan
            
            metrics.append({
                'year': year,
                'net_income': net_income,
                'total_assets': total_assets,
                'stockholders_equity': stockholders_equity,
                'invested_capital': invested_capital,
                'roe': roe,
                'roa': roa,
                'roic': roic
            })
        
        return pd.DataFrame(metrics)
    
    def calculate_efficiency_metrics(self) -> pd.DataFrame:
        """
        Calculate efficiency ratios (asset turnover, etc.)
        """
        metrics = []
        
        for i, row in self.income.iterrows():
            year = int(row['year'])
            revenue = row.get('revenue', np.nan)
            
            balance_row = self.balance[self.balance['year'] == year]
            if len(balance_row) > 0:
                balance_row = balance_row.iloc[0]
                total_assets = balance_row.get('total_assets', np.nan)
                stockholders_equity = balance_row.get('stockholders_equity', np.nan)
            else:
                total_assets = np.nan
                stockholders_equity = np.nan
            
            # Asset turnover
            asset_turnover = (revenue / total_assets) if pd.notna(revenue) and pd.notna(total_assets) and total_assets > 0 else np.nan
            
            # Equity turnover
            equity_turnover = (revenue / stockholders_equity) if pd.notna(revenue) and pd.notna(stockholders_equity) and stockholders_equity > 0 else np.nan
            
            metrics.append({
                'year': year,
                'revenue': revenue,
                'total_assets': total_assets,
                'stockholders_equity': stockholders_equity,
                'asset_turnover': asset_turnover,
                'equity_turnover': equity_turnover
            })
        
        return pd.DataFrame(metrics)
    
    def calculate_all_metrics(self) -> Dict[str, pd.DataFrame]:
        """
        Calculate all financial metrics and return as dictionary
        """
        return {
            'growth_metrics': self.calculate_growth_metrics(),
            'profitability_metrics': self.calculate_profitability_metrics(),
            'balance_sheet_metrics': self.calculate_balance_sheet_metrics(),
            'returns_metrics': self.calculate_returns_metrics(),
            'efficiency_metrics': self.calculate_efficiency_metrics()
        }
    
    def get_summary_statistics(self, metrics_dict: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        Calculate summary statistics for different time periods
        """
        summary = {}
        
        for metric_name, df in metrics_dict.items():
            if df.empty:
                continue
                
            # Filter to recent years (2011-2025)
            recent_df = df[df['year'] >= 2011].copy()
            
            if recent_df.empty:
                continue
            
            stats = {}
            
            # Last 3 years
            last_3y = recent_df.tail(3)
            if len(last_3y) >= 3:
                for col in last_3y.columns:
                    if col != 'year' and col in last_3y.columns:
                        values = last_3y[col].dropna()
                        if len(values) > 0:
                            stats[f'{col}_3y_avg'] = values.mean()
                            stats[f'{col}_3y_std'] = values.std()
            
            # Last 10 years
            last_10y = recent_df.tail(10)
            if len(last_10y) >= 5:  # At least 5 years
                for col in last_10y.columns:
                    if col != 'year' and col in last_10y.columns:
                        values = last_10y[col].dropna()
                        if len(values) > 0:
                            stats[f'{col}_10y_avg'] = values.mean()
                            stats[f'{col}_10y_std'] = values.std()
            
            # All time
            for col in recent_df.columns:
                if col != 'year' and col in recent_df.columns:
                    values = recent_df[col].dropna()
                    if len(values) > 0:
                        stats[f'{col}_all_avg'] = values.mean()
                        stats[f'{col}_all_std'] = values.std()
                        stats[f'{col}_all_min'] = values.min()
                        stats[f'{col}_all_max'] = values.max()
            
            summary[metric_name] = stats
        
        return summary
