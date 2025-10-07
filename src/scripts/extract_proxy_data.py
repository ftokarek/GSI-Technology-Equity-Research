
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from utils.excel_parser import ExcelParser
from utils.data_cleaner import DataCleaner

def extract_proxy_data(excel_file: Path) -> pd.DataFrame:
    parser = ExcelParser(str(excel_file))
    metadata = parser.extract_metadata_from_filename()
    metadata['source_file'] = excel_file.name
    
    all_data = []
    
    sheets = parser.get_sheet_names()
    
    for sheet_name in sheets:
        try:
            df = parser.read_sheet(sheet_name)
            
            if df.shape[0] < 2 or df.shape[1] < 2:
                continue
            
            df = DataCleaner.remove_empty_rows_and_columns(df, threshold=0.3)
            
            if df.empty:
                continue
            
            df.insert(0, 'sheet_name', sheet_name)
            for key, value in reversed(list(metadata.items())):
                df.insert(0, key, value)
            
            all_data.append(df)
            
        except Exception as e:
            print(f"    Warning: Could not process sheet '{sheet_name}': {str(e)}")
            continue
    
    parser.close()
    
    if not all_data:
        return pd.DataFrame()
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    return combined_df

def process_all_proxy_statements(input_dir: Path, output_file: Path) -> bool:
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
                
                df = extract_proxy_data(excel_file)
                
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
    
    print(f"\nCombining data from {len(all_data)} files...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Successfully processed {processed_files}/{total_files} files")
    print(f"✓ Total rows extracted: {len(combined_df)}")
    print(f"✓ Saved to: {output_file}")
    
    return True

def main():
    project_root = Path(__file__).parent.parent.parent
    input_dir = project_root / "data/raw/proxies and info statements"
    output_file = project_root / "data/processed/proxy_statements/proxy_data.csv"
    
    print("=" * 80)
    print("GSI Technology - Proxy Statements Extraction")
    print("=" * 80)
    print()
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    success = process_all_proxy_statements(input_dir, output_file)
    
    print()
    print("=" * 80)
    if success:
        print("Proxy statements extraction completed successfully!")
    else:
        print("Proxy statements extraction failed!")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

