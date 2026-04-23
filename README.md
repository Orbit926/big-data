# AWS Data Engineering Capstone: Sea Around Us Fisheries Pipeline

## 📝 Project Description
This repository contains the implementation of an end-to-end data engineering pipeline designed to process and analyze fisheries data from the "Sea Around Us" dataset. The project demonstrates the use of AWS cloud services to build a scalable, robust, and production-ready data platform.

## 📊 Dataset
The pipeline utilizes the **Sea Around Us fisheries dataset**, which provides comprehensive information on global fish catches, effort, and marine ecosystem health.

## 🎯 Pipeline Objective
The primary goal is to automate the ingestion, transformation, and quality validation of raw fisheries data, moving it through a multi-tier architecture (Raw $\rightarrow$ Processed $\rightarrow$ Curated) to enable high-performance analytical querying and visualization.

## 🏗️ General Architecture
The architecture follows a modern data lakehouse pattern on AWS:
1.  **Ingestion**: Python scripts simulate the movement of CSV data into an **Amazon S3 (Raw Bucket)**.
2.  **Processing**: **AWS Glue** (simulated locally via Python/Pandas) transforms CSV data into **Apache Parquet** format, optimized for analytical workloads.
3.  **Data Quality**: Automated validation checks ensure schema integrity and business rule compliance.
4.  **Storage**: Data is organized in **Amazon S3 (Processed/Curated Buckets)** using a partitioned structure.
5.  **Analytics**: **Amazon Athena** is used for serverless SQL querying against the S3 data lake.
6.  **Visualization**: **Amazon QuickSight** serves as the BI layer for presenting key performance indicators (KPIs).

## 🚀 How to Run the Project
*Note: This project is designed to run locally to simulate the AWS environment.*

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/data-eng-project-team01.git
   cd data-eng-project 
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute the pipeline:**
   ```bash
   ./orchestration/pipeline.sh
   ```

## 👥 Team Roles
- **Data Engineer (Pipeline/Ingestion)**: [Name]
- **Data Engineer (Transformation/Glue)**: [Name]
- **Data Quality Engineer**: [Name]
- **Data Analyst (Analytics/QuickSight)**: [Name]
- **DevOps/Cloud Architect**: [Name]