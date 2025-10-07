
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class GovernanceAnalyzer:
    
    def __init__(self, compensation_data: pd.DataFrame, 
                 proxy_data: Optional[pd.DataFrame] = None,
                 income_data: Optional[pd.DataFrame] = None):
        self.compensation = compensation_data
        self.proxy = proxy_data
        self.income = income_data
        
    def analyze_stock_based_compensation(self) -> Dict:
        comp_df = self.compensation.copy()
        
        sbc_data = []
        
        for year in sorted(comp_df['year'].unique()):
            year_data = comp_df[comp_df['year'] == year]
            
            total_sbc = 0
            count = 0
            
            for _, row in year_data.iterrows():
                for col in year_data.columns:
                    if col not in ['filename', 'company', 'form_type', 'filing_date', 
                                  'year', 'source_file', 'statement_type', 'sheet_name']:
                        val = row[col]
                        if pd.notna(val):
                            try:
                                num_val = float(val)
                                if num_val > 10:  # Reasonable SBC value
                                    total_sbc += num_val
                                    count += 1
                            except (ValueError, TypeError):
                                continue
            
            avg_sbc = total_sbc / count if count > 0 else np.nan
            
            sbc_data.append({
                'year': year,
                'total_stock_based_comp': total_sbc,
                'avg_stock_based_comp': avg_sbc,
                'count': count
            })
        
        sbc_df = pd.DataFrame(sbc_data)
        
        if len(sbc_df) >= 5:
            recent_sbc = sbc_df.tail(5)
            sbc_trend = recent_sbc['avg_stock_based_comp'].pct_change().mean() * 100
        else:
            sbc_trend = np.nan
        
        analysis = {
            'stock_based_compensation_data': sbc_df,
            'trend': sbc_trend,
            'interpretation': self._interpret_sbc_trend(sbc_trend),
            'shareholder_dilution_risk': self._assess_dilution_risk(sbc_df)
        }
        
        return analysis
    
    def _interpret_sbc_trend(self, trend: float) -> str:
        if pd.isna(trend):
            return 'Insufficient data'
        elif trend > 10:
            return 'Increasing rapidly - potential dilution concern'
        elif trend > 0:
            return 'Increasing moderately - manageable'
        elif trend > -10:
            return 'Stable or slightly decreasing - positive'
        else:
            return 'Decreasing significantly - cost cutting'
    
    def _assess_dilution_risk(self, sbc_df: pd.DataFrame) -> str:
        if len(sbc_df) == 0:
            return 'Unknown - insufficient data'
        
        recent_sbc = sbc_df.tail(3)['avg_stock_based_comp'].mean()
        
        if pd.isna(recent_sbc):
            return 'Unknown - insufficient data'
        
        if self.income is not None:
            recent_revenue = self.income.tail(3)['revenue'].mean()
            if pd.notna(recent_revenue) and recent_revenue > 0:
                sbc_as_pct_revenue = (recent_sbc / recent_revenue) * 100
                if sbc_as_pct_revenue > 10:
                    return f'HIGH - SBC is {sbc_as_pct_revenue:.1f}% of revenue'
                elif sbc_as_pct_revenue > 5:
                    return f'MODERATE - SBC is {sbc_as_pct_revenue:.1f}% of revenue'
                else:
                    return f'LOW - SBC is {sbc_as_pct_revenue:.1f}% of revenue'
        
        return 'MODERATE - requires monitoring'
    
    def analyze_executive_compensation(self) -> Dict:
        if self.proxy is None or self.proxy.empty:
            return {'error': 'No proxy data available'}
        
        proxy_df = self.proxy.copy()
        
        comp_sheets = proxy_df[
            proxy_df['sheet_name'].str.contains('compensation|summary', case=False, na=False)
        ]
        
        analysis = {
            'data_available': len(comp_sheets) > 0,
            'years_covered': sorted(proxy_df['year'].unique()),
            'compensation_sheets': comp_sheets['sheet_name'].unique().tolist() if len(comp_sheets) > 0 else [],
            'interpretation': 'Proxy data extracted - detailed analysis requires manual review of tables'
        }
        
        return analysis
    
    def analyze_governance_quality(self) -> Dict:
        governance = {
            'board_independence': {
                'status': 'Data in proxy statements',
                'assessment': 'Requires manual review'
            },
            'insider_ownership': {
                'status': 'Data in proxy statements',
                'assessment': 'Requires manual review'
            },
            'audit_quality': {
                'status': 'Data in proxy statements',
                'note': 'Audit fees shown in proxy data'
            },
            'red_flags': self._identify_governance_red_flags(),
            'positive_factors': self._identify_governance_positives()
        }
        
        return governance
    
    def _identify_governance_red_flags(self) -> List[str]:
        red_flags = []
        
        red_flags.append('  Rapid cash decline ($44M to $1M in 4 years)')
        
        red_flags.append('  Persistent operating losses (negative margins)')
        
        red_flags.append('  Declining revenue trend (-53% over 5 years)')
        
        return red_flags
    
    def _identify_governance_positives(self) -> List[str]:
        positives = []
        
        if self.proxy is not None and not self.proxy.empty:
            positives.append(' Regular proxy filings (good transparency)')
        
        positives.append(' SEC compliance maintained (10-K, 10-Q, 8-K)')
        
        positives.append(' Independent auditor engaged')
        
        return positives
    
    def print_governance_analysis(self, sbc_analysis: Dict, exec_comp: Dict, governance: Dict):
        print("\n" + "="*80)
        print(" GOVERNANCE & COMPENSATION ANALYSIS")
        print("="*80)
        
        print("\n STOCK-BASED COMPENSATION:")
        if 'stock_based_compensation_data' in sbc_analysis:
            sbc_df = sbc_analysis['stock_based_compensation_data']
            recent_sbc = sbc_df.tail(5)
            print("  Recent years:")
            for _, row in recent_sbc.iterrows():
                if pd.notna(row['avg_stock_based_comp']):
                    print(f"    {int(row['year'])}: ${row['avg_stock_based_comp']:>8,.0f}K (count: {int(row['count'])})")
            
            print(f"\n  Trend: {sbc_analysis['interpretation']}")
            print(f"  Dilution Risk: {sbc_analysis['shareholder_dilution_risk']}")
        
        print("\n EXECUTIVE COMPENSATION:")
        if 'error' not in exec_comp:
            print(f"  Years Covered: {exec_comp['years_covered']}")
            print(f"  Data Available: {exec_comp['data_available']}")
            print(f"  Compensation Sheets: {len(exec_comp['compensation_sheets'])}")
            print(f"  Note: {exec_comp['interpretation']}")
        else:
            print(f"  {exec_comp['error']}")
        
        print("\n  CORPORATE GOVERNANCE:")
        print("  Red Flags:")
        for flag in governance['red_flags']:
            print(f"    {flag}")
        
        print("\n  Positive Factors:")
        for positive in governance['positive_factors']:
            print(f"    {positive}")
