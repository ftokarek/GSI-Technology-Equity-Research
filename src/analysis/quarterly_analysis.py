"""
Quarterly Data Analysis for GSI Technology
Analysis of quarterly trends, seasonality, and patterns
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class QuarterlyAnalyzer:
    """
    Quarterly financial data analysis
    """
    
    def __init__(self, quarterly_income: pd.DataFrame, quarterly_balance: pd.DataFrame):
        """
        Initialize with quarterly data
        """
        self.q_income = quarterly_income
        self.q_balance = quarterly_balance
        
    def extract_quarterly_metrics(self) -> pd.DataFrame:
        """
        Extract key metrics from quarterly data
        """
        quarterly_metrics = []
        
        for year in sorted(self.q_income['year'].unique()):
            year_data = self.q_income[self.q_income['year'] == year]
            
            # Extract key line items
            revenue_rows = year_data[year_data['line_item'].str.contains('Net revenue', case=False, na=False)]
            gross_profit_rows = year_data[year_data['line_item'].str.contains('Gross profit', case=False, na=False)]
            net_income_rows = year_data[year_data['line_item'].str.contains('Net income', case=False, na=False)]
            
            # Try to get values (this is complex due to varying column structures)
            for _, row in revenue_rows.iterrows():
                # Find first substantial numeric value
                for col in row.index:
                    if col not in ['year', 'filename', 'company', 'form_type', 
                                  'filing_date', 'source_file', 'statement_type', 
                                  'sheet_name', 'line_item']:
                        val = row[col]
                        if pd.notna(val):
                            try:
                                num_val = float(val)
                                if num_val > 100:  # Reasonable revenue value
                                    quarterly_metrics.append({
                                        'year': year,
                                        'quarter': 'Q_unknown',
                                        'revenue': num_val,
                                        'source_sheet': row.get('sheet_name', 'unknown')
                                    })
                                    break
                            except (ValueError, TypeError):
                                continue
        
        return pd.DataFrame(quarterly_metrics)
    
    def analyze_seasonality(self) -> Dict:
        """
        Analyze quarterly seasonality patterns
        """
        q_metrics = self.extract_quarterly_metrics()
        
        if q_metrics.empty or len(q_metrics) < 12:
            return {
                'seasonality_detected': False,
                'note': 'Insufficient quarterly data for seasonality analysis'
            }
        
        # Group by estimated quarter (if we can determine it)
        analysis = {
            'seasonality_detected': False,
            'quarterly_data_available': len(q_metrics),
            'years_covered': sorted(q_metrics['year'].unique()),
            'note': 'Quarterly data extracted but quarter identification complex due to varying formats'
        }
        
        return analysis
    
    def analyze_quarterly_volatility(self) -> Dict:
        """
        Analyze quarterly revenue volatility
        """
        q_metrics = self.extract_quarterly_metrics()
        
        if q_metrics.empty:
            return {'error': 'No quarterly data available'}
        
        # Calculate quarterly variance by year
        volatility_by_year = []
        
        for year in sorted(q_metrics['year'].unique()):
            year_data = q_metrics[q_metrics['year'] == year]
            if len(year_data) >= 2:
                volatility = year_data['revenue'].std()
                avg_revenue = year_data['revenue'].mean()
                cv = (volatility / avg_revenue * 100) if avg_revenue > 0 else np.nan
                
                volatility_by_year.append({
                    'year': year,
                    'quarterly_count': len(year_data),
                    'avg_quarterly_revenue': avg_revenue,
                    'quarterly_volatility': volatility,
                    'coefficient_of_variation': cv
                })
        
        volatility_df = pd.DataFrame(volatility_by_year)
        
        analysis = {
            'volatility_data': volatility_df,
            'avg_coefficient_of_variation': volatility_df['coefficient_of_variation'].mean(),
            'interpretation': self._interpret_quarterly_volatility(
                volatility_df['coefficient_of_variation'].mean()
            )
        }
        
        return analysis
    
    def _interpret_quarterly_volatility(self, cv: float) -> str:
        """Interpret quarterly volatility"""
        if pd.isna(cv):
            return 'Insufficient data'
        elif cv > 30:
            return 'HIGH - Significant quarterly fluctuations'
        elif cv > 15:
            return 'MODERATE - Normal quarterly variation'
        else:
            return 'LOW - Stable quarterly performance'
    
    def print_quarterly_analysis(self, seasonality: Dict, volatility: Dict):
        """
        Print quarterly analysis
        """
        print("\n" + "="*80)
        print("📅 QUARTERLY DATA ANALYSIS")
        print("="*80)
        
        print("\n🔍 SEASONALITY ANALYSIS:")
        print(f"  Seasonality Detected: {seasonality.get('seasonality_detected', False)}")
        print(f"  Quarterly Data Available: {seasonality.get('quarterly_data_available', 0)} quarters")
        print(f"  Years Covered: {seasonality.get('years_covered', [])}")
        print(f"  Note: {seasonality.get('note', '')}")
        
        print("\n📊 QUARTERLY VOLATILITY:")
        if 'error' not in volatility:
            print(f"  Average Coefficient of Variation: {volatility['avg_coefficient_of_variation']:.1f}%")
            print(f"  Interpretation: {volatility['interpretation']}")
            
            if 'volatility_data' in volatility:
                vol_df = volatility['volatility_data']
                print(f"\n  Recent years:")
                recent = vol_df.tail(5)
                for _, row in recent.iterrows():
                    print(f"    {int(row['year'])}: Avg ${row['avg_quarterly_revenue']:>8,.0f}K | CV {row['coefficient_of_variation']:>5.1f}%")
        else:
            print(f"  {volatility['error']}")
