
from pathlib import Path
import pandas as pd
import logging
from clean import clean_linkedin_data, clean_website_data

# Setup logging
logging.basicConfig(
    filename="logs/data_transformation_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def bronze_to_silver():
    """Ingest raw data and clean it for the Silver layer."""
    try:
        linkedin_df = pd.read_excel("data/raw/linkedin_stats.xls", header=1)
        website_df = pd.read_csv("data/raw/website_requests.csv")
        logging.info("Loaded raw data into Bronze layer")
    except Exception as e:
        logging.error(f"Error loading raw data: {str(e)}")
        raise
    
    linkedin_df = clean_linkedin_data(linkedin_df, "LinkedIn")
    website_df = clean_website_data(website_df, "Website")
    
    linkedin_df.to_parquet("data/processed/linkedin_cleaned.parquet", index=False)
    website_df.to_parquet("data/processed/website_cleaned.parquet", index=False)
    logging.info("Saved cleaned data to Silver layer")

def silver_to_gold():
    """Transform Silver layer data into Gold layer for analysis."""
    try:
        linkedin_df = pd.read_parquet("data/processed/linkedin_cleaned.parquet")
        website_df = pd.read_parquet("data/processed/website_cleaned.parquet")
        logging.info("Loaded Silver layer data")
    except Exception as e:
        logging.error(f"Error loading Silver layer data: {str(e)}")
        raise
    
    # LinkedIn: Monthly aggregates
    linkedin_df["month"] = linkedin_df["Date"].dt.strftime("%Y-%m")  # Convert to YYYY-MM string
    logging.info(f"LinkedIn month column type: {linkedin_df['month'].dtype}")
    logging.info(f"LinkedIn month sample values: {linkedin_df['month'].head().tolist()}")
    linkedin_monthly = linkedin_df.groupby("month").agg({
        "Impressions (total)": "sum",
        "Clicks (total)": "sum",
        "Reactions (total)": "sum",
        "Comments (total)": "sum",
        "Engagement rate (total)": "mean"
    }).reset_index()
    logging.info(f"LinkedIn monthly month column type: {linkedin_monthly['month'].dtype}")
    logging.info(f"LinkedIn monthly sample values: {linkedin_monthly['month'].head().tolist()}")
    linkedin_monthly.to_parquet("data/final/linkedin_monthly.parquet", index=False)
    logging.info("Saved monthly LinkedIn aggregates to Gold layer")
    
    # LinkedIn: Weekly aggregates
    linkedin_df["week"] = linkedin_df["Date"].dt.strftime("%Y-%W")  # Convert to YYYY-WW string
    linkedin_weekly = linkedin_df.groupby("week").agg({
        "Impressions (total)": "sum",
        "Clicks (total)": "sum",
        "Reactions (total)": "sum"
    }).reset_index()
    linkedin_weekly.to_parquet("data/final/linkedin_weekly.parquet", index=False)
    logging.info("Saved weekly LinkedIn aggregates to Gold layer")
    
    # Website: Top 10 countries by requests
    website_top10 = website_df.nlargest(10, "requests")
    website_top10.to_parquet("data/final/website_top10_countries.parquet", index=False)
    logging.info("Saved top 10 Website countries to Gold layer")
    
    # Website: Full dataset
    website_df.to_parquet("data/final/website_requests_by_country.parquet", index=False)
    logging.info("Saved Website data to Gold layer")

if __name__ == "__main__":
    bronze_to_silver()
    silver_to_gold()