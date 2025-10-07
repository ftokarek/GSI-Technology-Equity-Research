"""
Extended Equity Analysis for GSI Technology
Comprehensive analysis including scenarios, strategic analysis, and time horizons
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from analysis.financial_metrics import FinancialMetricsCalculator
from analysis.trend_analysis import TrendAnalyzer
from analysis.valuation_analysis import ValuationAnalyzer
from analysis.scenario_analysis import ScenarioAnalyzer
from analysis.strategic_analysis import StrategicAnalyzer

class ExtendedEquityAnalysis:
    """
    Extended comprehensive equity analysis for investment decision making
    """
    
    def __init__(self, data_dir: str = "data/consolidated"):
        """
        Initialize extended analysis
        """
        self.data_dir = Path(data_dir)
        self.load_data()
        
    def load_data(self):
        """
        Load all consolidated financial data
        """
        print("Loading consolidated financial data...")
        
        # Load main datasets
        self.income = pd.read_csv(self.data_dir / "master_income_statement.csv")
        self.balance = pd.read_csv(self.data_dir / "master_balance_sheet.csv")
        
        # Load optional datasets
        cashflow_path = self.data_dir / "master_cashflow.csv"
        market_path = self.data_dir / "market_data_annual.csv"
        
        self.cashflow = pd.read_csv(cashflow_path) if cashflow_path.exists() else None
        self.market = pd.read_csv(market_path) if market_path.exists() else None
        
        print(f"✅ Loaded data:")
        print(f"  Income Statement: {len(self.income)} years")
        print(f"  Balance Sheet: {len(self.balance)} years")
        
    def run_extended_analysis(self) -> Dict:
        """
        Run extended comprehensive analysis
        """
        print("\n" + "="*80)
        print("🚀 EXTENDED EQUITY ANALYSIS - GSI TECHNOLOGY")
        print("="*80)
        
        # Step 1: Financial Metrics
        print("\n📊 STEP 1: CALCULATING FINANCIAL METRICS...")
        calculator = FinancialMetricsCalculator(
            self.income, 
            self.balance, 
            self.market
        )
        metrics = calculator.calculate_all_metrics()
        
        # Step 2: Trend Analysis
        print("\n📈 STEP 2: TREND ANALYSIS...")
        trend_analyzer = TrendAnalyzer(metrics)
        trend_summary = trend_analyzer.generate_trend_summary()
        
        # Step 3: Valuation Analysis
        print("\n💰 STEP 3: VALUATION ANALYSIS...")
        valuation_analyzer = ValuationAnalyzer(metrics, self.market)
        multiples = valuation_analyzer.calculate_multiples()
        fair_value = valuation_analyzer.calculate_fair_value_estimation()
        attractiveness = valuation_analyzer.analyze_valuation_attractiveness()
        
        # Step 4: Scenario Analysis (NEW)
        print("\n🎯 STEP 4: SCENARIO ANALYSIS (BULL/BASE/BEAR)...")
        scenario_analyzer = ScenarioAnalyzer(metrics)
        scenario_results = scenario_analyzer.run_scenario_analysis()
        
        # Step 5: Strategic Analysis (NEW)
        print("\n🎯 STEP 5: STRATEGIC ANALYSIS (TIME HORIZONS & MARKET)...")
        strategic_analyzer = StrategicAnalyzer(metrics, self.income)
        time_horizons = strategic_analyzer.analyze_time_horizons()
        market_opportunity = strategic_analyzer.analyze_market_opportunity()
        strategic_options = strategic_analyzer.analyze_strategic_options()
        investment_thesis = strategic_analyzer.analyze_investment_thesis()
        
        # Combine all results
        extended_results = {
            'financial_metrics': metrics,
            'trend_analysis': trend_summary,
            'valuation_analysis': {
                'current_valuation': multiples,
                'fair_value_estimation': fair_value,
                'attractiveness': attractiveness
            },
            'scenario_analysis': scenario_results,
            'strategic_analysis': {
                'time_horizons': time_horizons,
                'market_opportunity': market_opportunity,
                'strategic_options': strategic_options,
                'investment_thesis': investment_thesis
            }
        }
        
        return extended_results
    
    def print_extended_summary(self, results: Dict):
        """
        Print extended analysis summary
        """
        # Print scenario analysis
        scenario_analyzer = ScenarioAnalyzer(results['financial_metrics'])
        scenario_analyzer.print_scenario_analysis(results['scenario_analysis'])
        
        # Print strategic analysis
        strategic_analyzer = StrategicAnalyzer(results['financial_metrics'], self.income)
        strategic_analyzer.print_strategic_analysis(
            results['strategic_analysis']['time_horizons'],
            results['strategic_analysis']['market_opportunity'],
            results['strategic_analysis']['strategic_options'],
            results['strategic_analysis']['investment_thesis']
        )
    
    def generate_final_recommendation(self, results: Dict) -> Dict:
        """
        Generate final investment recommendation based on all analyses
        """
        attractiveness = results['valuation_analysis']['attractiveness']
        scenario_results = results['scenario_analysis']
        time_horizons = results['strategic_analysis']['time_horizons']
        
        # Analyze across time horizons
        short_term_viable = 'CRITICAL' not in time_horizons['short_term']['assessment']
        medium_term_potential = 'LOW' not in time_horizons['medium_term']['assessment']
        long_term_strategic = 'HIGH' in time_horizons['long_term']['assessment']
        
        # Scenario-based recommendation
        expected_cagr = scenario_results['expected_cagr']
        bull_case_value = scenario_results['scenarios'][0]['implied_enterprise_value']
        bear_case_value = scenario_results['scenarios'][2]['implied_enterprise_value']
        
        # Risk/Reward analysis
        upside_potential = (bull_case_value - bear_case_value) / bear_case_value * 100
        
        recommendation = {
            'primary_recommendation': attractiveness['recommendation'],
            'confidence': attractiveness['confidence'],
            'score': attractiveness['score'],
            'time_horizon_assessment': {
                'short_term': time_horizons['short_term']['assessment'],
                'medium_term': time_horizons['medium_term']['assessment'],
                'long_term': time_horizons['long_term']['assessment']
            },
            'scenario_based_view': {
                'expected_5y_cagr': expected_cagr,
                'upside_potential': upside_potential,
                'best_case_value': bull_case_value,
                'worst_case_value': bear_case_value
            },
            'investment_suitability': self._determine_suitability(
                attractiveness['score'],
                short_term_viable,
                expected_cagr,
                upside_potential
            ),
            'key_catalysts': [
                'Revenue stabilization',
                'Path to profitability',
                'Strategic partnership or acquisition',
                'APU technology adoption'
            ],
            'key_risks': [
                'Cash runway concerns',
                'Continued revenue decline',
                'Market share erosion',
                'Need for dilutive financing'
            ]
        }
        
        return recommendation
    
    def _determine_suitability(self, score: int, short_term_viable: bool, 
                               expected_cagr: float, upside: float) -> str:
        """
        Determine investment suitability
        """
        if score >= 2 and short_term_viable and expected_cagr > 5:
            return 'Suitable for GROWTH-oriented investors with HIGH risk tolerance'
        elif score >= 0 and short_term_viable:
            return 'Suitable for SPECULATIVE investors willing to bet on turnaround'
        elif upside > 200:
            return 'Suitable for HIGH-RISK/HIGH-REWARD opportunity investors'
        elif not short_term_viable:
            return 'NOT SUITABLE - High risk of capital loss'
        else:
            return 'Suitable only for DEEP VALUE investors betting on liquidation value'
    
    def save_extended_results(self, results: Dict, output_dir: str = "data/analysis"):
        """
        Save extended analysis results
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 Saving extended analysis results...")
        
        # Save scenario analysis
        scenarios_list = []
        for scenario in results['scenario_analysis']['scenarios']:
            scenario_summary = {
                'name': scenario['name'],
                'probability': scenario['probability'],
                'five_year_revenue': scenario['five_year_revenue'],
                'five_year_cagr': scenario['five_year_cagr'],
                'implied_enterprise_value': scenario['implied_enterprise_value']
            }
            scenarios_list.append(scenario_summary)
        
        scenarios_df = pd.DataFrame(scenarios_list)
        scenarios_df.to_csv(output_path / "scenario_analysis_summary.csv", index=False)
        print(f"  ✅ Saved scenario_analysis_summary.csv")
        
        # Save scenario projections
        for scenario in results['scenario_analysis']['scenarios']:
            projections_df = pd.DataFrame(scenario['projections'])
            filename = f"scenario_projections_{scenario['name'].lower().replace(' ', '_').replace('-', '')}.csv"
            projections_df.to_csv(output_path / filename, index=False)
            print(f"  ✅ Saved {filename}")
        
        # Save strategic analysis
        time_horizons_list = []
        for horizon_name, horizon in results['strategic_analysis']['time_horizons'].items():
            time_horizons_list.append({
                'horizon': horizon_name,
                'period': horizon['period'],
                'focus': horizon['focus'],
                'assessment': horizon['assessment']
            })
        
        time_horizons_df = pd.DataFrame(time_horizons_list)
        time_horizons_df.to_csv(output_path / "time_horizons_analysis.csv", index=False)
        print(f"  ✅ Saved time_horizons_analysis.csv")
        
        # Save final recommendation
        final_rec = self.generate_final_recommendation(results)
        final_rec_df = pd.DataFrame([{
            'recommendation': final_rec['primary_recommendation'],
            'confidence': final_rec['confidence'],
            'score': final_rec['score'],
            'expected_5y_cagr': final_rec['scenario_based_view']['expected_5y_cagr'],
            'upside_potential': final_rec['scenario_based_view']['upside_potential'],
            'investment_suitability': final_rec['investment_suitability']
        }])
        final_rec_df.to_csv(output_path / "final_recommendation.csv", index=False)
        print(f"  ✅ Saved final_recommendation.csv")
        
        print(f"✅ All extended analysis results saved!")
        
        return final_rec
    
    def run_full_extended_analysis(self):
        """
        Run complete extended analysis pipeline
        """
        # Run analysis
        results = self.run_extended_analysis()
        
        # Print extended summary
        self.print_extended_summary(results)
        
        # Generate and print final recommendation
        final_rec = self.generate_final_recommendation(results)
        
        print("\n" + "="*80)
        print("🎯 FINAL INVESTMENT RECOMMENDATION")
        print("="*80)
        print(f"\n  Recommendation: {final_rec['primary_recommendation']}")
        print(f"  Confidence: {final_rec['confidence']}")
        print(f"  Score: {final_rec['score']}/10")
        print(f"\n  Expected 5-Year CAGR: {final_rec['scenario_based_view']['expected_5y_cagr']:.1f}%")
        print(f"  Upside Potential: {final_rec['scenario_based_view']['upside_potential']:.0f}%")
        print(f"\n  Investment Suitability:")
        print(f"    {final_rec['investment_suitability']}")
        
        print(f"\n  Key Catalysts:")
        for catalyst in final_rec['key_catalysts']:
            print(f"    ✅ {catalyst}")
        
        print(f"\n  Key Risks:")
        for risk in final_rec['key_risks']:
            print(f"    ⚠️  {risk}")
        
        # Save results
        self.save_extended_results(results)
        
        return results

def main():
    """
    Main execution function
    """
    print("🚀 EXTENDED EQUITY ANALYSIS - GSI TECHNOLOGY")
    print("="*60)
    
    # Initialize analysis
    analysis = ExtendedEquityAnalysis()
    
    # Run full extended analysis
    results = analysis.run_full_extended_analysis()
    
    print("\n" + "="*80)
    print("✅ EXTENDED ANALYSIS COMPLETE!")
    print("="*80)
    print("📊 All results saved to: data/analysis/")
    print("📈 Ready for LaTeX report generation!")
    print("🎯 Final investment recommendation generated!")
    
    return results

if __name__ == "__main__":
    main()
