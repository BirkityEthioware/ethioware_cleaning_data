# scripts/pipeline.py
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
    # Load raw data (Bronze)
    linkedin_df = pd.read_excel("data/raw/linkedin_stats.xls", header=1)
    website_df = pd.read_csv("data/raw/website_requests.csv")
    logging.info("Loaded raw data into Bronze layer")
    
    # Clean and normalize
    linkedin_df = clean_linkedin_data(linkedin_df, "LinkedIn")
    website_df = clean_website_data(website_df, "Website")
    
    # Save to Silver layer
    linkedin_df.to_parquet("data/processed/linkedin_cleaned.parquet", index=False)
    website_df.to_parquet("data/processed/website_cleaned.parquet", index=False)
    logging.info("Saved cleaned data to Silver layer")

def silver_to_gold():
    """Transform Silver layer data into Gold layer for analysis."""
    # Load Silver data
    linkedin_df = pd.read_parquet("data/processed/linkedin_cleaned.parquet")
    website_df = pd.read_parquet("data/processed/website_cleaned.parquet")
    logging.info("Loaded Silver layer data")
    
    # Aggregate LinkedIn data by month
    linkedin_df["month"] = linkedin_df["Date"].dt.to_period("M")
    linkedin_agg = linkedin_df.groupby("month").agg({
        "Impressions (total)": "sum",
        "Clicks (total)": "sum",
        "Engagement rate (total)": "mean"
    }).reset_index()
    linkedin_agg.to_parquet("data/final/linkedin_monthly.parquet", index=False)
    logging.info("Saved aggregated LinkedIn data to Gold layer")
    
    # Website data (already aggregated by country)
    website_df.to_parquet("data/final/website_requests_by_country.parquet", index=False)
    logging.info("Saved Website data to Gold layer")

if __name__ == "__main__":
    bronze_to_silver()
    silver_to_gold()