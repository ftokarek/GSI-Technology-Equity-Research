"""
Trend Analysis Module for GSI Technology
Comprehensive trend analysis across different time periods
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TrendAnalyzer:
    """
    Comprehensive trend analysis for financial metrics
    """
    
    def __init__(self, metrics_data: Dict[str, pd.DataFrame]):
        """
        Initialize with calculated metrics data
        """
        self.metrics = metrics_data
        
    def analyze_revenue_trends(self) -> Dict:
        """
        Analyze revenue trends across different periods
        """
        growth_df = self.metrics['growth_metrics']
        
        # Filter to recent years (2011-2025)
        recent_data = growth_df[growth_df['year'] >= 2011].copy()
        
        trends = {}
        
        # 3-Year Analysis (2023-2025)
        last_3y = recent_data.tail(3)
        if len(last_3y) >= 3:
            trends['3y'] = {
                'period': '2023-2025',
                'start_revenue': last_3y.iloc[0]['revenue'],
                'end_revenue': last_3y.iloc[-1]['revenue'],
                'cagr': last_3y.iloc[-1]['revenue_cagr_3y'],
                'avg_growth': last_3y['revenue_growth_yoy'].mean(),
                'volatility': last_3y['revenue_growth_yoy'].std(),
                'trend_direction': 'declining' if last_3y.iloc[-1]['revenue'] < last_3y.iloc[0]['revenue'] else 'growing'
            }
        
        # 10-Year Analysis (2016-2025)
        last_10y = recent_data.tail(10)
        if len(last_10y) >= 5:
            trends['10y'] = {
                'period': '2016-2025',
                'start_revenue': last_10y.iloc[0]['revenue'],
                'end_revenue': last_10y.iloc[-1]['revenue'],
                'cagr': last_10y.iloc[-1]['revenue_cagr_10y'],
                'avg_growth': last_10y['revenue_growth_yoy'].mean(),
                'volatility': last_10y['revenue_growth_yoy'].std(),
                'trend_direction': 'declining' if last_10y.iloc[-1]['revenue'] < last_10y.iloc[0]['revenue'] else 'growing'
            }
        
        # All-Time Analysis (2011-2025)
        if len(recent_data) >= 10:
            trends['all_time'] = {
                'period': '2011-2025',
                'start_revenue': recent_data.iloc[0]['revenue'],
                'end_revenue': recent_data.iloc[-1]['revenue'],
                'cagr': recent_data.iloc[-1]['revenue_cagr_10y'],  # Use 10Y CAGR as proxy
                'avg_growth': recent_data['revenue_growth_yoy'].mean(),
                'volatility': recent_data['revenue_growth_yoy'].std(),
                'trend_direction': 'declining' if recent_data.iloc[-1]['revenue'] < recent_data.iloc[0]['revenue'] else 'growing',
                'peak_revenue': recent_data['revenue'].max(),
                'peak_year': recent_data.loc[recent_data['revenue'].idxmax(), 'year']
            }
        
        return trends
    
    def analyze_profitability_trends(self) -> Dict:
        """
        Analyze profitability trends across different periods
        """
        profit_df = self.metrics['profitability_metrics']
        recent_data = profit_df[profit_df['year'] >= 2011].copy()
        
        trends = {}
        
        # 3-Year Analysis
        last_3y = recent_data.tail(3)
        if len(last_3y) >= 3:
            trends['3y'] = {
                'period': '2023-2025',
                'avg_gross_margin': last_3y['gross_margin'].mean(),
                'avg_operating_margin': last_3y['operating_margin'].mean(),
                'avg_net_margin': last_3y['net_margin'].mean(),
                'gross_margin_trend': 'improving' if last_3y.iloc[-1]['gross_margin'] > last_3y.iloc[0]['gross_margin'] else 'declining',
                'operating_margin_trend': 'improving' if last_3y.iloc[-1]['operating_margin'] > last_3y.iloc[0]['operating_margin'] else 'declining'
            }
        
        # 10-Year Analysis
        last_10y = recent_data.tail(10)
        if len(last_10y) >= 5:
            trends['10y'] = {
                'period': '2016-2025',
                'avg_gross_margin': last_10y['gross_margin'].mean(),
                'avg_operating_margin': last_10y['operating_margin'].mean(),
                'avg_net_margin': last_10y['net_margin'].mean(),
                'gross_margin_trend': 'improving' if last_10y.iloc[-1]['gross_margin'] > last_10y.iloc[0]['gross_margin'] else 'declining',
                'operating_margin_trend': 'improving' if last_10y.iloc[-1]['operating_margin'] > last_10y.iloc[0]['operating_margin'] else 'declining'
            }
        
        # All-Time Analysis
        if len(recent_data) >= 10:
            trends['all_time'] = {
                'period': '2011-2025',
                'avg_gross_margin': recent_data['gross_margin'].mean(),
                'avg_operating_margin': recent_data['operating_margin'].mean(),
                'avg_net_margin': recent_data['net_margin'].mean(),
                'best_gross_margin': recent_data['gross_margin'].max(),
                'best_gross_margin_year': recent_data.loc[recent_data['gross_margin'].idxmax(), 'year'],
                'worst_operating_margin': recent_data['operating_margin'].min(),
                'worst_operating_margin_year': recent_data.loc[recent_data['operating_margin'].idxmin(), 'year']
            }
        
        return trends
    
    def analyze_balance_sheet_trends(self) -> Dict:
        """
        Analyze balance sheet trends across different periods
        """
        balance_df = self.metrics['balance_sheet_metrics']
        recent_data = balance_df[balance_df['year'] >= 2011].copy()
        
        trends = {}
        
        # 3-Year Analysis
        last_3y = recent_data.tail(3)
        if len(last_3y) >= 3:
            trends['3y'] = {
                'period': '2023-2025',
                'avg_cash': last_3y['cash'].mean(),
                'avg_total_assets': last_3y['total_assets'].mean(),
                'avg_debt_to_equity': last_3y['debt_to_equity'].mean(),
                'avg_current_ratio': last_3y['current_ratio'].mean(),
                'cash_trend': 'improving' if last_3y.iloc[-1]['cash'] > last_3y.iloc[0]['cash'] else 'declining',
                'assets_trend': 'improving' if last_3y.iloc[-1]['total_assets'] > last_3y.iloc[0]['total_assets'] else 'declining'
            }
        
        # 10-Year Analysis
        last_10y = recent_data.tail(10)
        if len(last_10y) >= 5:
            trends['10y'] = {
                'period': '2016-2025',
                'avg_cash': last_10y['cash'].mean(),
                'avg_total_assets': last_10y['total_assets'].mean(),
                'avg_debt_to_equity': last_10y['debt_to_equity'].mean(),
                'avg_current_ratio': last_10y['current_ratio'].mean(),
                'cash_trend': 'improving' if last_10y.iloc[-1]['cash'] > last_10y.iloc[0]['cash'] else 'declining',
                'assets_trend': 'improving' if last_10y.iloc[-1]['total_assets'] > last_10y.iloc[0]['total_assets'] else 'declining'
            }
        
        # All-Time Analysis
        if len(recent_data) >= 10:
            trends['all_time'] = {
                'period': '2011-2025',
                'avg_cash': recent_data['cash'].mean(),
                'avg_total_assets': recent_data['total_assets'].mean(),
                'avg_debt_to_equity': recent_data['debt_to_equity'].mean(),
                'avg_current_ratio': recent_data['current_ratio'].mean(),
                'peak_cash': recent_data['cash'].max(),
                'peak_cash_year': recent_data.loc[recent_data['cash'].idxmax(), 'year'],
                'peak_assets': recent_data['total_assets'].max(),
                'peak_assets_year': recent_data.loc[recent_data['total_assets'].idxmax(), 'year']
            }
        
        return trends
    
    def analyze_returns_trends(self) -> Dict:
        """
        Analyze returns trends across different periods
        """
        returns_df = self.metrics['returns_metrics']
        recent_data = returns_df[returns_df['year'] >= 2011].copy()
        
        trends = {}
        
        # 3-Year Analysis
        last_3y = recent_data.tail(3)
        if len(last_3y) >= 3:
            trends['3y'] = {
                'period': '2023-2025',
                'avg_roe': last_3y['roe'].mean(),
                'avg_roa': last_3y['roa'].mean(),
                'avg_roic': last_3y['roic'].mean(),
                'roe_trend': 'improving' if last_3y.iloc[-1]['roe'] > last_3y.iloc[0]['roe'] else 'declining',
                'roa_trend': 'improving' if last_3y.iloc[-1]['roa'] > last_3y.iloc[0]['roa'] else 'declining'
            }
        
        # 10-Year Analysis
        last_10y = recent_data.tail(10)
        if len(last_10y) >= 5:
            trends['10y'] = {
                'period': '2016-2025',
                'avg_roe': last_10y['roe'].mean(),
                'avg_roa': last_10y['roa'].mean(),
                'avg_roic': last_10y['roic'].mean(),
                'roe_trend': 'improving' if last_10y.iloc[-1]['roe'] > last_10y.iloc[0]['roe'] else 'declining',
                'roa_trend': 'improving' if last_10y.iloc[-1]['roa'] > last_10y.iloc[0]['roa'] else 'declining'
            }
        
        # All-Time Analysis
        if len(recent_data) >= 10:
            trends['all_time'] = {
                'period': '2011-2025',
                'avg_roe': recent_data['roe'].mean(),
                'avg_roa': recent_data['roa'].mean(),
                'avg_roic': recent_data['roic'].mean(),
                'best_roe': recent_data['roe'].max(),
                'best_roe_year': recent_data.loc[recent_data['roe'].idxmax(), 'year'],
                'best_roa': recent_data['roa'].max(),
                'best_roa_year': recent_data.loc[recent_data['roa'].idxmax(), 'year']
            }
        
        return trends
    
    def generate_trend_summary(self) -> Dict:
        """
        Generate comprehensive trend summary across all metrics
        """
        summary = {
            'revenue_trends': self.analyze_revenue_trends(),
            'profitability_trends': self.analyze_profitability_trends(),
            'balance_sheet_trends': self.analyze_balance_sheet_trends(),
            'returns_trends': self.analyze_returns_trends()
        }
        
        return summary
    
    def print_trend_analysis(self, trend_summary: Dict):
        """
        Print comprehensive trend analysis
        """
        print("\n" + "="*80)
        print("📈 COMPREHENSIVE TREND ANALYSIS")
        print("="*80)
        
        # Revenue Trends
        print("\n💰 REVENUE TRENDS:")
        revenue_trends = trend_summary['revenue_trends']
        
        for period, data in revenue_trends.items():
            print(f"\n  {period.upper()} PERIOD ({data['period']}):")
            print(f"    Revenue: ${data['start_revenue']:,.0f}K → ${data['end_revenue']:,.0f}K")
            print(f"    CAGR: {data['cagr']:.1f}%")
            print(f"    Avg Growth: {data['avg_growth']:.1f}%")
            print(f"    Volatility: {data['volatility']:.1f}%")
            print(f"    Trend: {data['trend_direction'].upper()}")
            
            if 'peak_revenue' in data:
                print(f"    Peak Revenue: ${data['peak_revenue']:,.0f}K ({data['peak_year']})")
        
        # Profitability Trends
        print("\n📊 PROFITABILITY TRENDS:")
        profit_trends = trend_summary['profitability_trends']
        
        for period, data in profit_trends.items():
            print(f"\n  {period.upper()} PERIOD ({data['period']}):")
            print(f"    Gross Margin: {data['avg_gross_margin']:.1f}%")
            print(f"    Operating Margin: {data['avg_operating_margin']:.1f}%")
            if 'avg_net_margin' in data and pd.notna(data['avg_net_margin']):
                print(f"    Net Margin: {data['avg_net_margin']:.1f}%")
            if 'gross_margin_trend' in data:
                print(f"    Gross Trend: {data['gross_margin_trend'].upper()}")
            if 'operating_margin_trend' in data:
                print(f"    Operating Trend: {data['operating_margin_trend'].upper()}")
            
            if 'best_gross_margin' in data:
                print(f"    Best Gross Margin: {data['best_gross_margin']:.1f}% ({data['best_gross_margin_year']})")
                print(f"    Worst Operating Margin: {data['worst_operating_margin']:.1f}% ({data['worst_operating_margin_year']})")
        
        # Balance Sheet Trends
        print("\n💼 BALANCE SHEET TRENDS:")
        balance_trends = trend_summary['balance_sheet_trends']
        
        for period, data in balance_trends.items():
            print(f"\n  {period.upper()} PERIOD ({data['period']}):")
            print(f"    Avg Cash: ${data['avg_cash']:,.0f}K")
            if pd.notna(data['avg_total_assets']):
                print(f"    Avg Assets: ${data['avg_total_assets']:,.0f}K")
            if pd.notna(data['avg_debt_to_equity']):
                print(f"    Avg D/E: {data['avg_debt_to_equity']:.2f}")
            print(f"    Avg Current Ratio: {data['avg_current_ratio']:.2f}")
            if 'cash_trend' in data:
                print(f"    Cash Trend: {data['cash_trend'].upper()}")
            if 'assets_trend' in data:
                print(f"    Assets Trend: {data['assets_trend'].upper()}")
            
            if 'peak_cash' in data:
                print(f"    Peak Cash: ${data['peak_cash']:,.0f}K ({data['peak_cash_year']})")
                print(f"    Peak Assets: ${data['peak_assets']:,.0f}K ({data['peak_assets_year']})")
        
        # Returns Trends
        print("\n🎯 RETURNS TRENDS:")
        returns_trends = trend_summary['returns_trends']
        
        for period, data in returns_trends.items():
            print(f"\n  {period.upper()} PERIOD ({data['period']}):")
            if pd.notna(data['avg_roe']):
                print(f"    Avg ROE: {data['avg_roe']:.1f}%")
            if pd.notna(data['avg_roa']):
                print(f"    Avg ROA: {data['avg_roa']:.1f}%")
            if pd.notna(data['avg_roic']):
                print(f"    Avg ROIC: {data['avg_roic']:.1f}%")
            if 'roe_trend' in data:
                print(f"    ROE Trend: {data['roe_trend'].upper()}")
            if 'roa_trend' in data:
                print(f"    ROA Trend: {data['roa_trend'].upper()}")
            
            if 'best_roe' in data and pd.notna(data['best_roe']):
                print(f"    Best ROE: {data['best_roe']:.1f}% ({data['best_roe_year']})")
            if 'best_roa' in data and pd.notna(data['best_roa']):
                print(f"    Best ROA: {data['best_roa']:.1f}% ({data['best_roa_year']})")
