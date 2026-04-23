# Project Architecture: Sea Around Us Pipeline

## 🏗️ Overview
This document describes the architectural design of the data pipeline used to process the Sea Around Us fisheries dataset. The architecture is designed to be a scalable, cloud-native "Lakehouse" implementation using AWS managed services.

## 🗺️ Data Flow Diagram (Conceptual)
`Source (CSV)` $\rightarrow$ `S3 Raw Bucket` $\rightarrow$ `AWS Glue (ETL)` $\rightarrow$ `S3 Processed/Curcented Bucket (Parquet)` $\rightarrow$ `Amazon Athena (SQL)` $\rightarrow$ `Amazon QuickSight (BI)`

## 🗄️ Storage Strategy: The S3 Data Lake
We implement a multi-tier storage strategy within Amazon S3 to ensure data lineage and separation of concerns:

1.  **Raw Zone (Bronze)**: 
    - **Format**: Original format (CSV).
    - **Purpose**: Landing area for incoming data. No transformations are applied here.
    - **Lifecycle**: Immutable. Once written, data is never modified.

2.  **Processed Zone (Silver)**: 
    - **Format**: Apache Parquet.
    - **Purpose**: Cleaned, validated, and standardized data.
    - **Key features**: Schema enforcement and basic data type standardization.

3.  **Curated Zone (Gold)**: 
    - **Format**: Apache Parquet (Partitioned).
    - **Purpose**: Highly optimized, aggregated, and business-ready data.
    - **Key features**: Partitioned by key dimensions (e.g., `year`, `region`) to optimize query performance and reduce costs in Athena.

## ⚙️ Core Components

### 1. AWS Glue (ETL Engine)
- **Role**: The compute engine for our transformation logic.
- **Function**: Reads data from the Raw zone, applies schema changes, converts files to Parint, and writes to the Processed/Curated zones.
- **Logic**: Implements schema-on-read and handles the complexity of file format conversion.

### 2. Amazon Athena (Serverless Querying)
- **Role**: The SQL interface for the data lake.
- **Function**: Provides a serverless, distributed query engine to run standard SQL against the S3 data.
- **Benefit**: No infrastructure management required; users pay only for the data scanned.

### 3. Amazon QuickSight (Business Intelligence)
- **Role**: The visualization and reporting layer.
- **Function**: Connects directly to Athena to build interactive dashboards, monitoring global fish catches and ecosystem trends.

## 🔄 Step-by-Step Pipeline Flow
1.  **Ingestion**: Data is uploaded/simulated into the **S3 Raw Bucket**.
2.  **Trigger**: A schedule or event-driven trigger (e.g., S3 Event Notifications) initiates the Glue job.
3.  **Transformation**: Glue reads the CSV, performs cleaning, and converts it to **Parquet**.
4.  **Quality Check**: Post-transformation, a validation script ensures the data meets predefined quality rules.
5.  **Partitioning**: The processed data is stored in the **S3 Curated Bucket**, partitioned by relevant keys (e.g., `year`).
6.  **Consumption**: Analysts query the data via **Athena**, and stakeholders view insights in **QuickSight**.