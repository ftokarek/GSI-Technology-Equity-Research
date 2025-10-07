"""
Valuation Analysis Module for GSI Technology
Comprehensive valuation analysis including DCF, multiples, and fair value estimation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ValuationAnalyzer:
    """
    Comprehensive valuation analysis for GSI Technology
    """
    
    def __init__(self, metrics_data: Dict[str, pd.DataFrame], 
                 market_data: Optional[pd.DataFrame] = None):
        """
        Initialize with financial metrics and market data
        """
        self.metrics = metrics_data
        self.market = market_data
        
    def calculate_multiples(self) -> Dict:
        """
        Calculate valuation multiples (P/E, P/BV, EV/EBITDA, EV/Sales)
        """
        multiples = {}
        
        income_df = self.metrics['profitability_metrics']
        balance_df = self.metrics['balance_sheet_metrics']
        
        latest_year = income_df['year'].max()
        latest_income = income_df[income_df['year'] == latest_year].iloc[0]
        latest_balance = balance_df[balance_df['year'] == latest_year].iloc[0]
        
        if self.market is not None and not self.market.empty:
            latest_market = self.market[self.market['year'] == latest_year]
            if not latest_market.empty:
                latest_market = latest_market.iloc[0]
                current_price = latest_market.get('avg_price', np.nan)
            else:
                current_price = np.nan
        else:
            current_price = np.nan
        
        # Note: We don't have shares outstanding, so we'll use book value as proxy
        market_cap = np.nan
        if pd.notna(current_price):
            # This is a placeholder - in real analysis we'd need shares outstanding
            market_cap = current_price * 1000  # Placeholder calculation
        
        revenue = latest_income.get('revenue', np.nan)
        ebitda = latest_income.get('ebitda', np.nan)
        net_income = latest_income.get('net_income', np.nan)
        total_assets = latest_balance.get('total_assets', np.nan)
        stockholders_equity = latest_balance.get('stockholders_equity', np.nan)
        
        # P/E Ratio
        if pd.notna(net_income) and net_income > 0 and pd.notna(market_cap):
            pe_ratio = market_cap / (net_income * 1000)  # Convert to millions
        else:
            pe_ratio = np.nan
        
        # P/BV Ratio
        if pd.notna(stockholders_equity) and stockholders_equity > 0 and pd.notna(market_cap):
            pbv_ratio = market_cap / (stockholders_equity * 1000)  # Convert to millions
        else:
            pbv_ratio = np.nan
        
        # EV/EBITDA (approximation)
        if pd.notna(ebitda) and ebitda > 0 and pd.notna(market_cap):
            ev_ebitda = market_cap / (ebitda * 1000)  # Convert to millions
        else:
            ev_ebitda = np.nan
        
        # EV/Sales
        if pd.notna(revenue) and revenue > 0 and pd.notna(market_cap):
            ev_sales = market_cap / (revenue * 1000)  # Convert to millions
        else:
            ev_sales = np.nan
        
        multiples = {
            'year': latest_year,
            'current_price': current_price,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'pbv_ratio': pbv_ratio,
            'ev_ebitda': ev_ebitda,
            'ev_sales': ev_sales,
            'revenue': revenue,
            'ebitda': ebitda,
            'net_income': net_income,
            'stockholders_equity': stockholders_equity
        }
        
        return multiples
    
    def calculate_dcf_valuation(self, 
                               terminal_growth_rate: float = 2.0,
                               discount_rate: float = 10.0,
                               projection_years: int = 5) -> Dict:
        """
        Calculate DCF valuation (simplified version)
        """
        income_df = self.metrics['profitability_metrics']
        recent_data = income_df[income_df['year'] >= 2020].copy()
        
        if recent_data.empty:
            return {'error': 'Insufficient data for DCF analysis'}
        
        avg_revenue_growth = recent_data['revenue'].pct_change().mean() * 100
        avg_ebitda_margin = (recent_data['ebitda'] / recent_data['revenue'] * 100).mean()
        avg_net_margin = (recent_data['net_income'] / recent_data['revenue'] * 100).mean()
        
        latest_year = recent_data['year'].max()
        latest_revenue = recent_data[recent_data['year'] == latest_year]['revenue'].iloc[0]
        latest_ebitda = recent_data[recent_data['year'] == latest_year]['ebitda'].iloc[0]
        
        # Project future cash flows
        projections = []
        current_revenue = latest_revenue
        current_ebitda = latest_ebitda
        
        for year in range(1, projection_years + 1):
            # Project revenue (using historical growth rate)
            projected_revenue = current_revenue * (1 + avg_revenue_growth/100)
            
            # Project EBITDA (using historical margin)
            projected_ebitda = projected_revenue * (avg_ebitda_margin/100)
            
            # Project free cash flow (simplified: EBITDA * 0.8)
            projected_fcf = projected_ebitda * 0.8
            
            # Discount to present value
            pv_fcf = projected_fcf / ((1 + discount_rate/100) ** year)
            
            projections.append({
                'year': latest_year + year,
                'revenue': projected_revenue,
                'ebitda': projected_ebitda,
                'fcf': projected_fcf,
                'pv_fcf': pv_fcf
            })
            
            current_revenue = projected_revenue
            current_ebitda = projected_ebitda
        
        terminal_fcf = projections[-1]['fcf'] * (1 + terminal_growth_rate/100)
        terminal_value = terminal_fcf / ((discount_rate - terminal_growth_rate) / 100)
        pv_terminal_value = terminal_value / ((1 + discount_rate/100) ** projection_years)
        
        pv_cash_flows = sum([p['pv_fcf'] for p in projections])
        enterprise_value = pv_cash_flows + pv_terminal_value
        
        # Convert to millions
        enterprise_value_millions = enterprise_value / 1000
        
        dcf_results = {
            'projection_years': projection_years,
            'terminal_growth_rate': terminal_growth_rate,
            'discount_rate': discount_rate,
            'historical_avg_revenue_growth': avg_revenue_growth,
            'historical_avg_ebitda_margin': avg_ebitda_margin,
            'projections': projections,
            'terminal_value': terminal_value,
            'pv_terminal_value': pv_terminal_value,
            'pv_cash_flows': pv_cash_flows,
            'enterprise_value': enterprise_value,
            'enterprise_value_millions': enterprise_value_millions
        }
        
        return dcf_results
    
    def calculate_fair_value_estimation(self) -> Dict:
        """
        Calculate fair value using multiple methods
        """
        fair_value = {}
        
        # Method 1: P/E Multiple (if available)
        multiples = self.calculate_multiples()
        if pd.notna(multiples['pe_ratio']) and pd.notna(multiples['net_income']):
            # Use industry average P/E (placeholder: 15x)
            industry_pe = 15.0
            fair_value_pe = (multiples['net_income'] * 1000) * industry_pe / 1000  # Convert to millions
            fair_value['pe_method'] = {
                'method': 'P/E Multiple',
                'industry_pe': industry_pe,
                'fair_value': fair_value_pe,
                'confidence': 'medium'
            }
        
        # Method 2: P/BV Multiple (if available)
        if pd.notna(multiples['pbv_ratio']) and pd.notna(multiples['stockholders_equity']):
            # Use industry average P/BV (placeholder: 1.5x)
            industry_pbv = 1.5
            fair_value_pbv = (multiples['stockholders_equity'] * 1000) * industry_pbv / 1000  # Convert to millions
            fair_value['pbv_method'] = {
                'method': 'P/BV Multiple',
                'industry_pbv': industry_pbv,
                'fair_value': fair_value_pbv,
                'confidence': 'medium'
            }
        
        # Method 3: DCF Analysis
        dcf_results = self.calculate_dcf_valuation()
        if 'error' not in dcf_results:
            fair_value['dcf_method'] = {
                'method': 'DCF Analysis',
                'fair_value': dcf_results['enterprise_value_millions'],
                'confidence': 'high',
                'details': dcf_results
            }
        
        # Method 4: Revenue Multiple (if available)
        if pd.notna(multiples['revenue']):
            # Use industry average EV/Sales (placeholder: 2.0x)
            industry_ev_sales = 2.0
            fair_value_revenue = (multiples['revenue'] * 1000) * industry_ev_sales / 1000  # Convert to millions
            fair_value['revenue_method'] = {
                'method': 'Revenue Multiple',
                'industry_ev_sales': industry_ev_sales,
                'fair_value': fair_value_revenue,
                'confidence': 'low'
            }
        
        valid_values = [v['fair_value'] for v in fair_value.values() if 'fair_value' in v]
        if valid_values:
            fair_value['average'] = np.mean(valid_values)
            fair_value['median'] = np.median(valid_values)
            fair_value['std'] = np.std(valid_values)
        
        return fair_value
    
    def analyze_valuation_attractiveness(self) -> Dict:
        """
        Analyze valuation attractiveness and investment recommendation
        """
        multiples = self.calculate_multiples()
        fair_value = self.calculate_fair_value_estimation()
        
        attractiveness = {
            'current_valuation': multiples,
            'fair_value_estimation': fair_value
        }
        
        score = 0
        factors = []
        
        # P/E Analysis
        if pd.notna(multiples['pe_ratio']):
            if multiples['pe_ratio'] < 10:
                score += 2
                factors.append('Low P/E ratio')
            elif multiples['pe_ratio'] < 15:
                score += 1
                factors.append('Moderate P/E ratio')
            else:
                score -= 1
                factors.append('High P/E ratio')
        
        # P/BV Analysis
        if pd.notna(multiples['pbv_ratio']):
            if multiples['pbv_ratio'] < 1.0:
                score += 2
                factors.append('Trading below book value')
            elif multiples['pbv_ratio'] < 1.5:
                score += 1
                factors.append('Moderate P/BV ratio')
            else:
                score -= 1
                factors.append('High P/BV ratio')
        
        # Revenue Growth Analysis
        growth_df = self.metrics['growth_metrics']
        recent_growth = growth_df[growth_df['year'] >= 2020]['revenue_growth_yoy'].mean()
        if pd.notna(recent_growth):
            if recent_growth > 5:
                score += 2
                factors.append('Strong revenue growth')
            elif recent_growth > 0:
                score += 1
                factors.append('Positive revenue growth')
            else:
                score -= 2
                factors.append('Negative revenue growth')
        
        # Profitability Analysis
        profit_df = self.metrics['profitability_metrics']
        recent_operating_margin = profit_df[profit_df['year'] >= 2020]['operating_margin'].mean()
        if pd.notna(recent_operating_margin):
            if recent_operating_margin > 10:
                score += 2
                factors.append('Strong operating margins')
            elif recent_operating_margin > 0:
                score += 1
                factors.append('Positive operating margins')
            else:
                score -= 2
                factors.append('Negative operating margins')
        
        # Financial Health Analysis
        balance_df = self.metrics['balance_sheet_metrics']
        recent_cash = balance_df[balance_df['year'] >= 2020]['cash'].mean()
        recent_current_ratio = balance_df[balance_df['year'] >= 2020]['current_ratio'].mean()
        
        if pd.notna(recent_cash) and recent_cash > 10000:  # More than $10M
            score += 1
            factors.append('Strong cash position')
        elif pd.notna(recent_cash) and recent_cash < 1000:  # Less than $1M
            score -= 2
            factors.append('Weak cash position')
        
        if pd.notna(recent_current_ratio) and recent_current_ratio > 2.0:
            score += 1
            factors.append('Strong liquidity')
        elif pd.notna(recent_current_ratio) and recent_current_ratio < 1.0:
            score -= 2
            factors.append('Weak liquidity')
        
        # Determine recommendation
        if score >= 4:
            recommendation = 'STRONG BUY'
            confidence = 'High'
        elif score >= 2:
            recommendation = 'BUY'
            confidence = 'Medium'
        elif score >= 0:
            recommendation = 'HOLD'
            confidence = 'Medium'
        elif score >= -2:
            recommendation = 'SELL'
            confidence = 'Medium'
        else:
            recommendation = 'STRONG SELL'
            confidence = 'High'
        
        attractiveness['score'] = score
        attractiveness['factors'] = factors
        attractiveness['recommendation'] = recommendation
        attractiveness['confidence'] = confidence
        
        return attractiveness
    
    def print_valuation_analysis(self, valuation_results: Dict):
        """
        Print comprehensive valuation analysis
        """
        print("\n" + "="*80)
        print(" VALUATION ANALYSIS")
        print("="*80)
        
        # Current Multiples
        multiples = valuation_results['current_valuation']
        print(f"\n CURRENT VALUATION MULTIPLES:")
        print(f"  Year: {multiples['year']}")
        if pd.notna(multiples['current_price']):
            print(f"  Current Price: ${multiples['current_price']:.2f}")
        if pd.notna(multiples['pe_ratio']):
            print(f"  P/E Ratio: {multiples['pe_ratio']:.2f}")
        if pd.notna(multiples['pbv_ratio']):
            print(f"  P/BV Ratio: {multiples['pbv_ratio']:.2f}")
        if pd.notna(multiples['ev_ebitda']):
            print(f"  EV/EBITDA: {multiples['ev_ebitda']:.2f}")
        if pd.notna(multiples['ev_sales']):
            print(f"  EV/Sales: {multiples['ev_sales']:.2f}")
        
        # Fair Value Estimation
        fair_value = valuation_results['fair_value_estimation']
        print(f"\n FAIR VALUE ESTIMATION:")
        for method, data in fair_value.items():
            if method != 'average' and method != 'median' and method != 'std':
                print(f"  {data['method']}: ${data['fair_value']:.2f}M (Confidence: {data['confidence']})")
        
        if 'average' in fair_value:
            print(f"\n  Average Fair Value: ${fair_value['average']:.2f}M")
            print(f"  Median Fair Value: ${fair_value['median']:.2f}M")
            print(f"  Standard Deviation: ${fair_value['std']:.2f}M")
        
        # Investment Recommendation
        attractiveness = valuation_results['attractiveness']
        print(f"\n INVESTMENT RECOMMENDATION:")
        print(f"  Recommendation: {attractiveness['recommendation']}")
        print(f"  Confidence: {attractiveness['confidence']}")
        print(f"  Score: {attractiveness['score']}/10")
        print(f"\n  Key Factors:")
        for factor in attractiveness['factors']:
            print(f"    • {factor}")
        
        # DCF Details (if available)
        if 'dcf_method' in fair_value:
            dcf_details = fair_value['dcf_method']['details']
            print(f"\n DCF ANALYSIS DETAILS:")
            print(f"  Projection Years: {dcf_details['projection_years']}")
            print(f"  Discount Rate: {dcf_details['discount_rate']:.1f}%")
            print(f"  Terminal Growth: {dcf_details['terminal_growth_rate']:.1f}%")
            print(f"  Historical Revenue Growth: {dcf_details['historical_avg_revenue_growth']:.1f}%")
            print(f"  Historical EBITDA Margin: {dcf_details['historical_avg_ebitda_margin']:.1f}%")
            print(f"  Enterprise Value: ${dcf_details['enterprise_value_millions']:.2f}M")
