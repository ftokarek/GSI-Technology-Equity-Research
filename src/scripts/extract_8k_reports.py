#!/usr/bin/env python3
"""
Extract financial data from 8-K reports (Current Reports).
8-K reports contain material events and earnings releases with key financial highlights.
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.append(str(Path(__file__).parent))
from utils.excel_parser import ExcelParser
from utils.data_cleaner import DataCleaner


def extract_8k_data(excel_file: Path, metadata: dict) -> pd.DataFrame:
    """
    Extract financial data from a single 8-K Excel file.
    
    Args:
        excel_file: Path to Excel file
        metadata: Metadata about the file
        
    Returns:
        DataFrame with extracted data
    """
    parser = ExcelParser(str(excel_file))
    
    # Categorize sheets
    categories = parser.find_financial_statement_sheets()
    
    all_data = []
    
    # Focus on income statement and balance sheet data
    relevant_sheets = (categories['income_statement'] + 
                      categories['balance_sheet'] + 
                      categories['cash_flow'])
    
    if not relevant_sheets:
        # If no categorized sheets, try all sheets
        relevant_sheets = parser.get_sheet_names()
    
    for sheet_name in relevant_sheets:
        try:
            df = parser.read_sheet(sheet_name)
            
            # Skip very small sheets
            if df.shape[0] < 3 or df.shape[1] < 2:
                continue
            
            # Find table boundaries
            start_row, end_row = parser.detect_table_boundaries(df)
            df = df.iloc[start_row:end_row]
            
            # Clean the dataframe
            df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.3)
            
            if df.empty:
                continue
            
            # Try to identify if this is a financial table
            first_col = df.iloc[:, 0].astype(str).str.lower()
            
            # Look for financial statement keywords
            financial_keywords = ['revenue', 'income', 'expense', 'assets', 
                                'liabilities', 'equity', 'cash', 'profit', 'loss']
            
            has_financial_data = any(
                any(keyword in str(cell).lower() for keyword in financial_keywords)
                for cell in first_col
            )
            
            if not has_financial_data:
                continue
            
            # Extract the data
            # Assume first column is the line item name
            df = df.reset_index(drop=True)
            
            # Clean column names
            df.columns = [f"col_{i}" if i == 0 else f"period_{i-1}" 
                         for i in range(len(df.columns))]
            
            # Rename first column to 'line_item'
            df.rename(columns={'col_0': 'line_item'}, inplace=True)
            
            df['sheet_name'] = sheet_name
            df['sheet_type'] = _categorize_sheet(sheet_name)
            
            all_data.append(df)
            
        except Exception as e:
            print(f"    Warning: Could not process sheet '{sheet_name}': {str(e)}")
            continue
    
    parser.close()
    
    if not all_data:
        return pd.DataFrame()
    
    # Combine all extracted data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    for key, value in metadata.items():
        combined_df.insert(0, key, value)
    
    return combined_df


def _categorize_sheet(sheet_name: str) -> str:
    """Categorize sheet by type based on name."""
    name_lower = sheet_name.lower()
    
    if any(kw in name_lower for kw in ['income', 'operation', 'profit', 'loss']):
        return 'income_statement'
    elif any(kw in name_lower for kw in ['balance', 'assets', 'liabilities']):
        return 'balance_sheet'
    elif any(kw in name_lower for kw in ['cash flow', 'cash']):
        return 'cash_flow'
    else:
        return 'other'


def process_all_8k_files(input_dir: Path, output_file: Path) -> bool:
    """
    Process all 8-K files and combine into single CSV.
    
    Args:
        input_dir: Directory containing 8-K subdirectories by year
        output_file: Output CSV file path
        
    Returns:
        True if successful, False otherwise
    """
    all_data = []
    total_files = 0
    processed_files = 0
    
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
                
                # Parse metadata from filename
                parser = ExcelParser(str(excel_file))
                metadata = parser.extract_metadata_from_filename()
                metadata['source_file'] = excel_file.name
                metadata['year_folder'] = year
                
                # Extract data
                df = extract_8k_data(excel_file, metadata)
                
                if not df.empty:
                    all_data.append(df)
                    processed_files += 1
                    print(f"    ✓ Extracted {len(df)} rows")
                else:
                    print(f"     No data extracted")
                    
            except Exception as e:
                print(f"    ✗ Error: {str(e)}")
                continue
    
    if not all_data:
        print("\n✗ No data extracted from any files!")
        return False
    
    # Combine all data
    print(f"\nCombining data from {len(all_data)} files...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Successfully processed {processed_files}/{total_files} files")
    print(f"✓ Total rows extracted: {len(combined_df)}")
    print(f"✓ Saved to: {output_file}")
    
    return True


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / "data/raw/8-k related"
    output_file = project_root / "data/processed/8k_reports/financial_highlights.csv"
    
    print("=" * 80)
    print("GSI Technology - 8-K Reports Extraction")
    print("=" * 80)
    print()
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    success = process_all_8k_files(input_dir, output_file)
    
    print()
    print("=" * 80)
    if success:
        print("8-K extraction completed successfully!")
    else:
        print("8-K extraction failed!")
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

