
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from utils.excel_parser import ExcelParser
from utils.data_cleaner import DataCleaner

def extract_market_data(input_file: str, output_file: str) -> bool:
    try:
        print(f"Processing: {input_file}")
        
        parser = ExcelParser(input_file)
        
        sheets = parser.get_sheet_names()
        print(f"  Found {len(sheets)} sheet(s): {sheets}")
        
        df = parser.read_sheet(sheets[0])
        print(f"  Original shape: {df.shape}")
        
        df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.5)
        
        df.columns = [col.strip().lower().replace('/', '_').replace(' ', '_') 
                     for col in df.columns]
        
        if 'close_price' in df.columns:
            df.rename(columns={'close_price': 'close'}, inplace=True)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.sort_values('date')
        
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'date' in df.columns:
            df = df.dropna(subset=['date'])
        
        df.insert(0, 'ticker', 'GSIT')
        df.insert(1, 'company', 'GSI Technology Inc.')
        
        print(f"  Cleaned shape: {df.shape}")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Columns: {list(df.columns)}")
        
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

