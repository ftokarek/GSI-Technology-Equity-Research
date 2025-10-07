
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

sys.path.append(str(Path(__file__).parent.parent))

from analysis.financial_metrics import FinancialMetricsCalculator

class GSIEquityAnalysis:
    
    def __init__(self, data_dir: str = "data/consolidated"):
        self.data_dir = Path(data_dir)
        self.load_data()
        
    def load_data(self):
        print("Loading data")
        
        self.income = pd.read_csv(self.data_dir / "master_income_statement.csv")
        self.balance = pd.read_csv(self.data_dir / "master_balance_sheet.csv")
        
        cashflow_path = self.data_dir / "master_cashflow.csv"
        market_path = self.data_dir / "market_data_annual.csv"
        
        self.cashflow = pd.read_csv(cashflow_path) if cashflow_path.exists() else None
        self.market = pd.read_csv(market_path) if market_path.exists() else None
        
        print(f" Loaded data:")
        print(f"  Income Statement: {len(self.income)} years")
        print(f"  Balance Sheet: {len(self.balance)} years")
        print(f"  Cash Flow: {len(self.cashflow) if self.cashflow is not None else 0} years")
        print(f"  Market Data: {len(self.market) if self.market is not None else 0} years")
        
    def run_comprehensive_analysis(self) -> Dict:
        print("\n" + "="*80)
        print(" STARTING Comprehensive FINANCIAL ANALYSIS")
        print("="*80)
        
        calculator = FinancialMetricsCalculator(
            self.income, 
            self.balance, 
            self.market
        )
        
        print("\n Calculating metrics")
        metrics = calculator.calculate_all_metrics()
        
        print(" Calculating summary statistics...")
        summary = calculator.get_summary_statistics(metrics)
        
        analysis_results = {
            'metrics': metrics,
            'summary': summary,
            'raw_data': {
                'income': self.income,
                'balance': self.balance,
                'cashflow': self.cashflow,
                'market': self.market
            }
        }
        
        return analysis_results
    
    def print_analysis_summary(self, analysis_results: Dict):
        print("\n" + "="*80)
        print(" FINANCIAL ANALYSIS SUMMARY")
        print("="*80)
        
        metrics = analysis_results['metrics']
        summary = analysis_results['summary']
        
        print("\n REVENUE ANALYSIS:")
        growth_df = metrics['growth_metrics']
        recent_growth = growth_df[growth_df['year'] >= 2020]
        
        if not recent_growth.empty:
            print(f"  Recent Revenue (2020-2025):")
            for _, row in recent_growth.iterrows():
                year = int(row['year'])
                revenue = row['revenue']
                growth = row['revenue_growth_yoy']
                if pd.notna(revenue):
                    growth_str = f" ({growth:+.1f}%)" if pd.notna(growth) else ""
                    print(f"    {year}: ${revenue:>8,.0f}K{growth_str}")
        
        print("\n PROFITABILITY ANALYSIS:")
        profit_df = metrics['profitability_metrics']
        recent_profit = profit_df[profit_df['year'] >= 2020]
        
        if not recent_profit.empty:
            print(f"  Recent Margins (2020-2025):")
            for _, row in recent_profit.iterrows():
                year = int(row['year'])
                revenue = row['revenue']
                gross_margin = row['gross_margin']
                operating_margin = row['operating_margin']
                net_margin = row['net_margin']
                
                if pd.notna(revenue):
                    print(f"    {year}: Revenue ${revenue:>8,.0f}K")
                    if pd.notna(gross_margin):
                        print(f"           Gross Margin: {gross_margin:>6.1f}%")
                    if pd.notna(operating_margin):
                        print(f"           Operating Margin: {operating_margin:>6.1f}%")
                    if pd.notna(net_margin):
                        print(f"           Net Margin: {net_margin:>6.1f}%")
        
        print("\n BALANCE SHEET ANALYSIS:")
        balance_df = metrics['balance_sheet_metrics']
        recent_balance = balance_df[balance_df['year'] >= 2020]
        
        if not recent_balance.empty:
            print(f"  Recent Financial Position (2020-2025):")
            for _, row in recent_balance.iterrows():
                year = int(row['year'])
                cash = row['cash']
                total_assets = row['total_assets']
                debt_to_equity = row['debt_to_equity']
                current_ratio = row['current_ratio']
                
                if pd.notna(cash):
                    print(f"    {year}: Cash ${cash:>8,.0f}K", end="")
                    if pd.notna(total_assets):
                        print(f" | Assets ${total_assets:>8,.0f}K", end="")
                    if pd.notna(debt_to_equity):
                        print(f" | D/E {debt_to_equity:>5.2f}", end="")
                    if pd.notna(current_ratio):
                        print(f" | Current {current_ratio:>5.2f}", end="")
                    print()
        
        print("\n RETURNS ANALYSIS:")
        returns_df = metrics['returns_metrics']
        recent_returns = returns_df[returns_df['year'] >= 2020]
        
        if not recent_returns.empty:
            print(f"  Recent Returns (2020-2025):")
            for _, row in recent_returns.iterrows():
                year = int(row['year'])
                roe = row['roe']
                roa = row['roa']
                roic = row['roic']
                
                if pd.notna(roe) or pd.notna(roa) or pd.notna(roic):
                    print(f"    {year}:", end="")
                    if pd.notna(roe):
                        print(f" ROE {roe:>6.1f}%", end="")
                    if pd.notna(roa):
                        print(f" ROA {roa:>6.1f}%", end="")
                    if pd.notna(roic):
                        print(f" ROIC {roic:>6.1f}%", end="")
                    print()
        
        print("\n SUMMARY STATISTICS:")
        if 'growth_metrics' in summary:
            growth_stats = summary['growth_metrics']
            if 'revenue_cagr_3y_3y_avg' in growth_stats:
                print(f"  3-Year Revenue CAGR: {growth_stats['revenue_cagr_3y_3y_avg']:.1f}%")
            if 'revenue_cagr_10y_10y_avg' in growth_stats:
                print(f"  10-Year Revenue CAGR: {growth_stats['revenue_cagr_10y_10y_avg']:.1f}%")
        
        if 'profitability_metrics' in summary:
            profit_stats = summary['profitability_metrics']
            if 'gross_margin_3y_avg' in profit_stats:
                print(f"  Average Gross Margin (3Y): {profit_stats['gross_margin_3y_avg']:.1f}%")
            if 'operating_margin_3y_avg' in profit_stats:
                print(f"  Average Operating Margin (3Y): {profit_stats['operating_margin_3y_avg']:.1f}%")
        
        if 'returns_metrics' in summary:
            returns_stats = summary['returns_metrics']
            if 'roe_3y_avg' in returns_stats:
                print(f"  Average ROE (3Y): {returns_stats['roe_3y_avg']:.1f}%")
            if 'roa_3y_avg' in returns_stats:
                print(f"  Average ROA (3Y): {returns_stats['roa_3y_avg']:.1f}%")
    
    def save_analysis_results(self, analysis_results: Dict, output_dir: str = "data/analysis"):
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n💾 Saving analysis results to {output_path}...")
        
        for metric_name, df in analysis_results['metrics'].items():
            filename = f"{metric_name}.csv"
            filepath = output_path / filename
            df.to_csv(filepath, index=False)
            print(f"   Saved {filename}")
        
        summary_df = pd.DataFrame(analysis_results['summary'])
        summary_df.to_csv(output_path / "summary_statistics.csv", index=True)
        print(f"   Saved summary_statistics.csv")
        
        print(f" All analysis results saved!")
    
    def run_full_analysis(self):
        results = self.run_comprehensive_analysis()
        
        self.print_analysis_summary(results)
        
        self.save_analysis_results(results)
        
        return results

def main():
    print(" GSI Technology Equity Analysis")
    print("="*50)
    
    analysis = GSIEquityAnalysis()
    
    results = analysis.run_full_analysis()
    
    print("\n" + "="*80)
    print(" ANALYSIS Complete!")
    print("="*80)
    print(" Results saved to: data/analysis/")
    print(" Ready for LaTeX report generation!")
    
    return results

if __name__ == "__main__":
    main()
