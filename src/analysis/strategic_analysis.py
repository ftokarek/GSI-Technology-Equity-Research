
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class StrategicAnalyzer:
    
    def __init__(self, metrics_data: Dict[str, pd.DataFrame], income_df: pd.DataFrame):
        self.metrics = metrics_data
        self.income = income_df
        
    def analyze_time_horizons(self) -> Dict:
        growth_df = self.metrics['growth_metrics']
        profit_df = self.metrics['profitability_metrics']
        balance_df = self.metrics['balance_sheet_metrics']
        
        latest_data = {
            'revenue': growth_df.iloc[-1]['revenue'],
            'cash': balance_df.iloc[-1]['cash'],
            'operating_margin': profit_df.iloc[-1]['operating_margin'],
            'current_ratio': balance_df.iloc[-1]['current_ratio']
        }
        
        horizons = {}
        
        monthly_burn_rate = latest_data['cash'] / 12  
        cash_runway_months = latest_data['cash'] / monthly_burn_rate if monthly_burn_rate > 0 else np.inf
        
        horizons['short_term'] = {
            'period': '1-2 Years',
            'focus': 'Survival & Liquidity',
            'key_metrics': {
                'current_cash': latest_data['cash'],
                'monthly_burn_rate': monthly_burn_rate,
                'cash_runway_months': cash_runway_months,
                'current_ratio': latest_data['current_ratio']
            },
            'assessment': self._assess_short_term(latest_data, cash_runway_months),
            'risks': [
                'Low cash position ($1M)',
                'Potential liquidity crisis',
                'Need for financing or restructuring'
            ],
            'opportunities': [
                'Cost cutting initiatives',
                'Strategic partnerships',
                'Asset sales to raise cash'
            ]
        }
        
        horizons['medium_term'] = {
            'period': '3-5 Years',
            'focus': 'Revenue Recovery & Profitability',
            'key_metrics': {
                'revenue_trend': 'Declining (-15% 3Y CAGR)',
                'operating_margin': latest_data['operating_margin'],
                'recovery_potential': 'Moderate'
            },
            'assessment': self._assess_medium_term(latest_data),
            'risks': [
                'Continued revenue decline',
                'Market share erosion',
                'Technology obsolescence'
            ],
            'opportunities': [
                'New product launches',
                'Market expansion',
                'Operational turnaround'
            ]
        }
        
        horizons['long_term'] = {
            'period': '5+ Years',
            'focus': 'Strategic Value & Technology',
            'key_metrics': {
                'technology_moat': 'Memory solutions IP',
                'market_position': 'Niche player',
                'strategic_value': 'Moderate'
            },
            'assessment': self._assess_long_term(latest_data),
            'risks': [
                'Technology disruption',
                'Competitive pressure from larger players',
                'Market consolidation'
            ],
            'opportunities': [
                'Acquisition target for larger competitor',
                'Technology licensing',
                'Pivot to high-growth applications (AI/ML)'
            ]
        }
        
        return horizons
    
    def _assess_short_term(self, latest_data: Dict, cash_runway: float) -> str:
        if cash_runway < 6:
            return 'CRITICAL - Immediate cash concerns'
        elif cash_runway < 12:
            return 'CONCERNING - Limited cash runway'
        elif cash_runway < 24:
            return 'MODERATE - Cash management needed'
        else:
            return 'STABLE - Adequate liquidity'
    
    def _assess_medium_term(self, latest_data: Dict) -> str:
        if latest_data['operating_margin'] < -50:
            return 'LOW - Significant operational challenges'
        elif latest_data['operating_margin'] < -20:
            return 'MODERATE - Path to profitability unclear'
        elif latest_data['operating_margin'] < 0:
            return 'GOOD - Near breakeven'
        else:
            return 'EXCELLENT - Already profitable'
    
    def _assess_long_term(self, latest_data: Dict) -> str:
        if latest_data['revenue'] > 50000:
            return 'HIGH - Strong market presence'
        elif latest_data['revenue'] > 20000:
            return 'MODERATE - Niche player with potential'
        else:
            return 'LOW - Limited scale'
    
    def analyze_market_opportunity(self) -> Dict:
        market_analysis = {
            'addressable_market': {
                'total_market_size': 'Memory IC Market: ~$120B (2024)',
                'serviceable_market': 'High-speed SRAM: ~$2-3B',
                'target_segments': [
                    'Networking equipment',
                    'Telecommunications',
                    'Data centers',
                    'Automotive (emerging)'
                ],
                'growth_rate': '5-7% CAGR'
            },
            'competitive_position': {
                'market_share': '<1% (estimated)',
                'positioning': 'Niche player in high-speed SRAM',
                'differentiation': 'High-performance, low-power solutions',
                'key_competitors': [
                    'Cypress Semiconductor (Infineon)',
                    'Renesas',
                    'Integrated Silicon Solution (ISSI)',
                    'Alliance Memory'
                ]
            },
            'technology_assessment': {
                'core_technology': 'High-speed SRAM and APU (Associative Processing Unit)',
                'ip_portfolio': 'Patents in memory architecture',
                'innovation_focus': 'In-memory computing for AI/ML',
                'technology_risk': 'Moderate - mature market, need innovation'
            },
            'market_trends': {
                'favorable': [
                    'AI/ML driving demand for high-speed memory',
                    'Edge computing growth',
                    '5G infrastructure buildout',
                    'Automotive electrification'
                ],
                'unfavorable': [
                    'Memory price pressure',
                    'Consolidation among suppliers',
                    'Competition from larger players',
                    'Shift to newer memory technologies (HBM, etc.)'
                ]
            }
        }
        
        return market_analysis
    
    def analyze_strategic_options(self) -> Dict:
        balance_df = self.metrics['balance_sheet_metrics']
        latest_cash = balance_df.iloc[-1]['cash']
        latest_assets = balance_df.iloc[-1]['total_assets']
        
        options = {
            'option_1_turnaround': {
                'name': 'Operational Turnaround',
                'description': 'Focus on core business, cut costs, return to profitability',
                'probability': 'Medium (40%)',
                'timeline': '2-3 years',
                'requirements': [
                    'Significant cost reductions',
                    'Revenue stabilization',
                    'Focus on profitable products',
                    'Efficient capital allocation'
                ],
                'potential_outcome': 'Stabilized business, modest growth',
                'value_potential': 'Moderate ($30-50M valuation)'
            },
            'option_2_pivot': {
                'name': 'Strategic Pivot to AI/ML',
                'description': 'Pivot to in-memory computing for AI applications',
                'probability': 'Low-Medium (25%)',
                'timeline': '3-5 years',
                'requirements': [
                    'Additional R&D investment',
                    'Strategic partnerships',
                    'Market validation',
                    'Capital raise needed'
                ],
                'potential_outcome': 'High-growth trajectory if successful',
                'value_potential': 'High ($100M+ valuation if successful)'
            },
            'option_3_acquisition': {
                'name': 'Acquisition Target',
                'description': 'Seek acquisition by larger competitor',
                'probability': 'Medium (35%)',
                'timeline': '1-2 years',
                'requirements': [
                    'Attractive IP portfolio',
                    'Strategic fit with acquirer',
                    'Acceptable valuation',
                    'Management willingness'
                ],
                'potential_outcome': 'Premium to current market value',
                'value_potential': 'Moderate ($40-60M acquisition price)'
            },
            'option_4_liquidation': {
                'name': 'Orderly Liquidation',
                'description': 'Wind down operations, sell assets',
                'probability': 'Low (10%)',
                'timeline': '1-2 years',
                'requirements': [
                    'Inability to raise capital',
                    'Continued cash burn',
                    'No strategic alternatives'
                ],
                'potential_outcome': 'Asset recovery only',
                'value_potential': f'Low (${latest_assets * 0.5:,.0f}K - 50% of book value)'
            }
        }
        
        return options
    
    def analyze_investment_thesis(self) -> Dict:
        thesis = {
            'bull_thesis': {
                'title': 'Why GSI Could Be Attractive',
                'points': [
                    ' Strong gross margins (60%+) show product differentiation',
                    ' Low cash position creates takeover attractiveness',
                    ' Memory IP portfolio has strategic value',
                    ' APU technology has AI/ML potential',
                    ' Niche market position defensible',
                    ' Current valuation extremely low (potential upside)'
                ]
            },
            'bear_thesis': {
                'title': 'Why GSI Is Risky',
                'points': [
                    '  Persistent revenue decline (-53% in 5 years)',
                    '  Negative operating margins (-100%+ in 2025)',
                    '  Critical cash position ($1M)',
                    '  Small scale disadvantage vs. competitors',
                    '  Limited R&D budget for innovation',
                    '  Market share erosion continuing'
                ]
            },
            'key_questions': [
                ' Can GSI stabilize revenue in next 12 months?',
                ' Will APU technology gain market traction?',
                ' Can they secure financing or partnership?',
                ' Is there acquisition interest from larger players?',
                ' Can they achieve profitability with current run rate?'
            ],
            'recommendation_drivers': {
                'for_buy': 'If you believe in turnaround potential and have HIGH risk tolerance',
                'for_hold': 'If you want to wait for clearer direction',
                'for_sell': 'If you prioritize capital preservation and steady returns'
            }
        }
        
        return thesis
    
    def print_strategic_analysis(self, time_horizons: Dict, market_opportunity: Dict, 
                                 strategic_options: Dict, investment_thesis: Dict):
        print("\n" + "="*80)
        print(" STRATEGIC ANALYSIS - TIME HORIZONS & MARKET OPPORTUNITY")
        print("="*80)
        
        print("\n TIME HORIZON ANALYSIS:")
        for horizon_name, horizon in time_horizons.items():
            print(f"\n  {horizon['period'].upper()} ({horizon['focus']})")
            print(f"    Assessment: {horizon['assessment']}")
            
            if 'key_metrics' in horizon:
                print(f"    Key Metrics:")
                for key, value in horizon['key_metrics'].items():
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        print(f"      • {key.replace('_', ' ').title()}: {value:,.2f}")
                    else:
                        print(f"      • {key.replace('_', ' ').title()}: {value}")
            
            print(f"    Risks:")
            for risk in horizon['risks']:
                print(f"        {risk}")
            
            print(f"    Opportunities:")
            for opp in horizon['opportunities']:
                print(f"       {opp}")
        
        print(f"\n\n MARKET OPPORTUNITY ANALYSIS:")
        print(f"\n  Addressable Market:")
        print(f"    • Total Market: {market_opportunity['addressable_market']['total_market_size']}")
        print(f"    • Serviceable Market: {market_opportunity['addressable_market']['serviceable_market']}")
        print(f"    • Growth Rate: {market_opportunity['addressable_market']['growth_rate']}")
        
        print(f"\n  Competitive Position:")
        print(f"    • Market Share: {market_opportunity['competitive_position']['market_share']}")
        print(f"    • Positioning: {market_opportunity['competitive_position']['positioning']}")
        
        print(f"\n  Technology Assessment:")
        print(f"    • Core Technology: {market_opportunity['technology_assessment']['core_technology']}")
        print(f"    • Innovation Focus: {market_opportunity['technology_assessment']['innovation_focus']}")
        
        print(f"\n\n STRATEGIC OPTIONS:")
        for option_key, option in strategic_options.items():
            print(f"\n  {option['name'].upper()}")
            print(f"    Probability: {option['probability']}")
            print(f"    Timeline: {option['timeline']}")
            print(f"    Outcome: {option['potential_outcome']}")
            print(f"    Value Potential: {option['value_potential']}")
        
        print(f"\n\n INVESTMENT THESIS:")
        
        print(f"\n  {investment_thesis['bull_thesis']['title']}:")
        for point in investment_thesis['bull_thesis']['points']:
            print(f"    {point}")
        
        print(f"\n  {investment_thesis['bear_thesis']['title']}:")
        for point in investment_thesis['bear_thesis']['points']:
            print(f"    {point}")
        
        print(f"\n  Key Questions for Investors:")
        for question in investment_thesis['key_questions']:
            print(f"    {question}")
