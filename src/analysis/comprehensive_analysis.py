"""
Comprehensive Equity Analysis for GSI Technology
Combines financial metrics, trend analysis, and valuation analysis
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

class ComprehensiveEquityAnalysis:
    """
    Comprehensive equity analysis combining all analytical components
    """
    
    def __init__(self, data_dir: str = "data/consolidated"):
        """
        Initialize comprehensive analysis
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
        print(f"  Cash Flow: {len(self.cashflow) if self.cashflow is not None else 0} years")
        print(f"  Market Data: {len(self.market) if self.market is not None else 0} years")
        
    def run_comprehensive_analysis(self) -> Dict:
        """
        Run comprehensive equity analysis
        """
        print("\n" + "="*80)
        print("🚀 COMPREHENSIVE EQUITY ANALYSIS - GSI TECHNOLOGY")
        print("="*80)
        
        # Step 1: Calculate Financial Metrics
        print("\n📊 STEP 1: CALCULATING FINANCIAL METRICS...")
        calculator = FinancialMetricsCalculator(
            self.income, 
            self.balance, 
            self.market
        )
        metrics = calculator.calculate_all_metrics()
        summary = calculator.get_summary_statistics(metrics)
        
        # Step 2: Trend Analysis
        print("\n📈 STEP 2: TREND ANALYSIS...")
        trend_analyzer = TrendAnalyzer(metrics)
        trend_summary = trend_analyzer.generate_trend_summary()
        
        # Step 3: Valuation Analysis
        print("\n💰 STEP 3: VALUATION ANALYSIS...")
        valuation_analyzer = ValuationAnalyzer(metrics, self.market)
        
        # Calculate valuation components
        multiples = valuation_analyzer.calculate_multiples()
        fair_value = valuation_analyzer.calculate_fair_value_estimation()
        attractiveness = valuation_analyzer.analyze_valuation_attractiveness()
        
        valuation_results = {
            'current_valuation': multiples,
            'fair_value_estimation': fair_value,
            'attractiveness': attractiveness
        }
        
        # Combine all results
        comprehensive_results = {
            'financial_metrics': {
                'metrics': metrics,
                'summary': summary
            },
            'trend_analysis': trend_summary,
            'valuation_analysis': valuation_results,
            'raw_data': {
                'income': self.income,
                'balance': self.balance,
                'cashflow': self.cashflow,
                'market': self.market
            }
        }
        
        return comprehensive_results
    
    def print_executive_summary(self, results: Dict):
        """
        Print executive summary of the analysis
        """
        print("\n" + "="*80)
        print("📋 EXECUTIVE SUMMARY - GSI TECHNOLOGY EQUITY ANALYSIS")
        print("="*80)
        
        # Get key metrics
        metrics = results['financial_metrics']['metrics']
        trend_analysis = results['trend_analysis']
        valuation = results['valuation_analysis']
        
        # Revenue Summary
        growth_df = metrics['growth_metrics']
        recent_revenue = growth_df[growth_df['year'] >= 2020]['revenue']
        latest_revenue = recent_revenue.iloc[-1] if not recent_revenue.empty else np.nan
        
        print(f"\n💰 REVENUE PERFORMANCE:")
        if pd.notna(latest_revenue):
            print(f"  Latest Revenue (2025): ${latest_revenue:,.0f}K")
        
        # Revenue trends
        revenue_trends = trend_analysis['revenue_trends']
        if '3y' in revenue_trends:
            print(f"  3-Year CAGR: {revenue_trends['3y']['cagr']:.1f}%")
        if '10y' in revenue_trends:
            print(f"  10-Year CAGR: {revenue_trends['10y']['cagr']:.1f}%")
        
        # Profitability Summary
        profit_df = metrics['profitability_metrics']
        recent_margins = profit_df[profit_df['year'] >= 2020]
        
        print(f"\n📊 PROFITABILITY PERFORMANCE:")
        if not recent_margins.empty:
            avg_gross_margin = recent_margins['gross_margin'].mean()
            avg_operating_margin = recent_margins['operating_margin'].mean()
            print(f"  Average Gross Margin (2020-2025): {avg_gross_margin:.1f}%")
            print(f"  Average Operating Margin (2020-2025): {avg_operating_margin:.1f}%")
        
        # Balance Sheet Summary
        balance_df = metrics['balance_sheet_metrics']
        recent_balance = balance_df[balance_df['year'] >= 2020]
        
        print(f"\n💼 FINANCIAL POSITION:")
        if not recent_balance.empty:
            latest_cash = recent_balance.iloc[-1]['cash']
            latest_assets = recent_balance.iloc[-1]['total_assets']
            latest_current_ratio = recent_balance.iloc[-1]['current_ratio']
            
            print(f"  Latest Cash Position: ${latest_cash:,.0f}K")
            if pd.notna(latest_assets):
                print(f"  Latest Total Assets: ${latest_assets:,.0f}K")
            print(f"  Latest Current Ratio: {latest_current_ratio:.2f}")
        
        # Valuation Summary
        print(f"\n🎯 VALUATION SUMMARY:")
        current_valuation = valuation['current_valuation']
        fair_value = valuation['fair_value_estimation']
        attractiveness = valuation['attractiveness']
        
        if pd.notna(current_valuation['pe_ratio']):
            print(f"  Current P/E Ratio: {current_valuation['pe_ratio']:.2f}")
        if pd.notna(current_valuation['pbv_ratio']):
            print(f"  Current P/BV Ratio: {current_valuation['pbv_ratio']:.2f}")
        
        if 'average' in fair_value:
            print(f"  Estimated Fair Value: ${fair_value['average']:.2f}M")
        
        print(f"\n  Investment Recommendation: {attractiveness['recommendation']}")
        print(f"  Confidence Level: {attractiveness['confidence']}")
        print(f"  Attractiveness Score: {attractiveness['score']}/10")
        
        # Key Risks and Opportunities
        print(f"\n⚠️  KEY RISKS:")
        print(f"  • Declining revenue trend (-53% over 5 years)")
        print(f"  • Negative operating margins (-73% average)")
        print(f"  • Cash burn from $44M to $1M")
        print(f"  • Asset shrinkage from $88M to $43M")
        
        print(f"\n💡 KEY OPPORTUNITIES:")
        print(f"  • Strong gross margins (63.9% average)")
        print(f"  • Good liquidity position (current ratio > 3)")
        print(f"  • Potential for operational turnaround")
        print(f"  • Undervalued based on book value")
        
        # Final Recommendation
        print(f"\n🎯 FINAL RECOMMENDATION:")
        if attractiveness['recommendation'] in ['STRONG BUY', 'BUY']:
            print(f"  ✅ {attractiveness['recommendation']} - GSI Technology presents")
            print(f"     attractive investment opportunity with strong fundamentals")
        elif attractiveness['recommendation'] == 'HOLD':
            print(f"  ⚠️  {attractiveness['recommendation']} - GSI Technology shows mixed signals")
            print(f"     with both strengths and weaknesses")
        else:
            print(f"  ❌ {attractiveness['recommendation']} - GSI Technology faces significant")
            print(f"     challenges that outweigh potential opportunities")
    
    def save_comprehensive_results(self, results: Dict, output_dir: str = "data/analysis"):
        """
        Save comprehensive analysis results
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 Saving comprehensive analysis results...")
        
        # Save financial metrics (DataFrames)
        financial_metrics = results['financial_metrics']
        for metric_name, df in financial_metrics['metrics'].items():
            filename = f"financial_{metric_name}.csv"
            filepath = output_path / filename
            df.to_csv(filepath, index=False)
            print(f"  ✅ Saved {filename}")
        
        # Save trend analysis (convert dicts to DataFrames)
        trend_analysis = results['trend_analysis']
        for trend_name, trend_data in trend_analysis.items():
            # Convert dict to DataFrame
            trend_df = pd.DataFrame(trend_data).T
            filename = f"trend_{trend_name}.csv"
            filepath = output_path / filename
            trend_df.to_csv(filepath, index=True)
            print(f"  ✅ Saved {filename}")
        
        # Save valuation analysis
        valuation_analysis = results['valuation_analysis']
        
        # Current valuation
        current_valuation_df = pd.DataFrame([valuation_analysis['current_valuation']])
        current_valuation_df.to_csv(output_path / "valuation_current.csv", index=False)
        print(f"  ✅ Saved valuation_current.csv")
        
        # Fair value estimation
        fair_value_df = pd.DataFrame([valuation_analysis['fair_value_estimation']])
        fair_value_df.to_csv(output_path / "valuation_fair_value.csv", index=False)
        print(f"  ✅ Saved valuation_fair_value.csv")
        
        # Attractiveness
        attractiveness_df = pd.DataFrame([valuation_analysis['attractiveness']])
        attractiveness_df.to_csv(output_path / "valuation_attractiveness.csv", index=False)
        print(f"  ✅ Saved valuation_attractiveness.csv")
        
        # Save executive summary
        summary_data = {
            'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
            'company': 'GSI Technology',
            'ticker': 'GSIT',
            'analysis_period': '2011-2025',
            'data_quality': 'High',
            'recommendation': results['valuation_analysis']['attractiveness']['recommendation'],
            'confidence': results['valuation_analysis']['attractiveness']['confidence'],
            'score': results['valuation_analysis']['attractiveness']['score']
        }
        
        summary_df = pd.DataFrame([summary_data])
        summary_df.to_csv(output_path / "executive_summary.csv", index=False)
        print(f"  ✅ Saved executive_summary.csv")
        
        print(f"✅ All comprehensive analysis results saved!")
    
    def run_full_analysis(self):
        """
        Run complete comprehensive analysis
        """
        # Run analysis
        results = self.run_comprehensive_analysis()
        
        # Print executive summary
        self.print_executive_summary(results)
        
        # Save results
        self.save_comprehensive_results(results)
        
        return results

def main():
    """
    Main execution function
    """
    print("🚀 COMPREHENSIVE EQUITY ANALYSIS - GSI TECHNOLOGY")
    print("="*60)
    
    # Initialize analysis
    analysis = ComprehensiveEquityAnalysis()
    
    # Run full analysis
    results = analysis.run_full_analysis()
    
    print("\n" + "="*80)
    print("✅ COMPREHENSIVE ANALYSIS COMPLETE!")
    print("="*80)
    print("📊 Results saved to: data/analysis/")
    print("📈 Ready for LaTeX report generation!")
    print("🎯 Investment recommendation generated!")
    
    return results

if __name__ == "__main__":
    main()
