
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataConsolidator:
    
    def __init__(self, processed_data_dir: str, output_dir: str):
        self.processed_dir = Path(processed_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.market_data = None
        self.annual_income = None
        self.annual_balance = None
        self.annual_cashflow = None
        self.quarterly_income = None
        self.quarterly_balance = None
        
    def load_all_data(self):
        print("=" * 80)
        print("LOADING PROCESSED DATA")
        print("=" * 80)
        print()
        
        market_file = self.processed_dir / "market_data/stock_prices.csv"
        if market_file.exists():
            self.market_data = pd.read_csv(market_file)
            self.market_data['date'] = pd.to_datetime(self.market_data['date'])
            print(f"✓ Market data loaded: {len(self.market_data)} rows")
        else:
            print(f"✗ Market data not found")
        
        print("\nLoading annual reports...")
        annual_dir = self.processed_dir / "annual_reports"
        
        income_file = annual_dir / "income_statements.csv"
        if income_file.exists():
            self.annual_income = pd.read_csv(income_file)
            print(f"  ✓ Annual income statements: {len(self.annual_income)} rows")
        
        balance_file = annual_dir / "balance_sheets.csv"
        if balance_file.exists():
            self.annual_balance = pd.read_csv(balance_file)
            print(f"  ✓ Annual balance sheets: {len(self.annual_balance)} rows")
        
        cashflow_file = annual_dir / "cash_flows.csv"
        if cashflow_file.exists():
            self.annual_cashflow = pd.read_csv(cashflow_file)
            print(f"  ✓ Annual cash flows: {len(self.annual_cashflow)} rows")
        
        print("\nLoading quarterly reports...")
        quarterly_dir = self.processed_dir / "quarterly_reports"
        
        q_income_file = quarterly_dir / "income_statements.csv"
        if q_income_file.exists():
            self.quarterly_income = pd.read_csv(q_income_file)
            print(f"  ✓ Quarterly income statements: {len(self.quarterly_income)} rows")
        
        q_balance_file = quarterly_dir / "balance_sheets.csv"
        if q_balance_file.exists():
            self.quarterly_balance = pd.read_csv(q_balance_file)
            print(f"  ✓ Quarterly balance sheets: {len(self.quarterly_balance)} rows")
        
        print()
        print("=" * 80)
        print("DATA LOADING COMPLETED")
        print("=" * 80)
        print()
    
    def analyze_data_structure(self):
        print("=" * 80)
        print("DATA STRUCTURE ANALYSIS")
        print("=" * 80)
        print()
        
        if self.annual_income is not None:
            print("Annual Income Statement - Columns:")
            print(f"  {list(self.annual_income.columns)}")
            print(f"\nUnique years: {sorted(self.annual_income['year'].unique())}")
            print(f"Unique line items: {self.annual_income['line_item'].nunique()}")
            print(f"\nSample line items:")
            print(self.annual_income['line_item'].value_counts().head(10))
            print()
        
        if self.annual_balance is not None:
            print("\nAnnual Balance Sheet - Columns:")
            print(f"  {list(self.annual_balance.columns)}")
            print(f"\nUnique years: {sorted(self.annual_balance['year'].unique())}")
            print(f"Unique line items: {self.annual_balance['line_item'].nunique()}")
            print()
        
        if self.annual_cashflow is not None:
            print("\nAnnual Cash Flow - Columns:")
            print(f"  {list(self.annual_cashflow.columns)}")
            print(f"\nUnique years: {sorted(self.annual_cashflow['year'].unique())}")
            print()
        
        if self.market_data is not None:
            print("\nMarket Data:")
            print(f"  Date range: {self.market_data['date'].min()} to {self.market_data['date'].max()}")
            print(f"  Trading days: {len(self.market_data)}")
            print()
        
        print("=" * 80)
        print()
    
    def extract_key_financial_items(self, df, item_mappings):
        extracted_data = []
        
        for year in sorted(df['year'].unique()):
            year_data = df[df['year'] == year]
            row_data = {'year': int(year)}
            
            for standard_name, possible_names in item_mappings.items():
                value = None
                all_values = []  # Will store (column_index, value, sheet_priority) tuples
                
                for name_pattern in possible_names:
                    matches = year_data[
                        year_data['line_item'].str.lower().str.contains(
                            name_pattern.lower(), 
                            na=False, 
                            regex=False
                        )
                    ]
                    
                    if not matches.empty:
                        for _, row in matches.iterrows():
                            col_list = list(matches.columns)
                            
                            quarterly_cols_with_data = 0
                            quarterly_col_names = ['june_30', 'september_30', 'december_31', 'march_31']
                            for col_name in quarterly_col_names:
                                if col_name in row.index and pd.notna(row[col_name]) and row[col_name] != '':
                                    quarterly_cols_with_data += 1
                            
                            has_quarterly = quarterly_cols_with_data >= 2  # If 2+ quarterly values present, it's quarterly data
                            
                            if has_quarterly:
                                continue  # Skip rows with actual quarterly data
                            
                            sheet_name = str(row.get('sheet_name', '')).lower()
                            
                            if 'financial statement' in sheet_name:
                                sheet_priority = 0
                            elif 'consolidated' in sheet_name and ('operation' in sheet_name or 'balance' in sheet_name):
                                sheet_priority = 1
                            elif 'operations' in sheet_name or 'income' in sheet_name:
                                sheet_priority = 2
                            elif 'balance' in sheet_name:
                                sheet_priority = 3
                            elif 'valuation' in sheet_name or 'contingent' in sheet_name:
                                sheet_priority = 4  # Better than consideration
                            elif 'consideration' in sheet_name:
                                sheet_priority = 8  # Often quarterly data
                            elif 'management' in sheet_name or 'selected financial' in sheet_name:
                                sheet_priority = 9  # Very low priority (likely percentages)
                            else:
                                sheet_priority = 5  # Default middle priority
                            
                            for col_idx, col in enumerate(col_list):
                                if col not in ['year', 'line_item', 'filename', 'company', 
                                             'form_type', 'filing_date', 'source_file', 
                                             'statement_type', 'sheet_name']:
                                    val = row[col]
                                    if pd.notna(val) and val != '':
                                        try:
                                            num_val = float(val)
                                            if abs(num_val) > 0.01:  # Ignore very small values
                                                all_values.append((sheet_priority, col_idx, abs(num_val)))
                                        except (ValueError, TypeError):
                                            continue
                        
                        if all_values:
                            break
                
                if all_values:
                    all_values.sort(key=lambda x: (x[0], x[1]))
                    
                    large_values = [(priority, idx, v) for priority, idx, v in all_values if v > 100]
                    
                    if large_values:
                        value = large_values[0][2]
                    else:
                        value = all_values[0][2]
                
                row_data[standard_name] = value
            
            extracted_data.append(row_data)
        
        return pd.DataFrame(extracted_data)
    
    def create_master_income_statement(self):
        print("Creating master income statement...")
        
        if self.annual_income is None:
            print("  ✗ No annual income data available")
            return None
        
        item_mappings = {
            'revenue': ['net revenue', 'total revenue', 'revenue'],
            'cost_of_revenue': ['cost of goods sold', 'cost of revenue', 'cogs'],
            'gross_profit': ['gross profit'],
            'research_development': ['research', 'r&d', 'research and development'],
            'selling_general_admin': ['selling, general', 'sg&a', 'sga'],
            'operating_expenses': ['total operating expense', 'operating expense'],
            'operating_income': ['operating income', 'operating profit'],
            'operating_loss': ['operating loss'],
            'interest_expense': ['interest expense'],
            'other_income': ['other income', 'interest and other income'],
            'income_before_tax': ['income before tax', 'pretax income'],
            'tax_expense': ['income tax', 'tax expense', 'provision for income'],
            'net_income': ['net income'],
            'net_loss': ['net loss'],
            'eps_basic': ['basic', 'per share, basic'],
            'eps_diluted': ['diluted', 'per share, diluted'],
        }
        
        master_income = self.extract_key_financial_items(
            self.annual_income, 
            item_mappings
        )
        
        if 'net_income' in master_income.columns and 'net_loss' in master_income.columns:
            master_income['net_income_final'] = master_income.apply(
                lambda row: row['net_income'] if pd.notna(row['net_income']) 
                else -row['net_loss'] if pd.notna(row['net_loss']) else None,
                axis=1
            )
        
        output_file = self.output_dir / "master_income_statement.csv"
        master_income.to_csv(output_file, index=False)
        print(f"  ✓ Master income statement saved: {len(master_income)} years")
        print(f"    Years covered: {master_income['year'].min()} - {master_income['year'].max()}")
        
        return master_income
    
    def create_master_balance_sheet(self):
        print("\nCreating master balance sheet...")
        
        if self.annual_balance is None:
            print("  ✗ No annual balance sheet data available")
            return None
        
        item_mappings = {
            'cash_and_equivalents': ['cash and cash equivalents', 'cash'],
            'short_term_investments': ['short-term investment', 'short term investment'],
            'accounts_receivable': ['accounts receivable', 'receivable'],
            'inventories': ['inventories', 'inventory'],
            'current_assets': ['total current assets', 'current assets'],
            'property_equipment': ['property and equipment', 'property, plant'],
            'total_assets': ['total assets'],
            'accounts_payable': ['accounts payable', 'payable'],
            'accrued_expenses': ['accrued expense'],
            'short_term_debt': ['short-term debt', 'current portion'],
            'current_liabilities': ['total current liabilities', 'current liabilities'],
            'long_term_debt': ['long-term debt', 'long term debt'],
            'total_liabilities': ['total liabilities'],
            'stockholders_equity': ['stockholders equity', 'shareholders equity', 
                                   'stockholders\' equity', 'total equity'],
            'common_stock': ['common stock'],
            'retained_earnings': ['retained earnings'],
        }
        
        master_balance = self.extract_key_financial_items(
            self.annual_balance,
            item_mappings
        )
        
        output_file = self.output_dir / "master_balance_sheet.csv"
        master_balance.to_csv(output_file, index=False)
        print(f"  ✓ Master balance sheet saved: {len(master_balance)} years")
        print(f"    Years covered: {master_balance['year'].min()} - {master_balance['year'].max()}")
        
        return master_balance
    
    def create_master_cashflow(self):
        print("\nCreating master cash flow statement...")
        
        if self.annual_cashflow is None:
            print("  ✗ No annual cash flow data available")
            return None
        
        item_mappings = {
            'net_income': ['net income', 'net loss'],
            'depreciation_amortization': ['depreciation', 'amortization'],
            'stock_based_compensation': ['stock-based compensation', 'stock based'],
            'changes_working_capital': ['working capital'],
            'operating_cash_flow': ['operating activities', 'cash from operations', 
                                   'net cash provided by operating'],
            'capital_expenditures': ['capital expenditure', 'capex', 
                                    'property and equipment'],
            'investing_cash_flow': ['investing activities', 'cash from investing',
                                   'net cash used in investing'],
            'financing_cash_flow': ['financing activities', 'cash from financing',
                                   'net cash provided by financing'],
            'net_change_cash': ['net increase', 'net change in cash'],
        }
        
        master_cashflow = self.extract_key_financial_items(
            self.annual_cashflow,
            item_mappings
        )
        
        output_file = self.output_dir / "master_cashflow.csv"
        master_cashflow.to_csv(output_file, index=False)
        print(f"  ✓ Master cash flow saved: {len(master_cashflow)} years")
        print(f"    Years covered: {master_cashflow['year'].min()} - {master_cashflow['year'].max()}")
        
        return master_cashflow
    
    def create_market_summary(self):
        print("\nCreating market data summary...")
        
        if self.market_data is None:
            print("  ✗ No market data available")
            return None
        
        df = self.market_data.copy()
        df['year'] = df['date'].dt.year
        
        annual_summary = df.groupby('year').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).reset_index()
        
        annual_summary['annual_return'] = annual_summary['close'].pct_change() * 100
        
        output_file = self.output_dir / "market_data_annual.csv"
        annual_summary.to_csv(output_file, index=False)
        print(f"  ✓ Market data summary saved: {len(annual_summary)} years")
        
        return annual_summary
    
    def consolidate_all(self):
        print("\n")
        print("=" * 80)
        print("STARTING DATA CONSOLIDATION")
        print("=" * 80)
        print("\n")
        
        self.load_all_data()
        
        self.analyze_data_structure()
        
        print("=" * 80)
        print("CREATING CONSOLIDATED DATASETS")
        print("=" * 80)
        print()
        
        income = self.create_master_income_statement()
        balance = self.create_master_balance_sheet()
        cashflow = self.create_master_cashflow()
        market = self.create_market_summary()
        
        print()
        print("=" * 80)
        print("CONSOLIDATION COMPLETED")
        print("=" * 80)
        print()
        print(f"Output directory: {self.output_dir}")
        print("\nCreated files:")
        for file in self.output_dir.glob("*.csv"):
            size_kb = file.stat().st_size / 1024
            print(f"  - {file.name} ({size_kb:.1f} KB)")
        print()
        
        return {
            'income': income,
            'balance': balance,
            'cashflow': cashflow,
            'market': market
        }

def main():
    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / "data/processed"
    output_dir = project_root / "data/consolidated"
    
    consolidator = DataConsolidator(str(processed_dir), str(output_dir))
    results = consolidator.consolidate_all()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

