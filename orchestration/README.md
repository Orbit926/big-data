# ⚙️ Orchestration Layer

This module manages the automated execution and workflow of the data pipeline. In a production environment, this layer would typically be implemented using **AWS Step Functions** or **Apache Airflow**.

## 🎯 Objective

The goal of the orchestration layer is to ensure that each stage of the pipeline (Ingestion $\rightarrow$ Transformation $\rightarrow$ Quality Checks) is executed in the correct order and that any failures in a previous step halt the downstream processes to prevent data corruption.

## 🛠️ Workflow Description

The pipeline follows a linear dependency chain:

1.  **Ingestion (`pipeline/ingest.py`)**: Simulates the movement of raw data from a source (e.g., an external API or FTP) to the **S3 Raw Zone**.
2.  **Transformation (`pipeline/transform.py`)**: Mimics an **AWS Glue ETL job**. It reads the CSV data from the Raw zone, applies schema enforcement, and writes it back to the **S3 Processed/Curated Zone** in **Apache Parquet** format.
3.  **Data Quality (`data_quality/checks.py`)**: Performs automated validation on the newly created Parquet files to ensure compliance with the business rules defined in `data_quality/rules.md`.

## 🚀 Running the Pipeline

To execute the entire pipeline locally, run the provided shell script from the project root:

```bash
chmod +x data-eng-project-team01/orchestration/pipeline.sh
./data-eng-project-team01/orchestration/pipeline.sh
```

## 🏗️ Future AWS Implementation

In a real-world AWS architecture, this orchestration would be replaced by:
- **AWS Step Functions**: To coordinate the sequence of Lambda functions or Glue jobs.
- **Amazon Managed Workflows for Apache Airflow (MWAA)**: For more complex, DAG-based dependencies and scheduling.
- **Amazon EventBridge**: To trigger the pipeline based on S3 event notifications (e.g., when a new file arrives in the Raw bucket).