import pandas as pd
import logging
from datetime import datetime

def convert_duration_to_seconds(duration_str):
    """Convert duration string (e.g., '0:03:53') to seconds."""
    try:
        if pd.isna(duration_str):
            return 0
        parts = duration_str.split(':')
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            minutes, seconds = parts
            return minutes * 60 + seconds
        return int(duration_str)
    except:
        logging.warning(f"Invalid duration format: {duration_str}, returning 0")
        return 0

def clean_content_chart_data(df, dataset_name):
    """Clean content/Chart data.csv."""
    logging.info(f"Cleaning {dataset_name}")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    logging.info(f"Converted Date to datetime; {df_cleaned['Date'].isna().sum()} invalid dates")
    
    # Handle missing values
    df_cleaned['Video publish time'] = df_cleaned['Video publish time'].fillna('Unknown')
    df_cleaned['Average percentage viewed (%)'] = df_cleaned['Average percentage viewed (%)'].fillna(0)
    
    # Validate numeric columns
    numeric_cols = ['Duration', 'Average percentage viewed (%)']
    negative_summary = {}
    for col in numeric_cols:
        negative_rows = (df_cleaned[col] < 0).sum()
        if negative_rows > 0:
            negative_summary[col] = negative_rows
            logging.warning(f"Negative values in {col}: {negative_rows} rows, setting to 0")
            df_cleaned[col] = df_cleaned[col].clip(lower=0)
    if negative_summary:
        logging.info(f"Negative values corrected in {dataset_name}: {negative_summary}")
    
    return df_cleaned

def clean_content_totals(df, dataset_name):
    """Clean content/Totals.csv."""
    logging.info(f"Cleaning {dataset_name}")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    logging.info(f"Converted Date to datetime; {df_cleaned['Date'].isna().sum()} invalid dates")
    
    # Handle missing values
    df_cleaned['Average percentage viewed (%)'] = df_cleaned['Average percentage viewed (%)'].fillna(0)
    
    # Validate numeric columns
    negative_rows = (df_cleaned['Average percentage viewed (%)'] < 0).sum()
    if negative_rows > 0:
        logging.warning(f"Negative values in Average percentage viewed (%): {negative_rows} rows, setting to 0")
        df_cleaned['Average percentage viewed (%)'] = df_cleaned['Average percentage viewed (%)'].clip(lower=0)
    
    return df_cleaned

def clean_content_table_data(df, dataset_name):
    """Clean content/Table data.csv."""
    logging.info(f"Cleaning {dataset_name}")
    df_cleaned = df.copy()
    
    # Separate Total row
    total_row = df_cleaned[df_cleaned['Content'] == 'Total']
    df_cleaned = df_cleaned[df_cleaned['Content'] != 'Total']
    
    # Convert Video publish time to datetime
    df_cleaned['Video publish time'] = pd.to_datetime(df_cleaned['Video publish time'], errors='coerce')
    logging.info(f"Converted Video publish time to datetime; {df_cleaned['Video publish time'].isna().sum()} invalid dates")
    
    # Handle missing values
    df_cleaned['Video title'] = df_cleaned['Video title'].fillna('Unknown')
    df_cleaned['Duration'] = df_cleaned['Duration'].fillna(df_cleaned['Duration'].median())
    # Drop Regular viewers due to 99% missingness
    if 'Regular viewers' in df_cleaned.columns:
        logging.info("Dropping Regular viewers due to high missingness")
        df_cleaned = df_cleaned.drop(columns=['Regular viewers'])
    df_cleaned['Impressions click-through rate (%)'] = df_cleaned['Impressions click-through rate (%)'].fillna(0)
    
    # Convert Average view duration to seconds
    df_cleaned['Average view duration (seconds)'] = df_cleaned['Average view duration'].apply(convert_duration_to_seconds)
    
    # Validate numeric columns
    numeric_cols = ['Duration', 'Average percentage viewed (%)', 'Engaged views', 
                    'Views', 'Watch time (hours)', 'Subscribers', 'Impressions', 
                    'Impressions click-through rate (%)']
    negative_summary = {}
    for col in numeric_cols:
        negative_rows = (df_cleaned[col] < 0).sum()
        if negative_rows > 0:
            negative_summary[col] = negative_rows
            logging.warning(f"Negative values in {col}: {negative_rows} rows, setting to 0")
            df_cleaned[col] = df_cleaned[col].clip(lower=0)
    if negative_summary:
        logging.info(f"Negative values corrected in {dataset_name}: {negative_summary}")
    
    # Drop original Average view duration
    df_cleaned = df_cleaned.drop(columns=['Average view duration'])
    
    # Handle Total row (impute separately)
    total_row = total_row.copy()
    total_row['Video title'] = total_row['Video title'].fillna('Total Summary')
    total_row['Duration'] = total_row['Duration'].fillna(0)  # Summary row, no duration
    if 'Regular viewers' in total_row.columns:
        total_row = total_row.drop(columns=['Regular viewers'])
    
    return df_cleaned, total_row

def clean_traffic_table_data(df, dataset_name):
    """Clean traffic/Table data.csv."""
    logging.info(f"Cleaning {dataset_name}")
    df_cleaned = df.copy()
    
    # Separate Total row
    total_row = df_cleaned[df_cleaned['Traffic source'] == 'Total']
    df_cleaned = df_cleaned[df_cleaned['Traffic source'] != 'Total']
    
    # Handle missing values
    df_cleaned['Impressions'] = df_cleaned['Impressions'].fillna(0)
    df_cleaned['Impressions click-through rate (%)'] = df_cleaned['Impressions click-through rate (%)'].fillna(0)
    
    # Convert Average view duration to seconds
    df_cleaned['Average view duration (seconds)'] = df_cleaned['Average view duration'].apply(convert_duration_to_seconds)
    
    # Validate numeric columns
    numeric_cols = ['Views', 'Watch time (hours)', 'Impressions', 'Impressions click-through rate (%)']
    negative_summary = {}
    for col in numeric_cols:
        negative_rows = (df_cleaned[col] < 0).sum()
        if negative_rows > 0:
            negative_summary[col] = negative_rows
            logging.warning(f"Negative values in {col}: {negative_rows} rows, setting to 0")
            df_cleaned[col] = df_cleaned[col].clip(lower=0)
    if negative_summary:
        logging.info(f"Negative values corrected in {dataset_name}: {negative_summary}")
    
    # Drop original Average view duration
    df_cleaned = df_cleaned.drop(columns=['Average view duration'])
    
    # Handle Total row
    total_row = total_row.copy()
    total_row['Impressions'] = total_row['Impressions'].fillna(0)
    total_row['Impressions click-through rate (%)'] = total_row['Impressions click-through rate (%)'].fillna(0)
    
    return df_cleaned, total_row

def clean_traffic_chart_data(df, dataset_name):
    """Clean traffic/Chart data.csv."""
    logging.info(f"Cleaning {dataset_name}")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    logging.info(f"Converted Date to datetime; {df_cleaned['Date'].isna().sum()} invalid dates")
    
    # Validate numeric columns
    negative_rows = (df_cleaned['Views'] < 0).sum()
    if negative_rows > 0:
        logging.warning(f"Negative values in Views: {negative_rows} rows, setting to 0")
        df_cleaned['Views'] = df_cleaned['Views'].clip(lower=0)
    
    return df_cleaned

def clean_traffic_totals(df, dataset_name):
    """Clean traffic/Totals.csv."""
    logging.info(f"Cleaning {dataset_name}")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    logging.info(f"Converted Date to datetime; {df_cleaned['Date'].isna().sum()} invalid dates")
    
    # Validate numeric columns
    negative_rows = (df_cleaned['Views'] < 0).sum()
    if negative_rows > 0:
        logging.warning(f"Negative values in Views: {negative_rows} rows, setting to 0")
        df_cleaned['Views'] = df_cleaned['Views'].clip(lower=0)
    
    return df_cleaned