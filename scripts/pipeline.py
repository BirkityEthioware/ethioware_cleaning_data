
from pathlib import Path
import pandas as pd
import logging
from clean import clean_linkedin_data, clean_website_data

# Setup project root
PROJECT_ROOT = Path(__file__).parent.parent  # Navigate to ethio_ware_cleaning

# Setup logging
log_dir = PROJECT_ROOT / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / "data_transformation_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def bronze_to_silver():
    """Ingest raw data and clean it for the Silver layer."""
    # Create processed directory
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    # LinkedIn
    try:
        linkedin_df = pd.read_excel(PROJECT_ROOT / "data" / "raw" / "linkedin_stats.xls", header=1)
        linkedin_df = clean_linkedin_data(linkedin_df, "LinkedIn")
        linkedin_df.to_parquet(processed_dir / "linkedin_cleaned.parquet", index=False)
        logging.info("Saved cleaned LinkedIn data to Silver layer")
    except Exception as e:
        logging.error(f"Error processing LinkedIn data: {str(e)}")
    
    # Website
    try:
        website_df = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "website_requests.csv")
        website_df = clean_website_data(website_df, "Website")
        website_df.to_parquet(processed_dir / "website_cleaned.parquet", index=False)
        logging.info("Saved cleaned Website data to Silver layer")
    except Exception as e:
        logging.error(f"Error processing Website data: {str(e)}")
    

def silver_to_gold():
    """Transform Silver layer data into Gold layer for analysis."""
    # Define directories
    processed_dir = PROJECT_ROOT / "data" / "processed"
    final_dir = PROJECT_ROOT / "data" / "final"
    final_dir.mkdir(exist_ok=True)
    
    # LinkedIn
    try:
        linkedin_df = pd.read_parquet(processed_dir / "linkedin_cleaned.parquet")
        linkedin_df["month"] = linkedin_df["Date"].dt.strftime("%Y-%m")
        linkedin_monthly = linkedin_df.groupby("month").agg({
            "Impressions (total)": "sum",
            "Clicks (total)": "sum",
            "Reactions (total)": "sum",
            "Comments (total)": "sum",
            "Engagement rate (total)": "mean"
        }).reset_index()
        linkedin_monthly.to_parquet(final_dir / "linkedin_monthly.parquet", index=False)
        logging.info("Saved monthly LinkedIn aggregates to Gold layer")
        
        linkedin_df["week"] = linkedin_df["Date"].dt.strftime("%Y-%W")
        linkedin_weekly = linkedin_df.groupby("week").agg({
            "Impressions (total)": "sum",
            "Clicks (total)": "sum",
            "Reactions (total)": "sum"
        }).reset_index()
        linkedin_weekly.to_parquet(final_dir / "linkedin_weekly.parquet", index=False)
        logging.info("Saved weekly LinkedIn aggregates to Gold layer")
    except Exception as e:
        logging.error(f"Error processing LinkedIn Gold layer: {str(e)}")
    
    # Website
    try:
        website_df = pd.read_parquet(processed_dir / "website_cleaned.parquet")
        website_top10 = website_df.nlargest(10, "requests")
        website_top10.to_parquet(final_dir / "website_top10_countries.parquet", index=False)
        website_df.to_parquet(final_dir / "website_requests_by_country.parquet", index=False)
        logging.info("Saved Website data to Gold layer")
    except Exception as e:
        logging.error(f"Error processing Website Gold layer: {str(e)}")
    
    # Content & Traffic processing removed as these datasets were migrated to a separate repository.

if __name__ == "__main__":
    bronze_to_silver()
    silver_to_gold()