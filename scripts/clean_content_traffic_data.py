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
    logging.info(f"Cleaning {dataset_name} (content/Chart data.csv)")
    logging.info("Step: Convert 'Date' to datetime with errors='coerce'.")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    invalid_dates = df_cleaned['Date'].isna().sum()
    logging.info(f"Converted 'Date' to datetime; {invalid_dates} invalid dates found and set to NaT.")
    
    # Handle missing values
    missing_video_publish = df_cleaned['Video publish time'].isna().sum()
    missing_avg_pct = df_cleaned['Average percentage viewed (%)'].isna().sum()
    df_cleaned['Video publish time'] = df_cleaned['Video publish time'].fillna('Unknown')
    df_cleaned['Average percentage viewed (%)'] = df_cleaned['Average percentage viewed (%)'].fillna(0)
    logging.info(f"Filled {missing_video_publish} missing 'Video publish time' with 'Unknown'.")
    logging.info(f"Filled {missing_avg_pct} missing 'Average percentage viewed (%)' with 0.")
    
    # Validate numeric columns
    numeric_cols = ['Duration', 'Average percentage viewed (%)']
    negative_summary = {}
    for col in numeric_cols:
        negative_rows = (df_cleaned[col] < 0).sum()
        if negative_rows > 0:
            negative_summary[col] = negative_rows
            logging.warning(f"Negative values in {col}: {negative_rows} rows, set to 0 using clip(lower=0)")
            df_cleaned[col] = df_cleaned[col].clip(lower=0)
    if negative_summary:
        logging.info(f"Negative values corrected in {dataset_name}: {negative_summary}")
    logging.info("Completed cleaning for content/Chart data.csv.")
    return df_cleaned

def clean_content_totals(df, dataset_name):
    """Clean content/Totals.csv."""
    logging.info(f"Cleaning {dataset_name} (content/Totals.csv)")
    logging.info("Step: Convert 'Date' to datetime with errors='coerce'.")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    invalid_dates = df_cleaned['Date'].isna().sum()
    logging.info(f"Converted 'Date' to datetime; {invalid_dates} invalid dates found and set to NaT.")
    
    # Handle missing values
    missing_avg_pct = df_cleaned['Average percentage viewed (%)'].isna().sum()
    df_cleaned['Average percentage viewed (%)'] = df_cleaned['Average percentage viewed (%)'].fillna(0)
    logging.info(f"Filled {missing_avg_pct} missing 'Average percentage viewed (%)' with 0.")
    
    # Validate numeric columns
    negative_rows = (df_cleaned['Average percentage viewed (%)'] < 0).sum()
    if negative_rows > 0:
        logging.warning(f"Negative values in 'Average percentage viewed (%)': {negative_rows} rows, set to 0 using clip(lower=0)")
        df_cleaned['Average percentage viewed (%)'] = df_cleaned['Average percentage viewed (%)'].clip(lower=0)
    if negative_rows > 0:
        logging.info(f"Negative values corrected in {dataset_name}: {{'Average percentage viewed (%)': negative_rows}}")
    logging.info("Completed cleaning for content/Totals.csv.")
    return df_cleaned

def clean_content_table_data(df, dataset_name):
    """Clean content/Table data.csv."""
    logging.info(f"Cleaning {dataset_name} (content/Table data.csv)")
    logging.info("Step: Separate 'Total' row, convert 'Video publish time' to datetime, handle missing values, drop columns with high missingness, convert durations, validate numeric columns.")
    df_cleaned = df.copy()
    
    # Separate Total row
    total_row = df_cleaned[df_cleaned['Content'] == 'Total']
    df_cleaned = df_cleaned[df_cleaned['Content'] != 'Total']
    logging.info(f"Separated {len(total_row)} 'Total' rows from main data.")
    
    # Convert Video publish time to datetime
    df_cleaned['Video publish time'] = pd.to_datetime(df_cleaned['Video publish time'], errors='coerce')
    invalid_dates = df_cleaned['Video publish time'].isna().sum()
    logging.info(f"Converted 'Video publish time' to datetime; {invalid_dates} invalid dates found and set to NaT.")
    
    # Handle missing values
    missing_titles = df_cleaned['Video title'].isna().sum()
    missing_duration = df_cleaned['Duration'].isna().sum()
    df_cleaned['Video title'] = df_cleaned['Video title'].fillna('Unknown')
    df_cleaned['Duration'] = df_cleaned['Duration'].fillna(df_cleaned['Duration'].median())
    logging.info(f"Filled {missing_titles} missing 'Video title' with 'Unknown'.")
    logging.info(f"Filled {missing_duration} missing 'Duration' with median value.")
    # Drop Regular viewers due to 99% missingness
    if 'Regular viewers' in df_cleaned.columns:
        logging.info("Dropped 'Regular viewers' column due to high missingness (99%).")
        df_cleaned = df_cleaned.drop(columns=['Regular viewers'])
    missing_ctr = df_cleaned['Impressions click-through rate (%)'].isna().sum()
    df_cleaned['Impressions click-through rate (%)'] = df_cleaned['Impressions click-through rate (%)'].fillna(0)
    logging.info(f"Filled {missing_ctr} missing 'Impressions click-through rate (%)' with 0.")
    
    # Convert Average view duration to seconds
    df_cleaned['Average view duration (seconds)'] = df_cleaned['Average view duration'].apply(convert_duration_to_seconds)
    logging.info("Converted 'Average view duration' to seconds.")
    
    # Validate numeric columns
    numeric_cols = ['Duration', 'Average percentage viewed (%)', 'Engaged views', 
                    'Views', 'Watch time (hours)', 'Subscribers', 'Impressions', 
                    'Impressions click-through rate (%)']
    negative_summary = {}
    for col in numeric_cols:
        negative_rows = (df_cleaned[col] < 0).sum()
        if negative_rows > 0:
            negative_summary[col] = negative_rows
            logging.warning(f"Negative values in {col}: {negative_rows} rows, set to 0 using clip(lower=0)")
            df_cleaned[col] = df_cleaned[col].clip(lower=0)
    if negative_summary:
        logging.info(f"Negative values corrected in {dataset_name}: {negative_summary}")
    
    # Drop original Average view duration
    df_cleaned = df_cleaned.drop(columns=['Average view duration'])
    logging.info("Dropped original 'Average view duration' column.")
    
    # Handle Total row (impute separately)
    total_row = total_row.copy()
    total_row['Video title'] = total_row['Video title'].fillna('Total Summary')
    total_row['Duration'] = total_row['Duration'].fillna(0)  # Summary row, no duration
    if 'Regular viewers' in total_row.columns:
        total_row = total_row.drop(columns=['Regular viewers'])
    logging.info("Completed cleaning for content/Table data.csv.")
    return df_cleaned, total_row

def clean_traffic_table_data(df, dataset_name):
    """Clean traffic/Table data.csv."""
    logging.info(f"Cleaning {dataset_name} (traffic/Table data.csv)")
    logging.info("Step: Separate 'Total' row, handle missing values, convert durations, validate numeric columns.")
    df_cleaned = df.copy()
    
    # Separate Total row
    total_row = df_cleaned[df_cleaned['Traffic source'] == 'Total']
    df_cleaned = df_cleaned[df_cleaned['Traffic source'] != 'Total']
    logging.info(f"Separated {len(total_row)} 'Total' rows from main data.")
    
    # Handle missing values
    missing_impr = df_cleaned['Impressions'].isna().sum()
    missing_ctr = df_cleaned['Impressions click-through rate (%)'].isna().sum()
    df_cleaned['Impressions'] = df_cleaned['Impressions'].fillna(0)
    df_cleaned['Impressions click-through rate (%)'] = df_cleaned['Impressions click-through rate (%)'].fillna(0)
    logging.info(f"Filled {missing_impr} missing 'Impressions' with 0.")
    logging.info(f"Filled {missing_ctr} missing 'Impressions click-through rate (%)' with 0.")
    
    # Convert Average view duration to seconds
    df_cleaned['Average view duration (seconds)'] = df_cleaned['Average view duration'].apply(convert_duration_to_seconds)
    logging.info("Converted 'Average view duration' to seconds.")
    
    # Validate numeric columns
    numeric_cols = ['Views', 'Watch time (hours)', 'Impressions', 'Impressions click-through rate (%)']
    negative_summary = {}
    for col in numeric_cols:
        negative_rows = (df_cleaned[col] < 0).sum()
        if negative_rows > 0:
            negative_summary[col] = negative_rows
            logging.warning(f"Negative values in {col}: {negative_rows} rows, set to 0 using clip(lower=0)")
            df_cleaned[col] = df_cleaned[col].clip(lower=0)
    if negative_summary:
        logging.info(f"Negative values corrected in {dataset_name}: {negative_summary}")
    
    # Drop original Average view duration
    df_cleaned = df_cleaned.drop(columns=['Average view duration'])
    logging.info("Dropped original 'Average view duration' column.")
    
    # Handle Total row
    total_row = total_row.copy()
    total_row['Impressions'] = total_row['Impressions'].fillna(0)
    total_row['Impressions click-through rate (%)'] = total_row['Impressions click-through rate (%)'].fillna(0)
    logging.info("Completed cleaning for traffic/Table data.csv.")
    return df_cleaned, total_row

def clean_traffic_chart_data(df, dataset_name):
    """Clean traffic/Chart data.csv."""
    logging.info(f"Cleaning {dataset_name} (traffic/Chart data.csv)")
    logging.info("Step: Convert 'Date' to datetime, validate numeric columns.")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    invalid_dates = df_cleaned['Date'].isna().sum()
    logging.info(f"Converted 'Date' to datetime; {invalid_dates} invalid dates found and set to NaT.")
    
    # Validate numeric columns
    negative_rows = (df_cleaned['Views'] < 0).sum()
    if negative_rows > 0:
        logging.warning(f"Negative values in 'Views': {negative_rows} rows, set to 0 using clip(lower=0)")
        df_cleaned['Views'] = df_cleaned['Views'].clip(lower=0)
    if negative_rows > 0:
        logging.info(f"Negative values corrected in {dataset_name}: {{'Views': negative_rows}}")
    logging.info("Completed cleaning for traffic/Chart data.csv.")
    return df_cleaned

def clean_traffic_totals(df, dataset_name):
    """Clean traffic/Totals.csv."""
    logging.info(f"Cleaning {dataset_name} (traffic/Totals.csv)")
    logging.info("Step: Convert 'Date' to datetime, validate numeric columns.")
    df_cleaned = df.copy()
    
    # Convert Date to datetime
    df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
    invalid_dates = df_cleaned['Date'].isna().sum()
    logging.info(f"Converted 'Date' to datetime; {invalid_dates} invalid dates found and set to NaT.")
    
    # Validate numeric columns
    negative_rows = (df_cleaned['Views'] < 0).sum()
    if negative_rows > 0:
        logging.warning(f"Negative values in 'Views': {negative_rows} rows, set to 0 using clip(lower=0)")
        df_cleaned['Views'] = df_cleaned['Views'].clip(lower=0)
    if negative_rows > 0:
        logging.info(f"Negative values corrected in {dataset_name}: {{'Views': negative_rows}}")
    logging.info("Completed cleaning for traffic/Totals.csv.")
    return df_cleaned