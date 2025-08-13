## Project: Ethio Ware Data Cleaning

This repository now focuses only on cleaning and transforming the following datasets:

1. LinkedIn performance statistics (`data/raw/linkedin_stats.xls`)
2. Website request statistics (`data/raw/website_requests.csv`)

The YouTube content and traffic datasets (previously under `data/raw/content` and `data/raw/traffic`) along with their cleaning scripts and analysis notebooks have been moved to a separate repository. All related code, notebooks, and processing steps have been removed here to keep the scope lean.

### Current ETL Pipeline

`scripts/pipeline.py` performs two stages:

- Bronze -> Silver: Ingest raw LinkedIn + Website data and clean them.
- Silver -> Gold: Produce aggregated monthly + weekly LinkedIn metrics and website summaries (top 10 countries + full country breakdown).

### How to Run (Windows PowerShell)

```
python scripts/pipeline.py
```

Outputs are written to:

- `data/processed/` (Silver layer cleaned parquet files)
- `data/final/` (Gold layer aggregated parquet files)

### Logs

Processing logs are stored in `logs/data_transformation_log.txt`.

### Next Steps (Optional)

- Add automated tests for cleaning functions in `clean.py`.
- Add a simple Makefile or task runner.
- Build visualization notebook focused only on current scope.

---
Scope trimmed on migration date: content & traffic modules removed.
