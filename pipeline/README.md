# 🏗️ Data Pipeline

This module contains the core logic for the data ingestion and transformation pipeline, simulating the movement of data from a raw landing zone to a processed/curated state.

## 🔄 Workflow

1.  **Ingestion (`ingest.py`)**:
    - Simulates uploading CSV files from a local source to an **Amazon S3 Raw Bucket**.
    - Ensures the raw data is preserved in its original state for lineage.

2.  **Transformation (`transform.py`)**:
    - Simulates an **AWS Glue** ETL job.
    - Reads data from the **S3 Raw Bucket**.
    - Performs cleaning, standardization, and schema enforcement.
    - Converts the data from CSV to **Apache Parquet** format.
    - Writes the final, optimized files to the **S3 Processed/Curated Bucket**.

## 🛠️ Implementation Details

- **Language**: Python 3.x
- **Libraries**: `pandas`, `pyarrow`
- **Simulated Environment**: Local directory structure mimicking Amazon S3 buckets (`data/raw`, `data/processed`).

## 🚀 Running the Pipeline (Local)

To run the transformation step, ensure you have the `data/raw` directory populated with a CSV file, then execute:

```bash
python pipeline/transform.py