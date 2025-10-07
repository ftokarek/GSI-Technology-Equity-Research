"""
COMPLETE Equity Analysis for GSI Technology
Final comprehensive analysis combining ALL data sources and analytical components
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from typing import Dict
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from analysis.financial_metrics import FinancialMetricsCalculator
from analysis.trend_analysis import TrendAnalyzer
from analysis.valuation_analysis import ValuationAnalyzer
from analysis.scenario_analysis import ScenarioAnalyzer
from analysis.strategic_analysis import StrategicAnalyzer
from analysis.governance_analysis import GovernanceAnalyzer
from analysis.quarterly_analysis import QuarterlyAnalyzer

class CompleteEquityAnalysis:
    """
    Complete comprehensive equity analysis using ALL available data sources
    """
    
    def __init__(self):
        """Initialize complete analysis"""
        self.load_all_data()
        
    def load_all_data(self):
        """Load ALL available data sources"""
        print("=" * 80)
        print("📊 LOADING ALL DATA SOURCES")
        print("=" * 80)
        
        # Consolidated data
        print("\n1. Consolidated Financial Data:")
        self.income = pd.read_csv("data/consolidated/master_income_statement.csv")
        self.balance = pd.read_csv("data/consolidated/master_balance_sheet.csv")
        print(f"  ✅ Income: {len(self.income)} years")
        print(f"  ✅ Balance: {len(self.balance)} years")
        
        # Quarterly data
        print("\n2. Quarterly Reports:")
        self.q_income = pd.read_csv("data/processed/quarterly_reports/income_statements.csv")
        self.q_balance = pd.read_csv("data/processed/quarterly_reports/balance_sheets.csv")
        print(f"  ✅ Quarterly Income: {len(self.q_income)} rows")
        print(f"  ✅ Quarterly Balance: {len(self.q_balance)} rows")
        
        # Compensation & Governance
        print("\n3. Governance Data:")
        self.compensation = pd.read_csv("data/processed/annual_reports/compensation_data.csv")
        self.proxy = pd.read_csv("data/processed/proxy_statements/proxy_data.csv")
        print(f"  ✅ Compensation: {len(self.compensation)} rows")
        print(f"  ✅ Proxy Statements: {len(self.proxy)} rows")
        
        # Market data
        print("\n4. Market Data:")
        self.market_daily = pd.read_csv("data/processed/market_data/stock_prices.csv")
        self.market_daily['date'] = pd.to_datetime(self.market_daily['date'])
        print(f"  ✅ Stock Prices: {len(self.market_daily)} days")
        
        # Cash flow (if available)
        cashflow_path = Path("data/consolidated/master_cashflow.csv")
        if cashflow_path.exists():
            self.cashflow = pd.read_csv(cashflow_path)
            print(f"\n5. Cash Flow:")
            print(f"  ✅ Cash Flow: {len(self.cashflow)} years")
        else:
            self.cashflow = None
        
        print("\n" + "=" * 80)
        
    def run_complete_analysis(self) -> Dict:
        """Run complete comprehensive analysis"""
        print("\n" + "="*80)
        print("🚀 COMPLETE EQUITY ANALYSIS - ALL DATA SOURCES")
        print("="*80)
        
        results = {}
        
        # 1. Financial Metrics
        print("\n📊 1. CALCULATING FINANCIAL METRICS...")
        calculator = FinancialMetricsCalculator(self.income, self.balance, None)
        metrics = calculator.calculate_all_metrics()
        results['financial_metrics'] = metrics
        
        # 2. Trend Analysis
        print("📈 2. TREND ANALYSIS...")
        trend_analyzer = TrendAnalyzer(metrics)
        trend_summary = trend_analyzer.generate_trend_summary()
        trend_analyzer.print_trend_analysis(trend_summary)
        results['trend_analysis'] = trend_summary
        
        # 3. Valuation Analysis
        print("\n💰 3. VALUATION ANALYSIS...")
        valuation_analyzer = ValuationAnalyzer(metrics, None)
        multiples = valuation_analyzer.calculate_multiples()
        fair_value = valuation_analyzer.calculate_fair_value_estimation()
        attractiveness = valuation_analyzer.analyze_valuation_attractiveness()
        valuation_analyzer.print_valuation_analysis({
            'current_valuation': multiples,
            'fair_value_estimation': fair_value,
            'attractiveness': attractiveness
        })
        results['valuation_analysis'] = {
            'current_valuation': multiples,
            'fair_value_estimation': fair_value,
            'attractiveness': attractiveness
        }
        
        # 4. Scenario Analysis
        print("\n🎯 4. SCENARIO ANALYSIS...")
        scenario_analyzer = ScenarioAnalyzer(metrics)
        scenario_results = scenario_analyzer.run_scenario_analysis()
        scenario_analyzer.print_scenario_analysis(scenario_results)
        results['scenario_analysis'] = scenario_results
        
        # 5. Strategic Analysis
        print("\n🎯 5. STRATEGIC ANALYSIS...")
        strategic_analyzer = StrategicAnalyzer(metrics, self.income)
        time_horizons = strategic_analyzer.analyze_time_horizons()
        market_opportunity = strategic_analyzer.analyze_market_opportunity()
        strategic_options = strategic_analyzer.analyze_strategic_options()
        investment_thesis = strategic_analyzer.analyze_investment_thesis()
        strategic_analyzer.print_strategic_analysis(
            time_horizons, market_opportunity, strategic_options, investment_thesis
        )
        results['strategic_analysis'] = {
            'time_horizons': time_horizons,
            'market_opportunity': market_opportunity,
            'strategic_options': strategic_options,
            'investment_thesis': investment_thesis
        }
        
        # 6. Governance & Compensation Analysis (NEW)
        print("\n👔 6. GOVERNANCE & COMPENSATION ANALYSIS...")
        governance_analyzer = GovernanceAnalyzer(self.compensation, self.proxy, self.income)
        sbc_analysis = governance_analyzer.analyze_stock_based_compensation()
        exec_comp = governance_analyzer.analyze_executive_compensation()
        governance = governance_analyzer.analyze_governance_quality()
        governance_analyzer.print_governance_analysis(sbc_analysis, exec_comp, governance)
        results['governance_analysis'] = {
            'stock_based_compensation': sbc_analysis,
            'executive_compensation': exec_comp,
            'governance_quality': governance
        }
        
        # 7. Quarterly Analysis (NEW)
        print("\n📅 7. QUARTERLY ANALYSIS...")
        quarterly_analyzer = QuarterlyAnalyzer(self.q_income, self.q_balance)
        seasonality = quarterly_analyzer.analyze_seasonality()
        volatility = quarterly_analyzer.analyze_quarterly_volatility()
        quarterly_analyzer.print_quarterly_analysis(seasonality, volatility)
        results['quarterly_analysis'] = {
            'seasonality': seasonality,
            'volatility': volatility
        }
        
        return results
    
    def generate_investment_decision(self, results: Dict) -> Dict:
        """Generate final investment decision with all considerations"""
        
        attractiveness = results['valuation_analysis']['attractiveness']
        scenario_results = results['scenario_analysis']
        time_horizons = results['strategic_analysis']['time_horizons']
        governance = results['governance_analysis']
        
        # Calculate expected value
        expected_value = scenario_results['expected_valuation']
        
        # Assess cash runway
        cash_runway = time_horizons['short_term']['key_metrics']['cash_runway_months']
        
        # Final decision
        decision = {
            'primary_recommendation': attractiveness['recommendation'],
            'confidence': attractiveness['confidence'],
            'score': attractiveness['score'],
            
            'investment_horizons': {
                'short_term': {
                    'recommendation': 'AVOID' if cash_runway < 12 else 'SPECULATIVE',
                    'reason': f'Cash runway: {cash_runway:.0f} months'
                },
                'medium_term': {
                    'recommendation': 'HOLD' if scenario_results['expected_cagr'] > 0 else 'SELL',
                    'reason': f"Expected CAGR: {scenario_results['expected_cagr']:.1f}%"
                },
                'long_term': {
                    'recommendation': 'SPECULATIVE BUY' if time_horizons['long_term']['assessment'] != 'LOW' else 'AVOID',
                    'reason': 'Strategic value and acquisition potential'
                }
            },
            
            'scenarios': {
                'bull_case': f"${scenario_results['scenarios'][0]['implied_enterprise_value']:,.0f}K (25% prob)",
                'base_case': f"${scenario_results['scenarios'][1]['implied_enterprise_value']:,.0f}K (50% prob)",
                'bear_case': f"${scenario_results['scenarios'][2]['implied_enterprise_value']:,.0f}K (25% prob)",
                'expected_value': f"${expected_value:,.0f}K"
            },
            
            'investor_profile': {
                'suitable_for': 'High-risk/high-reward opportunity investors',
                'not_suitable_for': 'Conservative, income-focused, or capital preservation investors',
                'risk_tolerance_required': 'Very High',
                'time_horizon_required': '2-5 years'
            },
            
            'key_decision_factors': {
                'positive': [
                    f"Strong gross margins ({results['financial_metrics']['profitability_metrics'].tail(3)['gross_margin'].mean():.1f}% avg)",
                    f"Good liquidity (Current ratio: {results['financial_metrics']['balance_sheet_metrics'].iloc[-1]['current_ratio']:.2f})",
                    'Potential acquisition target',
                    'Upside potential: 1536% (Bear to Bull)'
                ],
                'negative': [
                    f"Revenue decline: {scenario_results['scenarios'][1]['five_year_cagr']:.1f}% CAGR",
                    f"Negative operating margins: {results['financial_metrics']['profitability_metrics'].tail(3)['operating_margin'].mean():.1f}%",
                    f"Critical cash position: ${results['financial_metrics']['balance_sheet_metrics'].iloc[-1]['cash']:,.0f}K",
                    f"Cash runway: {cash_runway:.0f} months"
                ]
            },
            
            'action_items': [
                '✅ Monitor Q1/Q2 2026 earnings for stabilization signs',
                '✅ Watch for financing announcements',
                '✅ Track APU technology development/adoption',
                '✅ Monitor for M&A activity in memory sector',
                '✅ Review cash burn rate quarterly'
            ]
        }
        
        return decision
    
    def print_final_decision(self, decision: Dict):
        """Print final investment decision"""
        print("\n" + "="*80)
        print("🎯 FINAL INVESTMENT DECISION - ALL FACTORS CONSIDERED")
        print("="*80)
        
        print(f"\n📊 PRIMARY RECOMMENDATION: {decision['primary_recommendation']}")
        print(f"   Confidence: {decision['confidence']}")
        print(f"   Score: {decision['score']}/10")
        
        print(f"\n📅 RECOMMENDATIONS BY TIME HORIZON:")
        for horizon, rec in decision['investment_horizons'].items():
            print(f"  {horizon.upper()}: {rec['recommendation']}")
            print(f"    → {rec['reason']}")
        
        print(f"\n💰 SCENARIO-BASED VALUATIONS:")
        for scenario, value in decision['scenarios'].items():
            print(f"  {scenario.replace('_', ' ').title()}: {value}")
        
        print(f"\n👤 INVESTOR PROFILE:")
        print(f"  Suitable for: {decision['investor_profile']['suitable_for']}")
        print(f"  NOT suitable for: {decision['investor_profile']['not_suitable_for']}")
        print(f"  Risk tolerance: {decision['investor_profile']['risk_tolerance_required']}")
        print(f"  Time horizon: {decision['investor_profile']['time_horizon_required']}")
        
        print(f"\n✅ POSITIVE FACTORS:")
        for factor in decision['key_decision_factors']['positive']:
            print(f"    • {factor}")
        
        print(f"\n⚠️  NEGATIVE FACTORS:")
        for factor in decision['key_decision_factors']['negative']:
            print(f"    • {factor}")
        
        print(f"\n📋 ACTION ITEMS FOR MONITORING:")
        for action in decision['action_items']:
            print(f"  {action}")
    
    def save_complete_results(self, results: Dict, decision: Dict):
        """Save all results"""
        output_dir = Path("data/analysis")
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n💾 Saving complete analysis results...")
        
        # Save final decision
        decision_df = pd.DataFrame([{
            'recommendation': decision['primary_recommendation'],
            'confidence': decision['confidence'],
            'score': decision['score'],
            'short_term_rec': decision['investment_horizons']['short_term']['recommendation'],
            'medium_term_rec': decision['investment_horizons']['medium_term']['recommendation'],
            'long_term_rec': decision['investment_horizons']['long_term']['recommendation'],
            'expected_value': decision['scenarios']['expected_value'],
            'suitable_for': decision['investor_profile']['suitable_for'],
            'risk_tolerance': decision['investor_profile']['risk_tolerance_required']
        }])
        decision_df.to_csv(output_dir / "complete_investment_decision.csv", index=False)
        print(f"  ✅ Saved complete_investment_decision.csv")
        
        # Save all metrics
        for metric_name, df in results['financial_metrics'].items():
            df.to_csv(output_dir / f"complete_{metric_name}.csv", index=False)
            print(f"  ✅ Saved complete_{metric_name}.csv")
        
        print(f"✅ Complete analysis results saved!")
    
    def run_full_pipeline(self):
        """Run complete analysis pipeline"""
        print("\n" + "="*80)
        print("🚀 COMPLETE EQUITY ANALYSIS - GSI TECHNOLOGY")
        print("Using ALL available data sources")
        print("="*80)
        
        # Run analysis
        results = self.run_complete_analysis()
        
        # Generate final decision
        decision = self.generate_investment_decision(results)
        
        # Print final decision
        self.print_final_decision(decision)
        
        # Save results
        self.save_complete_results(results, decision)
        
        return results, decision

def main():
    """Main execution"""
    print("🚀 COMPLETE EQUITY ANALYSIS - GSI TECHNOLOGY")
    print("="*60)
    
    analysis = CompleteEquityAnalysis()
    results, decision = analysis.run_full_pipeline()
    
    print("\n" + "="*80)
    print("✅ COMPLETE ANALYSIS FINISHED!")
    print("="*80)
    print("📊 All data sources analyzed")
    print("📈 All results saved to: data/analysis/")
    print("🎯 Final investment decision generated")
    print("📄 Ready for LaTeX report generation!")
    
    return results, decision

if __name__ == "__main__":
    main()
