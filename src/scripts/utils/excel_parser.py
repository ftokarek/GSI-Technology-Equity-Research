
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re
from datetime import datetime

class ExcelParser:
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.excel_file = pd.ExcelFile(file_path)
        self.sheet_names = self.excel_file.sheet_names
        
    def get_sheet_names(self) -> List[str]:
        return self.sheet_names
    
    def read_sheet(self, sheet_name: str, **kwargs) -> pd.DataFrame:
        return pd.read_excel(self.excel_file, sheet_name=sheet_name, **kwargs)
    
    def find_header_row(self, df: pd.DataFrame, keywords: List[str] = None) -> int:
        if keywords is None:
            keywords = ['assets', 'revenue', 'date', 'period', 'fiscal', 'quarter']
        
        for idx, row in df.iterrows():
            row_str = ' '.join([str(val).lower() for val in row if pd.notna(val)])
            if any(keyword in row_str for keyword in keywords):
                return idx
        return 0
    
    def clean_dataframe(self, df: pd.DataFrame, header_row: int = 0) -> pd.DataFrame:
        if header_row > 0:
            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        df = df.dropna(how='all')
        
        df = df.dropna(axis=1, how='all')
        
        df.columns = [self._clean_column_name(col) for col in df.columns]
        
        df = df.loc[:, ~df.columns.duplicated()]
        
        return df
    
    def _clean_column_name(self, col_name) -> str:
        if pd.isna(col_name):
            return 'unnamed'
        
        col_name = str(col_name).lower().strip()
        
        col_name = re.sub(r'[^\w\s\(\)]', '', col_name)
        
        col_name = re.sub(r'\s+', '_', col_name)
        
        return col_name
    
    def detect_table_boundaries(self, df: pd.DataFrame) -> Tuple[int, int]:
        start_row = 0
        for idx, row in df.iterrows():
            non_null_ratio = row.notna().sum() / len(row)
            if non_null_ratio > 0.3:  # At least 30% non-null
                start_row = idx
                break
        
        end_row = len(df)
        for idx in range(len(df) - 1, -1, -1):
            row = df.iloc[idx]
            if row.notna().sum() > 1:  # At least 2 non-null values
                end_row = idx + 1
                break
        
        return start_row, end_row
    
    def extract_metadata_from_filename(self) -> Dict[str, str]:
        filename = self.file_path.stem
        metadata = {
            'filename': filename,
            'company': None,
            'form_type': None,
            'filing_date': None,
            'year': None
        }
        
        company_match = re.search(r'^([^(]+)', filename)
        if company_match:
            metadata['company'] = company_match.group(1).strip()
        
        form_patterns = [
            r'(8-K)', r'(10-K)', r'(10-Q)', r'(DEF\s*14A)',
            r'(S-\d+)', r'(ARS)', r'Form\s+(\w+-?\w*)'
        ]
        for pattern in form_patterns:
            form_match = re.search(pattern, filename, re.IGNORECASE)
            if form_match:
                metadata['form_type'] = form_match.group(1).upper()
                break
        
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if date_match:
            metadata['filing_date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            metadata['year'] = date_match.group(1)
        
        return metadata
    
    def find_financial_statement_sheets(self) -> Dict[str, List[str]]:
        categories = {
            'balance_sheet': [],
            'income_statement': [],
            'cash_flow': [],
            'comprehensive_income': [],
            'equity': [],
            'compensation': [],
            'notes': [],
            'other': []
        }
        
        keywords = {
            'balance_sheet': ['balance sheet', 'balance', 'assets', 'liabilities'],
            'income_statement': ['income statement', 'income', 'operations', 'profit', 'loss'],
            'cash_flow': ['cash flow', 'cash'],
            'comprehensive_income': ['comprehensive'],
            'equity': ['equity', 'stockholders', 'shareholders'],
            'compensation': ['compensation', 'executive'],
            'notes': ['note', 'accounting pronouncements', 'fair value', 'investment']
        }
        
        for sheet in self.sheet_names:
            sheet_lower = sheet.lower()
            categorized = False
            
            for category, kws in keywords.items():
                if any(kw in sheet_lower for kw in kws):
                    categories[category].append(sheet)
                    categorized = True
                    break
            
            if not categorized:
                categories['other'].append(sheet)
        
        return categories
    
    def merge_multi_level_headers(self, df: pd.DataFrame, num_header_rows: int = 2) -> pd.DataFrame:
        if num_header_rows < 2:
            return df
        
        header_rows = []
        for i in range(num_header_rows):
            header_rows.append(df.iloc[i].fillna(''))
        
        merged_headers = []
        for col_idx in range(len(df.columns)):
            parts = [str(header_rows[i].iloc[col_idx]).strip() 
                    for i in range(num_header_rows) 
                    if str(header_rows[i].iloc[col_idx]).strip()]
            merged_header = ' '.join(parts)
            merged_headers.append(self._clean_column_name(merged_header))
        
        df_new = df.iloc[num_header_rows:].copy()
        df_new.columns = merged_headers
        df_new = df_new.reset_index(drop=True)
        
        return df_new
    
    def standardize_financial_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        column_mappings = {
            r'.*date.*': 'date',
            r'.*period.*ended.*': 'period_ended',
            r'.*fiscal.*year.*': 'fiscal_year',
            
            r'.*total.*assets.*': 'total_assets',
            r'.*total.*liabilities.*': 'total_liabilities',
            r'.*stockholders.*equity.*': 'stockholders_equity',
            r'.*cash.*equivalents.*': 'cash_and_equivalents',
            r'.*accounts.*receivable.*': 'accounts_receivable',
            r'.*inventories.*': 'inventories',
            
            r'.*net.*revenues?.*': 'net_revenues',
            r'.*total.*revenues?.*': 'total_revenues',
            r'.*cost.*goods.*sold.*': 'cost_of_goods_sold',
            r'.*gross.*profit.*': 'gross_profit',
            r'.*operating.*income.*': 'operating_income',
            r'.*net.*income.*': 'net_income',
            r'.*net.*loss.*': 'net_loss',
            
            r'.*operating.*activities.*': 'cash_from_operations',
            r'.*investing.*activities.*': 'cash_from_investing',
            r'.*financing.*activities.*': 'cash_from_financing',
        }
        
        new_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            matched = False
            
            for pattern, standard_name in column_mappings.items():
                if re.match(pattern, col_lower):
                    new_columns.append(standard_name)
                    matched = True
                    break
            
            if not matched:
                new_columns.append(col)
        
        df.columns = new_columns
        return df
    
    def extract_numeric_values(self, df: pd.DataFrame, exclude_cols: List[str] = None) -> pd.DataFrame:
        if exclude_cols is None:
            exclude_cols = []
        
        df_copy = df.copy()
        
        for col in df_copy.columns:
            if col in exclude_cols:
                continue
            
            df_copy[col] = pd.to_numeric(df_copy[col], errors='ignore')
        
        return df_copy
    
    def close(self):
        self.excel_file.close()

