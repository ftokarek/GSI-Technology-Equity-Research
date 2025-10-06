#!/usr/bin/env python3
"""
Extract market data (stock prices) from Excel files and save to CSV.
This script processes the ChartData_GSIT.xlsx file containing historical stock prices.
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from utils.excel_parser import ExcelParser
from utils.data_cleaner import DataCleaner


def extract_market_data(input_file: str, output_file: str) -> bool:
    """
    Extract stock market data from Excel file and save to CSV.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output CSV file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Processing: {input_file}")
        
        # Read the Excel file
        parser = ExcelParser(input_file)
        
        # Get all sheets (usually just one for market data)
        sheets = parser.get_sheet_names()
        print(f"  Found {len(sheets)} sheet(s): {sheets}")
        
        # Read the first sheet
        df = parser.read_sheet(sheets[0])
        print(f"  Original shape: {df.shape}")
        
        # Clean the data
        df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.5)
        
        # Standardize column names
        df.columns = [col.strip().lower().replace('/', '_').replace(' ', '_') 
                     for col in df.columns]
        
        # Rename 'close_price' column if needed
        if 'close_price' in df.columns:
            df.rename(columns={'close_price': 'close'}, inplace=True)
        
        # Convert date column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Sort by date
            df = df.sort_values('date')
        
        # Clean numeric columns
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing dates
        if 'date' in df.columns:
            df = df.dropna(subset=['date'])
        
        # Add metadata
        df.insert(0, 'ticker', 'GSIT')
        df.insert(1, 'company', 'GSI Technology Inc.')
        
        print(f"  Cleaned shape: {df.shape}")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Columns: {list(df.columns)}")
        
        # Save to CSV
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_file, index=False)
        
        print(f"  ✓ Saved to: {output_file}")
        parser.close()
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {input_file}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution function."""
    # Define paths
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / "data/raw/market data/ChartData_GSIT.xlsx"
    output_file = project_root / "data/processed/market_data/stock_prices.csv"
    
    print("=" * 80)
    print("GSI Technology - Market Data Extraction")
    print("=" * 80)
    print()
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return 1
    
    success = extract_market_data(str(input_file), str(output_file))
    
    print()
    print("=" * 80)
    if success:
        print("Market data extraction completed successfully!")
        print(f"Output saved to: {output_file}")
    else:
        print("Market data extraction failed!")
    print("=" * 80)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

