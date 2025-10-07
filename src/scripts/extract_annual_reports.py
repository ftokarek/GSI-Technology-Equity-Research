#!/usr/bin/env python3
"""
Extract financial data from 10-K reports (Annual Reports).
10-K reports contain comprehensive annual financial statements and detailed disclosures.
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.append(str(Path(__file__).parent))
from utils.excel_parser import ExcelParser
from utils.data_cleaner import DataCleaner


def extract_financial_table(df: pd.DataFrame, 
                            table_type: str,
                            sheet_name: str,
                            metadata: dict) -> pd.DataFrame:
    """
    Extract and structure a financial table from 10-K.
    
    Args:
        df: Raw DataFrame from Excel sheet
        table_type: Type of financial statement
        sheet_name: Name of the source sheet
        metadata: File metadata
        
    Returns:
        Cleaned and structured DataFrame
    """
    # Remove empty rows and columns
    df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.3)
    
    if df.empty or df.shape[0] < 2:
        return pd.DataFrame()
    
    # Find the header row (usually contains fiscal years)
    header_row = 0
    for idx, row in df.iterrows():
        row_str = ' '.join([str(val).lower() for val in row if pd.notna(val)])
        # Look for year patterns or "march 31" style dates
        if any(kw in row_str for kw in ['march', 'fiscal', 'year ended', '2020', '2021', 
                                         '2022', '2023', '2024', '2025']):
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
            if pd.isna(col) or col_str in ['', 'nan', 'None']:
                new_columns.append(f'year_{i}')
            else:
                # Extract year if present
                year_match = re.search(r'(20\d{2})', col_str)
                if year_match:
                    new_columns.append(f'fy_{year_match.group(1)}')
                else:
                    # Clean the period name
                    clean_name = re.sub(r'[^\w\s\-/]', '', col_str)
                    clean_name = re.sub(r'\s+', '_', clean_name)
                    new_columns.append(clean_name.lower()[:50])  # Limit length
    
    df.columns = new_columns
    
    # Remove rows where line_item is empty
    df = df[df['line_item'].notna()]
    df = df[df['line_item'].astype(str).str.strip() != '']
    
    # Clean numeric columns
    numeric_cols = [col for col in df.columns if col != 'line_item']
    df = DataCleaner.clean_financial_values(df, value_columns=numeric_cols)
    
    # Normalize line item names
    df = DataCleaner.normalize_item_names(df, item_column='line_item')
    
    df.insert(0, 'sheet_name', sheet_name)
    df.insert(0, 'statement_type', table_type)
    for key, value in reversed(list(metadata.items())):
        df.insert(0, key, value)
    
    return df


def extract_annual_report(excel_file: Path) -> dict:
    """
    Extract all financial statements from an annual report.
    
    Args:
        excel_file: Path to 10-K Excel file
        
    Returns:
        Dictionary with DataFrames for each statement type
    """
    parser = ExcelParser(str(excel_file))
    metadata = parser.extract_metadata_from_filename()
    metadata['source_file'] = excel_file.name
    
    # Categorize sheets
    categories = parser.find_financial_statement_sheets()
    
    results = {
        'balance_sheets': [],
        'income_statements': [],
        'cash_flows': [],
        'comprehensive_income': [],
        'equity_statements': [],
        'compensation': []
    }
    
    # Process balance sheets
    for sheet_name in categories['balance_sheet'][:3]:  # Limit to avoid duplicates
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'balance_sheet', sheet_name, metadata)
            if not df_clean.empty:
                results['balance_sheets'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing balance sheet '{sheet_name}': {e}")
    
    # Process income statements
    for sheet_name in categories['income_statement'][:3]:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'income_statement', sheet_name, metadata)
            if not df_clean.empty:
                results['income_statements'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing income statement '{sheet_name}': {e}")
    
    # Process cash flow statements
    for sheet_name in categories['cash_flow'][:3]:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'cash_flow', sheet_name, metadata)
            if not df_clean.empty:
                results['cash_flows'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing cash flow '{sheet_name}': {e}")
    
    # Process comprehensive income statements
    for sheet_name in categories['comprehensive_income'][:2]:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'comprehensive_income', sheet_name, metadata)
            if not df_clean.empty:
                results['comprehensive_income'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing comprehensive income '{sheet_name}': {e}")
    
    # Process equity statements
    for sheet_name in categories['equity'][:2]:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'equity', sheet_name, metadata)
            if not df_clean.empty:
                results['equity_statements'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing equity statement '{sheet_name}': {e}")
    
    # Process compensation data
    for sheet_name in categories['compensation']:
        try:
            df = parser.read_sheet(sheet_name)
            df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.3)
            if not df.empty and df.shape[0] > 2:
                df.insert(0, 'sheet_name', sheet_name)
                df.insert(0, 'statement_type', 'compensation')
                for key, value in reversed(list(metadata.items())):
                    df.insert(0, key, value)
                results['compensation'].append(df)
        except Exception as e:
            print(f"    Warning: Error processing compensation '{sheet_name}': {e}")
    
    parser.close()
    return results


def process_all_annual_reports(input_dir: Path, output_dir: Path) -> bool:
    """
    Process all 10-K files and save by statement type.
    
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
    all_compensation = []
    
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
                
                results = extract_annual_report(excel_file)
                
                # Aggregate results
                if results['balance_sheets']:
                    all_balance_sheets.extend(results['balance_sheets'])
                if results['income_statements']:
                    all_income_statements.extend(results['income_statements'])
                if results['cash_flows']:
                    all_cash_flows.extend(results['cash_flows'])
                if results['comprehensive_income']:
                    all_comprehensive_income.extend(results['comprehensive_income'])
                if results['equity_statements']:
                    all_equity_statements.extend(results['equity_statements'])
                if results['compensation']:
                    all_compensation.extend(results['compensation'])
                
                processed_files += 1
                print(f"    ✓ Extracted data")
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files_created = 0
    
    if all_balance_sheets:
        df = pd.concat(all_balance_sheets, ignore_index=True)
        output_file = output_dir / "balance_sheets.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✓ Balance sheets: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_income_statements:
        df = pd.concat(all_income_statements, ignore_index=True)
        output_file = output_dir / "income_statements.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Income statements: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_cash_flows:
        df = pd.concat(all_cash_flows, ignore_index=True)
        output_file = output_dir / "cash_flows.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Cash flows: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_comprehensive_income:
        df = pd.concat(all_comprehensive_income, ignore_index=True)
        output_file = output_dir / "comprehensive_income.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Comprehensive income: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_equity_statements:
        df = pd.concat(all_equity_statements, ignore_index=True)
        output_file = output_dir / "equity_statements.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Equity statements: {len(df)} rows -> {output_file}")
        files_created += 1
    
    if all_compensation:
        df = pd.concat(all_compensation, ignore_index=True)
        output_file = output_dir / "compensation_data.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Compensation data: {len(df)} rows -> {output_file}")
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
    print("GSI Technology - Annual Reports (10-K) Extraction")
    print("=" * 80)
    print()
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    success = process_all_annual_reports(input_dir, output_dir)
    
    print()
    print("=" * 80)
    if success:
        print("Annual reports extraction completed successfully!")
    else:
        print("Annual reports extraction failed!")
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

