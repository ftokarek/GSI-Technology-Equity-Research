#!/usr/bin/env python3
"""
Master script to run all data extraction scripts.
Extracts all financial data from GSI Technology SEC filings and market data.
"""

import sys
from pathlib import Path
from datetime import datetime
import subprocess


def run_script(script_name: str, description: str) -> bool:
    """
    Run a single extraction script.
    
    Args:
        script_name: Name of the script to run
        description: Description of what the script does
        
    Returns:
        True if successful, False otherwise
    """
    print()
    print("=" * 80)
    print(f"Running: {description}")
    print("=" * 80)
    print()
    
    script_path = Path(__file__).parent / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✓ {description} completed successfully!")
            return True
        else:
            print(f"\n✗ {description} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error running {script_name}: {str(e)}")
        return False


def main():
    """Main execution function."""
    print("=" * 80)
    print("GSI TECHNOLOGY - COMPREHENSIVE DATA EXTRACTION")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Define extraction scripts in order of execution
    scripts = [
        ("extract_market_data.py", "Market Data (Stock Prices)"),
        ("extract_8k_reports.py", "8-K Reports (Current Reports)"),
        ("extract_quarterly_reports.py", "Quarterly Reports (10-Q)"),
        ("extract_annual_reports.py", "Annual Reports (10-K)"),
        ("extract_proxy_data.py", "Proxy Statements (DEF 14A)"),
    ]
    
    results = {}
    
    for script_name, description in scripts:
        success = run_script(script_name, description)
        results[description] = success
    
    # Print summary
    print()
    print()
    print("=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print()
    
    total_scripts = len(results)
    successful_scripts = sum(1 for success in results.values() if success)
    
    for description, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status:12} - {description}")
    
    print()
    print("-" * 80)
    print(f"Total: {successful_scripts}/{total_scripts} scripts completed successfully")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Print output directory info
    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / "data/processed"
    
    if processed_dir.exists():
        print()
        print("Processed data available in:")
        print(f"  {processed_dir}")
        print()
        print("Output structure:")
        for item in sorted(processed_dir.iterdir()):
            if item.is_dir():
                csv_files = list(item.glob("*.csv"))
                print(f"  ├── {item.name}/")
                for csv_file in csv_files:
                    print(f"  │   └── {csv_file.name}")
    
    print()
    print("=" * 80)
    print("Data extraction complete! Ready for analysis.")
    print("=" * 80)
    
    return 0 if successful_scripts == total_scripts else 1


if __name__ == "__main__":
    sys.exit(main())

