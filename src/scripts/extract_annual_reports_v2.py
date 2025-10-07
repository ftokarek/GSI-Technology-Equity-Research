#!/usr/bin/env python3
"""
IMPROVED Extract financial data from 10-K reports (Annual Reports).
This version detects financial statement types by CONTENT not just sheet names.
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.append(str(Path(__file__).parent))
from utils.excel_parser import ExcelParser
from utils.data_cleaner import DataCleaner


def detect_statement_type_by_content(df: pd.DataFrame, sheet_name: str) -> str:
    """
    Detect financial statement type by analyzing content.
    
    Args:
        df: DataFrame with sheet data
        sheet_name: Name of the sheet
        
    Returns:
        Statement type: 'balance_sheet', 'income_statement', 'cash_flow', 
                       'equity', 'comprehensive_income', or 'unknown'
    """
    if df.empty or df.shape[0] < 3:
        return 'unknown'
    
    first_col = df.iloc[:, 0].astype(str).str.lower()
    all_text = ' '.join(first_col.tolist())
    
    # Count keywords for each statement type
    scores = {
        'balance_sheet': 0,
        'income_statement': 0,
        'cash_flow': 0,
        'equity': 0,
        'comprehensive_income': 0
    }
    
    # Balance sheet keywords
    bs_keywords = ['assets', 'liabilities', 'cash and cash equivalents', 
                   'accounts receivable', 'inventories', 'stockholders equity',
                   'property and equipment', 'current assets']
    scores['balance_sheet'] = sum(1 for kw in bs_keywords if kw in all_text)
    
    # Income statement keywords
    is_keywords = ['net revenues', 'revenue', 'cost of revenues', 'gross profit',
                   'operating expenses', 'research and development',
                   'selling, general and administrative', 'net income', 'net loss',
                   'loss from operations', 'income from operations']
    scores['income_statement'] = sum(1 for kw in is_keywords if kw in all_text)
    
    # Cash flow keywords
    cf_keywords = ['cash flows', 'operating activities', 'investing activities',
                   'financing activities', 'net increase', 'net decrease',
                   'depreciation', 'capital expenditures']
    scores['cash_flow'] = sum(1 for kw in cf_keywords if kw in all_text)
    
    # Equity keywords
    eq_keywords = ['common stock', 'additional paid-in capital', 'retained earnings',
                   'accumulated other comprehensive', 'treasury stock',
                   'stock-based compensation expense', 'issuance of common stock']
    scores['equity'] = sum(1 for kw in eq_keywords if kw in all_text)
    
    # Comprehensive income keywords
    ci_keywords = ['comprehensive income', 'comprehensive loss', 
                   'unrealized gain', 'unrealized loss']
    scores['comprehensive_income'] = sum(1 for kw in ci_keywords if kw in all_text)
    
    # Return type with highest score (if score > 2)
    max_type = max(scores, key=scores.get)
    if scores[max_type] >= 2:
        return max_type
    
    return 'unknown'


def extract_financial_table_v2(df: pd.DataFrame, 
                               table_type: str,
                               sheet_name: str,
                               metadata: dict,
                               year: int) -> pd.DataFrame:
    """
    Extract and structure a financial table from 10-K.
    
    Args:
        df: Raw DataFrame from Excel sheet
        table_type: Type of financial statement
        sheet_name: Name of the source sheet
        metadata: File metadata
        year: Filing year
        
    Returns:
        Cleaned and structured DataFrame
    """
    # Remove empty rows and columns
    df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.3)
    
    if df.empty or df.shape[0] < 2:
        return pd.DataFrame()
    
    # Find header row (contains year WITH context, not just standalone year)
    header_row = 0
    for idx, row in df.iterrows():
        row_str = ' '.join([str(val).lower() for val in row if pd.notna(val)])
        # Look for year patterns WITH context (not just "2020" alone)
        # Must have "march" or "year ended" or multiple years
        has_context = any(pattern in row_str for pattern in ['march', 'year ended', 'fiscal'])
        has_multiple_years = sum(1 for y in ['2020', '2021', '2022', '2023', '2024', '2025'] 
                                if y in row_str) >= 2
        
        if has_context or has_multiple_years:
            header_row = idx
            break
    
    if header_row > 0:
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    if df.empty:
        return pd.DataFrame()
    
    # Clean column names
    new_columns = []
    for i, col in enumerate(df.columns):
        if i == 0:
            new_columns.append('line_item')
        else:
            col_str = str(col).strip()
            # Try to extract year
            year_match = re.search(r'(20\d{2})', col_str)
            if year_match:
                new_columns.append(f'fy_{year_match.group(1)}')
            elif pd.isna(col) or col_str in ['', 'nan', 'None', '​']:
                new_columns.append(f'col_{i}')
            else:
                # Clean the column name
                clean_name = re.sub(r'[^\w\s]', '', col_str)
                clean_name = re.sub(r'\s+', '_', clean_name).lower()[:30]
                new_columns.append(clean_name if clean_name else f'col_{i}')
    
    df.columns = new_columns
    
    # Remove rows where line_item is empty or just punctuation
    df = df[df['line_item'].notna()]
    df['line_item'] = df['line_item'].astype(str).str.strip()
    df = df[df['line_item'] != '']
    df = df[~df['line_item'].str.match(r'^[^\w]+$')]  # Remove rows with only punctuation
    
    # Clean numeric columns
    numeric_cols = [col for col in df.columns if col != 'line_item']
    df = DataCleaner.clean_financial_values(df, value_columns=numeric_cols)
    
    df.insert(0, 'sheet_name', sheet_name)
    df.insert(0, 'statement_type', table_type)
    
    if 'year' not in df.columns:
        df.insert(0, 'year', year)
    
    for key, value in reversed(list(metadata.items())):
        if key not in df.columns:  # Don't insert if column already exists
            df.insert(0, key, value)
    
    return df


def extract_annual_report_v2(excel_file: Path) -> dict:
    """
    Extract all financial statements from an annual report using content detection.
    
    Args:
        excel_file: Path to 10-K Excel file
        
    Returns:
        Dictionary with DataFrames for each statement type
    """
    parser = ExcelParser(str(excel_file))
    metadata = parser.extract_metadata_from_filename()
    metadata['source_file'] = excel_file.name
    
    # Determine year from filename or metadata
    year = int(metadata['year']) if metadata['year'] else 2020
    
    results = {
        'balance_sheets': [],
        'income_statements': [],
        'cash_flows': [],
        'comprehensive_income': [],
        'equity_statements': []
    }
    
    # Process ALL sheets and detect type by content
    for sheet_name in parser.get_sheet_names():
        try:
            # Skip obviously irrelevant sheets
            skip_keywords = ['exhibit', 'No Title', 'note', 'Note', 'accounting pronouncements',
                           'fair value measurement', 'stock pu', 'compensation']
            if any(kw in sheet_name for kw in skip_keywords):
                continue
            
            # Read sheet
            df = parser.read_sheet(sheet_name)
            
            if df.shape[0] < 3 or df.shape[1] < 2:
                continue
            
            # Detect statement type by content
            stmt_type = detect_statement_type_by_content(df, sheet_name)
            
            if stmt_type == 'unknown':
                continue
            
            # Extract the data
            df_clean = extract_financial_table_v2(df, stmt_type, sheet_name, metadata, year)
            
            if df_clean.empty:
                continue
            
            if stmt_type == 'balance_sheet':
                results['balance_sheets'].append(df_clean)
            elif stmt_type == 'income_statement':
                results['income_statements'].append(df_clean)
            elif stmt_type == 'cash_flow':
                results['cash_flows'].append(df_clean)
            elif stmt_type == 'comprehensive_income':
                results['comprehensive_income'].append(df_clean)
            elif stmt_type == 'equity':
                results['equity_statements'].append(df_clean)
                
        except Exception as e:
            print(f"    Warning: Error processing sheet '{sheet_name}': {e}")
            continue
    
    parser.close()
    return results


def process_all_annual_reports_v2(input_dir: Path, output_dir: Path) -> bool:
    """
    Process all 10-K files with improved content detection.
    
    Args:
        input_dir: Directory containing 10-K subdirectories by year
        output_dir: Output directory for CSV files
        
    Returns:
        True if successful, False otherwise
    """
    # Aggregated data by statement type
    all_balance_sheets = []
    all_income_statements = []
    all_cash_flows = []
    all_comprehensive_income = []
    all_equity_statements = []
    
    total_files = 0
    processed_files = 0
    
    year_dirs = sorted([d for d in input_dir.iterdir() if d.is_dir()],
                      key=lambda x: x.name)
    
    print(f"Found {len(year_dirs)} year directories")
    
    for year_dir in year_dirs:
        year = year_dir.name
        print(f"\nProcessing year: {year}")
        
        excel_files = [f for f in sorted(list(year_dir.glob("*.xlsx"))) 
                      if '10-K' in f.name or 'Annual report pursuant' in f.name]
        total_files += len(excel_files)
        
        for excel_file in excel_files:
            try:
                print(f"  Processing: {excel_file.name}")
                
                results = extract_annual_report_v2(excel_file)
                
                # Aggregate results
                if results['balance_sheets']:
                    all_balance_sheets.extend(results['balance_sheets'])
                    print(f"    ✓ Balance sheet: {len(results['balance_sheets'])} sheet(s)")
                if results['income_statements']:
                    all_income_statements.extend(results['income_statements'])
                    print(f"    ✓ Income statement: {len(results['income_statements'])} sheet(s)")
                if results['cash_flows']:
                    all_cash_flows.extend(results['cash_flows'])
                    print(f"    ✓ Cash flow: {len(results['cash_flows'])} sheet(s)")
                if results['comprehensive_income']:
                    all_comprehensive_income.extend(results['comprehensive_income'])
                    print(f"    ✓ Comprehensive income: {len(results['comprehensive_income'])} sheet(s)")
                if results['equity_statements']:
                    all_equity_statements.extend(results['equity_statements'])
                    print(f"    ✓ Equity: {len(results['equity_statements'])} sheet(s)")
                
                processed_files += 1
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files_created = 0
    
    if all_balance_sheets:
        df = pd.concat(all_balance_sheets, ignore_index=True)
        output_file = output_dir / "balance_sheets_v2.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✓ Balance sheets: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_income_statements:
        df = pd.concat(all_income_statements, ignore_index=True)
        output_file = output_dir / "income_statements_v2.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Income statements: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_cash_flows:
        df = pd.concat(all_cash_flows, ignore_index=True)
        output_file = output_dir / "cash_flows_v2.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Cash flows: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_comprehensive_income:
        df = pd.concat(all_comprehensive_income, ignore_index=True)
        output_file = output_dir / "comprehensive_income_v2.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Comprehensive income: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_equity_statements:
        df = pd.concat(all_equity_statements, ignore_index=True)
        output_file = output_dir / "equity_statements_v2.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Equity statements: {len(df)} rows -> {output_file}")
        files_created += 1
    
    print(f"\n✓ Successfully processed {processed_files}/{total_files} files")
    print(f"✓ Created {files_created} output files")
    
    return files_created > 0


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / "data/raw/annual reports"
    output_dir = project_root / "data/processed/annual_reports"
    
    print("=" * 80)
    print("GSI Technology - IMPROVED Annual Reports (10-K) Extraction")
    print("Using content-based detection instead of sheet names")
    print("=" * 80)
    print()
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    success = process_all_annual_reports_v2(input_dir, output_dir)
    
    print()
    print("=" * 80)
    if success:
        print("Annual reports extraction completed successfully!")
    else:
        print("Annual reports extraction failed!")
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

