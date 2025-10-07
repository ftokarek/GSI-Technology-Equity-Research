"""
Scenario Analysis Module for GSI Technology
Comprehensive scenario analysis: Bull, Base, Bear cases
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ScenarioAnalyzer:
    """
    Scenario-based analysis for investment decision making
    """
    
    def __init__(self, metrics_data: Dict[str, pd.DataFrame]):
        """
        Initialize with financial metrics data
        """
        self.metrics = metrics_data
        
    def analyze_historical_patterns(self) -> Dict:
        """
        Analyze historical patterns to inform scenarios
        """
        growth_df = self.metrics['growth_metrics']
        profit_df = self.metrics['profitability_metrics']
        balance_df = self.metrics['balance_sheet_metrics']
        
        # Filter to recent years
        recent_growth = growth_df[growth_df['year'] >= 2015].copy()
        recent_profit = profit_df[profit_df['year'] >= 2015].copy()
        recent_balance = balance_df[balance_df['year'] >= 2015].copy()
        
        patterns = {
            # Revenue patterns
            'avg_revenue_growth': recent_growth['revenue_growth_yoy'].mean(),
            'revenue_volatility': recent_growth['revenue_growth_yoy'].std(),
            'peak_revenue': recent_growth['revenue'].max(),
            'peak_revenue_year': recent_growth.loc[recent_growth['revenue'].idxmax(), 'year'],
            'current_revenue': recent_growth.iloc[-1]['revenue'],
            
            # Profitability patterns
            'avg_gross_margin': recent_profit['gross_margin'].mean(),
            'gross_margin_volatility': recent_profit['gross_margin'].std(),
            'best_operating_margin': recent_profit['operating_margin'].max(),
            'worst_operating_margin': recent_profit['operating_margin'].min(),
            'current_operating_margin': recent_profit.iloc[-1]['operating_margin'],
            
            # Balance sheet patterns
            'peak_cash': recent_balance['cash'].max(),
            'current_cash': recent_balance.iloc[-1]['cash'],
            'avg_current_ratio': recent_balance['current_ratio'].mean(),
            'cash_burn_rate': (recent_balance.iloc[-1]['cash'] - recent_balance.iloc[-5]['cash']) / 5 if len(recent_balance) >= 5 else np.nan
        }
        
        return patterns
    
    def build_bull_scenario(self, projection_years: int = 5) -> Dict:
        """
        Bull case: Successful turnaround scenario
        """
        patterns = self.analyze_historical_patterns()
        current_revenue = patterns['current_revenue']
        peak_revenue = patterns['peak_revenue']
        
        projections = []
        
        # Bull case assumptions
        revenue = current_revenue
        gross_margin = 65.0  # Strong margins maintained
        operating_margin_improvement = 5.0  # 5% improvement per year
        operating_margin = patterns['current_operating_margin']
        
        for year in range(1, projection_years + 1):
            # Revenue recovery: 10% growth per year
            revenue = revenue * 1.10
            
            # Operating margin improvement (cap at 15%)
            operating_margin = min(operating_margin + operating_margin_improvement, 15.0)
            
            # Calculate metrics
            gross_profit = revenue * (gross_margin / 100)
            operating_income = revenue * (operating_margin / 100)
            net_income = operating_income * 0.75  # 25% tax approximation
            
            projections.append({
                'year': 2025 + year,
                'revenue': revenue,
                'gross_margin': gross_margin,
                'operating_margin': operating_margin,
                'gross_profit': gross_profit,
                'operating_income': operating_income,
                'net_income': net_income
            })
        
        scenario = {
            'name': 'Bull Case - Successful Turnaround',
            'probability': 25,  # 25% probability
            'assumptions': {
                'revenue_growth': '10% per year',
                'gross_margin': f'{gross_margin}%',
                'operating_margin_improvement': '5% per year (cap at 15%)',
                'key_drivers': [
                    'New product launches successful',
                    'Market share gains in memory solutions',
                    'Operational efficiency improvements',
                    'R&D investments pay off'
                ]
            },
            'projections': projections,
            'five_year_revenue': projections[-1]['revenue'],
            'five_year_cagr': ((projections[-1]['revenue'] / current_revenue) ** (1/projection_years) - 1) * 100,
            'target_valuation_multiple': 3.0  # EV/Sales multiple
        }
        
        # Calculate implied valuation
        scenario['implied_enterprise_value'] = scenario['five_year_revenue'] * scenario['target_valuation_multiple']
        
        return scenario
    
    def build_base_scenario(self, projection_years: int = 5) -> Dict:
        """
        Base case: Stabilization scenario
        """
        patterns = self.analyze_historical_patterns()
        current_revenue = patterns['current_revenue']
        
        projections = []
        
        # Base case assumptions
        revenue = current_revenue
        gross_margin = 60.0  # Maintaining current margins
        operating_margin = patterns['current_operating_margin']
        operating_margin_improvement = 2.0  # Slow improvement
        
        for year in range(1, projection_years + 1):
            # Revenue stabilization: flat first 2 years, then 3% growth
            if year <= 2:
                revenue = revenue * 1.00  # Flat
            else:
                revenue = revenue * 1.03  # 3% growth
            
            # Operating margin gradual improvement (cap at 5%)
            operating_margin = min(operating_margin + operating_margin_improvement, 5.0)
            
            # Calculate metrics
            gross_profit = revenue * (gross_margin / 100)
            operating_income = revenue * (operating_margin / 100)
            net_income = operating_income * 0.75
            
            projections.append({
                'year': 2025 + year,
                'revenue': revenue,
                'gross_margin': gross_margin,
                'operating_margin': operating_margin,
                'gross_profit': gross_profit,
                'operating_income': operating_income,
                'net_income': net_income
            })
        
        scenario = {
            'name': 'Base Case - Stabilization',
            'probability': 50,  # 50% probability
            'assumptions': {
                'revenue_growth': 'Flat for 2 years, then 3% growth',
                'gross_margin': f'{gross_margin}%',
                'operating_margin_improvement': '2% per year (cap at 5%)',
                'key_drivers': [
                    'Revenue stabilizes at current levels',
                    'Cost cutting initiatives succeed',
                    'Maintains market position',
                    'No major breakthroughs or failures'
                ]
            },
            'projections': projections,
            'five_year_revenue': projections[-1]['revenue'],
            'five_year_cagr': ((projections[-1]['revenue'] / current_revenue) ** (1/projection_years) - 1) * 100,
            'target_valuation_multiple': 1.5  # EV/Sales multiple
        }
        
        scenario['implied_enterprise_value'] = scenario['five_year_revenue'] * scenario['target_valuation_multiple']
        
        return scenario
    
    def build_bear_scenario(self, projection_years: int = 5) -> Dict:
        """
        Bear case: Continued decline scenario
        """
        patterns = self.analyze_historical_patterns()
        current_revenue = patterns['current_revenue']
        
        projections = []
        
        # Bear case assumptions
        revenue = current_revenue
        gross_margin = 55.0  # Margin pressure
        operating_margin = patterns['current_operating_margin']
        
        for year in range(1, projection_years + 1):
            # Revenue decline: -10% per year
            revenue = revenue * 0.90
            
            # Operating margin deteriorates slightly
            operating_margin = operating_margin - 2.0
            
            # Calculate metrics
            gross_profit = revenue * (gross_margin / 100)
            operating_income = revenue * (operating_margin / 100)
            net_income = operating_income * 0.75
            
            projections.append({
                'year': 2025 + year,
                'revenue': revenue,
                'gross_margin': gross_margin,
                'operating_margin': operating_margin,
                'gross_profit': gross_profit,
                'operating_income': operating_income,
                'net_income': net_income
            })
        
        scenario = {
            'name': 'Bear Case - Continued Decline',
            'probability': 25,  # 25% probability
            'assumptions': {
                'revenue_growth': '-10% per year',
                'gross_margin': f'{gross_margin}%',
                'operating_margin_deterioration': '-2% per year',
                'key_drivers': [
                    'Market share losses continue',
                    'Technology becomes obsolete',
                    'Competition intensifies',
                    'Unable to achieve profitability'
                ]
            },
            'projections': projections,
            'five_year_revenue': projections[-1]['revenue'],
            'five_year_cagr': ((projections[-1]['revenue'] / current_revenue) ** (1/projection_years) - 1) * 100,
            'target_valuation_multiple': 0.5  # EV/Sales multiple (distressed)
        }
        
        scenario['implied_enterprise_value'] = scenario['five_year_revenue'] * scenario['target_valuation_multiple']
        
        return scenario
    
    def calculate_expected_value(self, scenarios: List[Dict]) -> Dict:
        """
        Calculate probability-weighted expected value
        """
        total_probability = sum([s['probability'] for s in scenarios])
        
        # Normalize probabilities
        for scenario in scenarios:
            scenario['normalized_probability'] = scenario['probability'] / total_probability
        
        # Calculate weighted averages
        expected_revenue = sum([s['five_year_revenue'] * s['normalized_probability'] for s in scenarios])
        expected_cagr = sum([s['five_year_cagr'] * s['normalized_probability'] for s in scenarios])
        expected_valuation = sum([s['implied_enterprise_value'] * s['normalized_probability'] for s in scenarios])
        
        return {
            'expected_revenue': expected_revenue,
            'expected_cagr': expected_cagr,
            'expected_valuation': expected_valuation,
            'scenarios': scenarios
        }
    
    def run_scenario_analysis(self) -> Dict:
        """
        Run comprehensive scenario analysis
        """
        # Build scenarios
        bull = self.build_bull_scenario()
        base = self.build_base_scenario()
        bear = self.build_bear_scenario()
        
        scenarios = [bull, base, bear]
        
        # Calculate expected value
        expected_value = self.calculate_expected_value(scenarios)
        
        return expected_value
    
    def print_scenario_analysis(self, scenario_results: Dict):
        """
        Print comprehensive scenario analysis
        """
        print("\n" + "="*80)
        print("📊 SCENARIO ANALYSIS - BULL / BASE / BEAR")
        print("="*80)
        
        scenarios = scenario_results['scenarios']
        
        for scenario in scenarios:
            print(f"\n{'='*80}")
            print(f"🎯 {scenario['name'].upper()}")
            print(f"{'='*80}")
            print(f"  Probability: {scenario['probability']}%")
            print(f"\n  Key Assumptions:")
            for key, value in scenario['assumptions'].items():
                if key != 'key_drivers':
                    print(f"    • {key.replace('_', ' ').title()}: {value}")
            
            print(f"\n  Key Drivers:")
            for driver in scenario['assumptions']['key_drivers']:
                print(f"    • {driver}")
            
            print(f"\n  5-Year Projections:")
            projections_df = pd.DataFrame(scenario['projections'])
            for _, row in projections_df.iterrows():
                print(f"    {int(row['year'])}: Revenue ${row['revenue']:>8,.0f}K | OpMargin {row['operating_margin']:>6.1f}%")
            
            print(f"\n  Outcome:")
            print(f"    • 5-Year Revenue: ${scenario['five_year_revenue']:,.0f}K")
            print(f"    • 5-Year CAGR: {scenario['five_year_cagr']:.1f}%")
            print(f"    • Implied Enterprise Value: ${scenario['implied_enterprise_value']:,.0f}K")
        
        # Expected value
        print(f"\n{'='*80}")
        print(f"🎯 PROBABILITY-WEIGHTED EXPECTED VALUE")
        print(f"{'='*80}")
        print(f"  Expected 5-Year Revenue: ${scenario_results['expected_revenue']:,.0f}K")
        print(f"  Expected 5-Year CAGR: {scenario_results['expected_cagr']:.1f}%")
        print(f"  Expected Enterprise Value: ${scenario_results['expected_valuation']:,.0f}K")
