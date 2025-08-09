from pathlib import Path
import pandas as pd
import logging
from clean import clean_linkedin_data, clean_website_data
from clean_content_traffic_data import (clean_content_chart_data, clean_content_totals, 
                            clean_content_table_data, clean_traffic_chart_data, 
                            clean_traffic_totals, clean_traffic_table_data)

# Setup logging
logging.basicConfig(
    filename="../logs/data_transformation_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def bronze_to_silver():
    """Ingest raw data and clean it for the Silver layer."""
    # Create processed directory
    Path("data/processed").mkdir(exist_ok=True)
    
    # LinkedIn
    try:
        linkedin_df = pd.read_excel("data/raw/linkedin_stats.xls", header=1)
        linkedin_df = clean_linkedin_data(linkedin_df, "LinkedIn")
        linkedin_df.to_parquet("data/processed/linkedin_cleaned.parquet", index=False)
        logging.info("Saved cleaned LinkedIn data to Silver layer")
    except Exception as e:
        logging.error(f"Error processing LinkedIn data: {str(e)}")
    
    # Website
    try:
        website_df = pd.read_csv("data/raw/website_requests.csv")
        website_df = clean_website_data(website_df, "Website")
        website_df.to_parquet("data/processed/website_cleaned.parquet", index=False)
        logging.info("Saved cleaned Website data to Silver layer")
    except Exception as e:
        logging.error(f"Error processing Website data: {str(e)}")
    
    # Content datasets
    content_files = {
        "Chart data.csv": clean_content_chart_data,
        "Totals.csv": clean_content_totals,
        "Table data.csv": clean_content_table_data
    }
    for file, clean_func in content_files.items():
        try:
            df = pd.read_csv(f"data/raw/content/{file}")
            if file == "Table data.csv":
                df_cleaned, total_row = clean_func(df, f"content/{file}")
                total_row.to_parquet(f"data/processed/content_table_total.parquet", index=False)
            else:
                df_cleaned = clean_func(df, f"content/{file}")
            df_cleaned.to_parquet(f"data/processed/content_{file.replace('.csv', '_cleaned.parquet')}", index=False)
            logging.info(f"Saved cleaned content/{file} to Silver layer")
        except Exception as e:
            logging.error(f"Error processing content/{file}: {str(e)}")
    
    # Traffic datasets
    traffic_files = {
        "Chart data.csv": clean_traffic_chart_data,
        "Totals.csv": clean_traffic_totals,
        "Table data.csv": clean_traffic_table_data
    }
    for file, clean_func in traffic_files.items():
        try:
            df = pd.read_csv(f"data/raw/traffic/{file}")
            if file == "Table data.csv":
                df_cleaned, total_row = clean_func(df, f"traffic/{file}")
                total_row.to_parquet(f"data/processed/traffic_table_total.parquet", index=False)
            else:
                df_cleaned = clean_func(df, f"traffic/{file}")
            df_cleaned.to_parquet(f"data/processed/traffic_{file.replace('.csv', '_cleaned.parquet')}", index=False)
            logging.info(f"Saved cleaned traffic/{file} to Silver layer")
        except Exception as e:
            logging.error(f"Error processing traffic/{file}: {str(e)}")

def silver_to_gold():
    """Transform Silver layer data into Gold layer for analysis."""
    # Create final directory
    Path("data/final").mkdir(exist_ok=True)
    
    # LinkedIn
    try:
        linkedin_df = pd.read_parquet("data/processed/linkedin_cleaned.parquet")
        linkedin_df["month"] = linkedin_df["Date"].dt.strftime("%Y-%m")
        linkedin_monthly = linkedin_df.groupby("month").agg({
            "Impressions (total)": "sum",
            "Clicks (total)": "sum",
            "Reactions (total)": "sum",
            "Comments (total)": "sum",
            "Engagement rate (total)": "mean"
        }).reset_index()
        linkedin_monthly.to_parquet("data/final/linkedin_monthly.parquet", index=False)
        logging.info("Saved monthly LinkedIn aggregates to Gold layer")
        
        linkedin_df["week"] = linkedin_df["Date"].dt.strftime("%Y-%W")
        linkedin_weekly = linkedin_df.groupby("week").agg({
            "Impressions (total)": "sum",
            "Clicks (total)": "sum",
            "Reactions (total)": "sum"
        }).reset_index()
        linkedin_weekly.to_parquet("data/final/linkedin_weekly.parquet", index=False)
        logging.info("Saved weekly LinkedIn aggregates to Gold layer")
    except Exception as e:
        logging.error(f"Error processing LinkedIn Gold layer: {str(e)}")
    
    # Website
    try:
        website_df = pd.read_parquet("data/processed/website_cleaned.parquet")
        website_top10 = website_df.nlargest(10, "requests")
        website_top10.to_parquet("data/final/website_top10_countries.parquet", index=False)
        website_df.to_parquet("data/final/website_requests_by_country.parquet", index=False)
        logging.info("Saved Website data to Gold layer")
    except Exception as e:
        logging.error(f"Error processing Website Gold layer: {str(e)}")
    
    # Placeholder for content and traffic Gold layer
    logging.info("Gold layer transformations for content and traffic deferred until analysis goals defined")

if __name__ == "__main__":
    bronze_to_silver()
    silver_to_gold()