import pandas as pd
import logging
import pycountry

def clean_linkedin_data(df, dataset_name):
    """
    Clean and normalize LinkedIn dataset.
    Args:
        df: Input DataFrame (with correct headers)
        dataset_name: Name for logging
    Returns:
        Cleaned DataFrame
    """
    logging.info(f"Cleaning {dataset_name} dataset")
    
    # Convert Date to datetime
    initial_rows = len(df)
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    null_dates = df["Date"].isnull().sum()
    logging.info(f"Converted 'Date' to datetime, {null_dates} nulls created")
    
    # Drop rows with invalid dates
    df = df.dropna(subset=["Date"])
    logging.info(f"Dropped {initial_rows - len(df)} rows with invalid dates")
    
    # Convert numerical columns
    numerical_columns = [
        "Impressions (organic)", "Impressions (sponsored)", "Impressions (total)",
        "Unique impressions (organic)", "Clicks (organic)", "Clicks (sponsored)",
        "Clicks (total)", "Reactions (organic)", "Reactions (sponsored)",
        "Reactions (total)", "Comments (organic)", "Comments (sponsored)",
        "Comments (total)", "Reposts (organic)", "Reposts (sponsored)",
        "Reposts (total)", "Engagement rate (organic)",
        "Engagement rate (sponsored)", "Engagement rate (total)"
    ]
    for col in numerical_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        logging.info(f"Converted '{col}' to numeric, {df[col].isnull().sum()} nulls created")
    
    # Ensure engagement rates are float
    for col in ["Engagement rate (organic)", "Engagement rate (sponsored)", "Engagement rate (total)"]:
        df[col] = df[col].astype("float64")
        logging.info(f"Ensured '{col}' is float64")
    
    # Handle missing values
    initial_rows = len(df)
    df = df.dropna()  # Drop rows with any missing values
    logging.info(f"Dropped {initial_rows - len(df)} rows with missing values")
    
    # Validate numerical columns (no negative values, exclude engagement rates)
    negative_summary = {}
    for col in numerical_columns[:-3]:
        negative_rows = (df[col] < 0).sum()
        if negative_rows > 0:
            negative_summary[col] = negative_rows
            logging.warning(f"Negative values found in '{col}' for {negative_rows} rows, setting to 0")
            df[col] = df[col].clip(lower=0)
    
    # Log negative values summary
    if negative_summary:
        logging.info(f"Summary of negative values corrected: {negative_summary}")
    
    # Validate engagement rates
    df["calculated_engagement"] = (
        df["Clicks (total)"] + df["Reactions (total)"] +
        df["Comments (total)"] + df["Reposts (total)"]
    ) / df["Impressions (total)"].replace(0, 1)  # Avoid division by zero
    df["engagement_diff"] = abs(df["Engagement rate (total)"] - df["calculated_engagement"])
    inconsistent_rows = df[df["engagement_diff"] > 0.01]
    if not inconsistent_rows.empty:
        logging.warning(f"Found {len(inconsistent_rows)} inconsistent engagement rates, updating with calculated values")
        df["Engagement rate (total)"] = df["calculated_engagement"]
    df = df.drop(columns=["calculated_engagement", "engagement_diff"])
    
    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates(subset=["Date"], keep="first")
    logging.info(f"Removed {initial_rows - len(df)} duplicates by Date")
    
    return df

def clean_website_data(df, dataset_name):
    """
    Clean and normalize Website dataset.
    Args:
        df: Input DataFrame
        dataset_name: Name for logging
    Returns:
        Cleaned DataFrame
    """
    logging.info(f"Cleaning {dataset_name} dataset")
    
    # Standardize country codes to full names
    def standardize_country(code):
        try:
            country = pycountry.countries.get(alpha_2=code.strip().upper())
            if country:
                return country.name
            logging.warning(f"Invalid country code: {code}")
            return code
        except:
            logging.warning(f"Error processing country code: {code}")
            return code
    
    df["name"] = df["name"].apply(standardize_country)
    logging.info("Standardized country codes to full names")
    
    # Validate requests
    if (df["requests"] < 0).any():
        logging.warning("Negative values found in 'requests', setting to 0")
        df["requests"] = df["requests"].clip(lower=0)
    
    # Remove duplicates
    initial_rows = len(df)
    df = df.drop_duplicates(subset=["name"], keep="first")
    logging.info(f"Removed {initial_rows - len(df)} duplicates by name")
    
    return df