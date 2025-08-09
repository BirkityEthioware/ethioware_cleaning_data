
from pathlib import Path
import pandas as pd
import logging
from clean import clean_linkedin_data, clean_website_data
from clean_content_traffic_data import (clean_content_chart_data, clean_content_totals, 
                            clean_content_table_data, clean_traffic_chart_data, 
                            clean_traffic_totals, clean_traffic_table_data)

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
    
    # Content datasets
    content_files = {
        "Chart data.csv": clean_content_chart_data,
        "Totals.csv": clean_content_totals,
        "Table data.csv": clean_content_table_data
    }
    for file, clean_func in content_files.items():
        try:
            file_path = PROJECT_ROOT / "data" / "raw" / "content" / file
            if not file_path.exists():
                logging.error(f"File not found: {file_path}")
                continue
            df = pd.read_csv(file_path)
            logging.info(f"Loaded {file_path} with {len(df)} rows")
            if file == "Table data.csv":
                df_cleaned, total_row = clean_func(df, f"content/{file}")
                total_row.to_parquet(processed_dir / "content_table_total.parquet", index=False)
                logging.info(f"Saved content_table_total.parquet with {len(total_row)} rows")
            else:
                df_cleaned = clean_func(df, f"content/{file}")
            df_cleaned.to_parquet(processed_dir / f"content_{file.replace('.csv', '_cleaned.parquet')}", index=False)
            logging.info(f"Saved cleaned content/{file} to Silver layer with {len(df_cleaned)} rows")
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
            file_path = PROJECT_ROOT / "data" / "raw" / "traffic" / file
            if not file_path.exists():
                logging.error(f"File not found: {file_path}")
                continue
            df = pd.read_csv(file_path)
            logging.info(f"Loaded {file_path} with {len(df)} rows")
            if file == "Table data.csv":
                df_cleaned, total_row = clean_func(df, f"traffic/{file}")
                total_row.to_parquet(processed_dir / "traffic_table_total.parquet", index=False)
                logging.info(f"Saved traffic_table_total.parquet with {len(total_row)} rows")
            else:
                df_cleaned = clean_func(df, f"traffic/{file}")
            df_cleaned.to_parquet(processed_dir / f"traffic_{file.replace('.csv', '_cleaned.parquet')}", index=False)
            logging.info(f"Saved cleaned traffic/{file} to Silver layer with {len(df_cleaned)} rows")
        except Exception as e:
            logging.error(f"Error processing traffic/{file}: {str(e)}")

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
    
    # Content: Monthly video performance
    try:
        content_table_df = pd.read_parquet(processed_dir / "content_Table data_cleaned.parquet")
        content_table_df["month"] = content_table_df["Video publish time"].dt.strftime("%Y-%m")
        monthly_content = content_table_df.groupby("month").agg({
            "Views": "sum",
            "Watch time (hours)": "sum",
            "Average percentage viewed (%)": "mean",
            "Impressions": "sum"
        }).reset_index()
        monthly_content.to_parquet(final_dir / "content_monthly.parquet", index=False)
        logging.info("Saved monthly content aggregates to Gold layer")
    except Exception as e:
        logging.error(f"Error processing Content Gold layer: {str(e)}")
    
    # Traffic: Monthly views by traffic source
    try:
        traffic_chart_df = pd.read_parquet(processed_dir / "traffic_Chart data_cleaned.parquet")
        traffic_chart_df["month"] = traffic_chart_df["Date"].dt.strftime("%Y-%m")
        monthly_traffic = traffic_chart_df.groupby(["month", "Traffic source"]).agg({
            "Views": "sum"
        }).reset_index()
        monthly_traffic.to_parquet(final_dir / "traffic_monthly.parquet", index=False)
        logging.info("Saved monthly traffic aggregates to Gold layer")
    except Exception as e:
        logging.error(f"Error processing Traffic Gold layer: {str(e)}")

if __name__ == "__main__":
    bronze_to_silver()
    silver_to_gold()