"""
Data cleaning utilities for financial data.
Handles normalization, validation, and standardization.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import re
from datetime import datetime


class DataCleaner:
    """Utility class for cleaning and standardizing financial data."""
    
    @staticmethod
    def remove_empty_rows_and_columns(df: pd.DataFrame, 
                                      threshold: float = 0.8) -> pd.DataFrame:
        """
        Remove rows and columns that are mostly empty.
        
        Args:
            df: DataFrame to clean
            threshold: Minimum ratio of non-null values to keep row/column
            
        Returns:
            Cleaned DataFrame
        """
        # Remove rows where more than (1-threshold) of values are null
        row_threshold = int(threshold * len(df.columns))
        df = df.dropna(thresh=row_threshold)
        
        # Remove columns where more than (1-threshold) of values are null
        col_threshold = int(threshold * len(df))
        df = df.dropna(axis=1, thresh=col_threshold)
        
        return df
    
    @staticmethod
    def clean_financial_values(df: pd.DataFrame, 
                               value_columns: List[str] = None,
                               thousands_units: bool = True) -> pd.DataFrame:
        """
        Clean financial values by removing special characters and converting to numbers.
        
        Args:
            df: DataFrame to clean
            value_columns: List of columns containing financial values (if None, auto-detect)
            thousands_units: If True, assume values are in thousands
            
        Returns:
            DataFrame with cleaned numeric values
        """
        df_copy = df.copy()
        
        if value_columns is None:
            # Auto-detect numeric columns
            value_columns = []
            for col in df_copy.columns:
                if df_copy[col].dtype == object:
                    # Check if column contains numeric-like values
                    sample = df_copy[col].dropna().head(10)
                    if any(DataCleaner._looks_like_number(str(val)) for val in sample):
                        value_columns.append(col)
        
        for col in value_columns:
            if col not in df_copy.columns:
                continue
            
            df_copy[col] = df_copy[col].apply(DataCleaner._clean_numeric_value)
            
            # Convert to numeric
            df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
        
        return df_copy
    
    @staticmethod
    def _looks_like_number(value: str) -> bool:
        """Check if a string looks like a number."""
        # Remove common formatting
        cleaned = re.sub(r'[\$,\s\(\)]', '', str(value))
        try:
            float(cleaned)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _clean_numeric_value(value):
        """
        Clean a single numeric value.
        
        Args:
            value: Value to clean
            
        Returns:
            Cleaned numeric value or None
        """
        if pd.isna(value):
            return None
        
        value_str = str(value).strip()
        
        # Handle empty strings
        if not value_str or value_str in ['-', '—', 'N/A', 'n/a', 'NA']:
            return None
        
        # Check if value is in parentheses (negative number)
        is_negative = False
        if value_str.startswith('(') and value_str.endswith(')'):
            is_negative = True
            value_str = value_str[1:-1]
        
        # Remove currency symbols, commas, and spaces
        value_str = re.sub(r'[\$€£¥,\s]', '', value_str)
        
        # Handle percentage
        if '%' in value_str:
            value_str = value_str.replace('%', '')
            try:
                return float(value_str) / 100
            except ValueError:
                return None
        
        # Convert to float
        try:
            numeric_value = float(value_str)
            return -numeric_value if is_negative else numeric_value
        except ValueError:
            return None
    
    @staticmethod
    def standardize_date_column(df: pd.DataFrame, 
                                date_column: str,
                                date_format: str = None) -> pd.DataFrame:
        """
        Standardize date column to datetime format.
        
        Args:
            df: DataFrame to process
            date_column: Name of the date column
            date_format: Expected date format (if None, auto-detect)
            
        Returns:
            DataFrame with standardized date column
        """
        df_copy = df.copy()
        
        if date_column not in df_copy.columns:
            return df_copy
        
        try:
            if date_format:
                df_copy[date_column] = pd.to_datetime(df_copy[date_column], 
                                                      format=date_format, 
                                                      errors='coerce')
            else:
                df_copy[date_column] = pd.to_datetime(df_copy[date_column], 
                                                      errors='coerce')
        except Exception:
            pass
        
        return df_copy
    
    @staticmethod
    def add_metadata_columns(df: pd.DataFrame, 
                            metadata: Dict[str, str]) -> pd.DataFrame:
        """
        Add metadata columns to the beginning of the DataFrame.
        
        Args:
            df: DataFrame to enhance
            metadata: Dictionary of metadata to add
            
        Returns:
            DataFrame with metadata columns
        """
        df_copy = df.copy()
        
        # Add metadata columns at the beginning
        for key, value in reversed(list(metadata.items())):
            df_copy.insert(0, key, value)
        
        return df_copy
    
    @staticmethod
    def deduplicate_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle duplicate column names by adding suffixes.
        
        Args:
            df: DataFrame with potentially duplicate column names
            
        Returns:
            DataFrame with unique column names
        """
        df_copy = df.copy()
        
        # Track column name counts
        col_counts = {}
        new_columns = []
        
        for col in df_copy.columns:
            if col in col_counts:
                col_counts[col] += 1
                new_columns.append(f"{col}_{col_counts[col]}")
            else:
                col_counts[col] = 0
                new_columns.append(col)
        
        df_copy.columns = new_columns
        return df_copy
    
    @staticmethod
    def normalize_item_names(df: pd.DataFrame, 
                            item_column: str = None) -> pd.DataFrame:
        """
        Normalize financial item names (e.g., 'Cash and cash equivalents').
        
        Args:
            df: DataFrame to process
            item_column: Column containing item names (usually first column)
            
        Returns:
            DataFrame with normalized item names
        """
        df_copy = df.copy()
        
        if item_column is None:
            item_column = df_copy.columns[0]
        
        if item_column not in df_copy.columns:
            return df_copy
        
        # Standardization mappings
        mappings = {
            r'.*cash.*cash equivalents.*': 'Cash and cash equivalents',
            r'.*short.*term.*investments?.*': 'Short-term investments',
            r'.*accounts? receivable.*': 'Accounts receivable',
            r'.*inventories.*': 'Inventories',
            r'.*total current assets.*': 'Total current assets',
            r'.*property.*equipment.*': 'Property and equipment',
            r'.*total assets.*': 'Total assets',
            r'.*accounts? payable.*': 'Accounts payable',
            r'.*accrued.*expenses.*': 'Accrued expenses',
            r'.*total current liabilities.*': 'Total current liabilities',
            r'.*total liabilities.*': 'Total liabilities',
            r'.*stockholders?.* equity.*': 'Stockholders equity',
            r'.*shareholders?.* equity.*': 'Stockholders equity',
            r'.*net revenues?.*': 'Net revenues',
            r'.*cost of (?:goods|revenue).*sold.*': 'Cost of revenues',
            r'.*gross profit.*': 'Gross profit',
            r'.*research.*development.*': 'Research and development',
            r'.*selling.*general.*administrative.*': 'Selling, general and administrative',
            r'.*operating (?:income|profit).*': 'Operating income',
            r'.*operating loss.*': 'Operating loss',
            r'.*net income.*': 'Net income',
            r'.*net loss.*': 'Net loss',
            r'.*(?:basic|diluted) (?:earnings|loss) per share.*': 'Earnings per share',
        }
        
        def normalize_name(name):
            if pd.isna(name):
                return name
            
            name_lower = str(name).lower().strip()
            
            for pattern, standard_name in mappings.items():
                if re.match(pattern, name_lower):
                    return standard_name
            
            return name
        
        df_copy[item_column] = df_copy[item_column].apply(normalize_name)
        
        return df_copy
    
    @staticmethod
    def validate_financial_statement(df: pd.DataFrame, 
                                     statement_type: str) -> Dict[str, any]:
        """
        Validate a financial statement DataFrame.
        
        Args:
            df: DataFrame to validate
            statement_type: Type of statement ('balance_sheet', 'income_statement', 'cash_flow')
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_valid': True,
            'row_count': len(df),
            'column_count': len(df.columns),
            'missing_data_percentage': df.isna().sum().sum() / (df.shape[0] * df.shape[1]) * 100,
            'issues': []
        }
        
        # Basic checks
        if len(df) == 0:
            validation['is_valid'] = False
            validation['issues'].append('DataFrame is empty')
        
        if len(df.columns) < 2:
            validation['is_valid'] = False
            validation['issues'].append('Insufficient columns')
        
        # Statement-specific checks
        if statement_type == 'balance_sheet':
            required_items = ['assets', 'liabilities', 'equity']
            DataCleaner._check_required_items(df, required_items, validation)
        
        elif statement_type == 'income_statement':
            required_items = ['revenue', 'expense', 'income', 'loss']
            DataCleaner._check_required_items(df, required_items, validation)
        
        elif statement_type == 'cash_flow':
            required_items = ['operating', 'investing', 'financing']
            DataCleaner._check_required_items(df, required_items, validation)
        
        return validation
    
    @staticmethod
    def _check_required_items(df: pd.DataFrame, 
                             required_keywords: List[str],
                             validation: Dict) -> None:
        """Helper method to check if DataFrame contains required items."""
        if len(df) == 0:
            return
        
        first_col = df.iloc[:, 0].astype(str).str.lower()
        all_text = ' '.join(first_col.tolist())
        
        for keyword in required_keywords:
            if keyword not in all_text:
                validation['issues'].append(f'Missing expected keyword: {keyword}')
    
    @staticmethod
    def remove_subtotal_rows(df: pd.DataFrame, 
                            item_column: str = None,
                            keywords: List[str] = None) -> pd.DataFrame:
        """
        Remove subtotal and total rows that might cause double-counting.
        
        Args:
            df: DataFrame to process
            item_column: Column containing item names
            keywords: Keywords that indicate subtotal rows
            
        Returns:
            DataFrame with subtotal rows removed
        """
        if keywords is None:
            keywords = ['subtotal', 'sub-total', 'continued']
        
        df_copy = df.copy()
        
        if item_column is None:
            item_column = df_copy.columns[0]
        
        if item_column not in df_copy.columns:
            return df_copy
        
        # Create mask for rows to keep
        mask = ~df_copy[item_column].astype(str).str.lower().str.contains(
            '|'.join(keywords), 
            na=False, 
            regex=True
        )
        
        return df_copy[mask]
    
    @staticmethod
    def pivot_quarterly_data(df: pd.DataFrame,
                            item_column: str,
                            period_columns: List[str]) -> pd.DataFrame:
        """
        Pivot quarterly data from wide to long format.
        
        Args:
            df: DataFrame in wide format
            item_column: Column containing line item names
            period_columns: Columns containing period data
            
        Returns:
            DataFrame in long format
        """
        df_long = pd.melt(
            df,
            id_vars=[item_column],
            value_vars=period_columns,
            var_name='period',
            value_name='value'
        )
        
        return df_long

