#!/usr/bin/env python3
"""
Extract financial data from 10-Q reports (Quarterly Reports).
10-Q reports contain detailed quarterly financial statements.
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from utils.excel_parser import ExcelParser
from utils.data_cleaner import DataCleaner


def extract_financial_table(df: pd.DataFrame, 
                            table_type: str,
                            metadata: dict) -> pd.DataFrame:
    """
    Extract and structure a financial table.
    
    Args:
        df: Raw DataFrame from Excel sheet
        table_type: Type of financial statement
        metadata: File metadata
        
    Returns:
        Cleaned and structured DataFrame
    """
    # Remove empty rows and columns
    df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.3)
    
    if df.empty or df.shape[0] < 2:
        return pd.DataFrame()
    
    # Find the header row (usually contains periods/dates)
    header_row = 0
    for idx, row in df.iterrows():
        row_str = ' '.join([str(val).lower() for val in row if pd.notna(val)])
        if any(kw in row_str for kw in ['march', 'june', 'september', 'december', 
                                         'quarter', '2020', '2021', '2022', '2023', '2024', '2025']):
            header_row = idx
            break
    
    # Set header and clean
    if header_row > 0:
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    # Ensure first column contains line items
    if df.empty:
        return pd.DataFrame()
    
    # Clean column names
    new_columns = []
    for i, col in enumerate(df.columns):
        if i == 0:
            new_columns.append('line_item')
        else:
            # Try to extract period information
            col_str = str(col).strip()
            if pd.isna(col) or col_str in ['', 'nan', 'None']:
                new_columns.append(f'period_{i}')
            else:
                # Clean the period name
                clean_name = re.sub(r'[^\w\s\-/]', '', col_str)
                clean_name = re.sub(r'\s+', '_', clean_name)
                new_columns.append(clean_name.lower())
    
    df.columns = new_columns
    
    # Remove rows where line_item is empty
    df = df[df['line_item'].notna()]
    df = df[df['line_item'].astype(str).str.strip() != '']
    
    # Clean numeric columns (all except first)
    numeric_cols = [col for col in df.columns if col != 'line_item']
    df = DataCleaner.clean_financial_values(df, value_columns=numeric_cols)
    
    # Add metadata and type
    df.insert(0, 'statement_type', table_type)
    for key, value in reversed(list(metadata.items())):
        df.insert(0, key, value)
    
    return df


def extract_quarterly_report(excel_file: Path) -> dict:
    """
    Extract all financial statements from a quarterly report.
    
    Args:
        excel_file: Path to 10-Q Excel file
        
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
        'equity_statements': []
    }
    
    # Process balance sheets
    for sheet_name in categories['balance_sheet']:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'balance_sheet', metadata)
            if not df_clean.empty:
                results['balance_sheets'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing balance sheet '{sheet_name}': {e}")
    
    # Process income statements
    for sheet_name in categories['income_statement']:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'income_statement', metadata)
            if not df_clean.empty:
                results['income_statements'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing income statement '{sheet_name}': {e}")
    
    # Process cash flow statements
    for sheet_name in categories['cash_flow']:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'cash_flow', metadata)
            if not df_clean.empty:
                results['cash_flows'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing cash flow '{sheet_name}': {e}")
    
    # Process equity statements
    for sheet_name in categories['equity']:
        try:
            df = parser.read_sheet(sheet_name)
            df_clean = extract_financial_table(df, 'equity', metadata)
            if not df_clean.empty:
                results['equity_statements'].append(df_clean)
        except Exception as e:
            print(f"    Warning: Error processing equity statement '{sheet_name}': {e}")
    
    parser.close()
    return results


def process_all_quarterly_reports(input_dir: Path, output_dir: Path) -> bool:
    """
    Process all 10-Q files and save by statement type.
    
    Args:
        input_dir: Directory containing 10-Q subdirectories by year
        output_dir: Output directory for CSV files
        
    Returns:
        True if successful, False otherwise
    """
    # Aggregated data by statement type
    all_balance_sheets = []
    all_income_statements = []
    all_cash_flows = []
    all_equity_statements = []
    
    total_files = 0
    processed_files = 0
    
    # Get all year directories
    year_dirs = sorted([d for d in input_dir.iterdir() if d.is_dir()],
                      key=lambda x: x.name)
    
    print(f"Found {len(year_dirs)} year directories")
    
    for year_dir in year_dirs:
        year = year_dir.name
        print(f"\nProcessing year: {year}")
        
        excel_files = sorted(list(year_dir.glob("*.xlsx")))
        total_files += len(excel_files)
        
        for excel_file in excel_files:
            try:
                print(f"  Processing: {excel_file.name}")
                
                results = extract_quarterly_report(excel_file)
                
                # Aggregate results
                if results['balance_sheets']:
                    all_balance_sheets.extend(results['balance_sheets'])
                if results['income_statements']:
                    all_income_statements.extend(results['income_statements'])
                if results['cash_flows']:
                    all_cash_flows.extend(results['cash_flows'])
                if results['equity_statements']:
                    all_equity_statements.extend(results['equity_statements'])
                
                processed_files += 1
                print(f"    ✓ Extracted data")
                
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                continue
    
    # Save aggregated data
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
    
    if all_equity_statements:
        df = pd.concat(all_equity_statements, ignore_index=True)
        output_file = output_dir / "equity_statements.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Equity statements: {len(df)} rows -> {output_file}")
        files_created += 1
    
    print(f"\n✓ Successfully processed {processed_files}/{total_files} files")
    print(f"✓ Created {files_created} output files")
    
    return files_created > 0


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / "data/raw/quarterly reports"
    output_dir = project_root / "data/processed/quarterly_reports"
    
    print("=" * 80)
    print("GSI Technology - Quarterly Reports (10-Q) Extraction")
    print("=" * 80)
    print()
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    success = process_all_quarterly_reports(input_dir, output_dir)
    
    print()
    print("=" * 80)
    if success:
        print("Quarterly reports extraction completed successfully!")
    else:
        print("Quarterly reports extraction failed!")
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

