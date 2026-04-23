# Technical Decisions Document

This document outlines the key architectural and technical decisions made during the design and implementation of the Sea Around Us data pipeline.

## 📂 1. File Format: Apache Parquet vs. CSV

**Decision**: We use **Apache Parquet** for the Processed and Curated zones, while keeping **CSV** for the Raw zone.

**Rationale**:
- **Efficiency**: Parquet is a columnar storage format, which significantly reduces the amount of data read during analytical queries (e. Im. Athena).
- **Compression**: Parquet offers superior compression ratios compared to CSV, reducing S3 storage costs.
- **Schema Preservation**: Unlike CSV, Parquet stores metadata and schema information, preventing type inference errors during downstream processing.
- **Cost Optimization**: By using a columnar format, Amazon Athena scans only the required columns, directly reducing the cost per query.

## 📂 2. Data Partitioning Strategy

**Decision**: Implement **partitioning** in the Curated zone based on high-cardinality dimensions (e.g., `year`, `region`).

**Rationale**:
- **Query Performance**: Partitioning allows the query engine (Athena) to "prune" partitions, skipping entire directories of data that do not match the `WHERE` clause.
- **Scalability**: As the dataset grows from MBs to TBs, partitioning ensures that query latency remains manageable.
- **Cost Control**: Fewer data scanned $\rightarrow$ lower Athena costs.

## 📂 3. Schema-on-Read vs. Schema-on-Write

**Decision**: Implement a **Schema-on-Read** approach using AWS Glue and Athena.

**Rationale**:
- **Flexibility**: The Raw zone can ingest data without strict validation, allowing for rapid ingestion of new data sources.
- **Agility**: We can adapt the schema in the Glue Data Catalog without having to rewrite the historical data in the Raw zone.
 layer.
- **Integration**: Athena's ability to interpret S3 data structures makes it easy to define and update the schema via the Glue Catalog.

## 📂 4. Use of Amazon Athena for Analytics

**Decision**: Utilize **Amazon Athena** as the primary serverless SQL engine.

**Rationale**:
- **Serverless**: No need to manage, scale, or patch EC2 instances or EMR clusters.
- **Cost-Effectiveness**: A pay-per-query model is ideal for our workload, as we only incur costs when executing analytical tasks.
- **Standard SQL**: Allows analysts to use familiar SQL syntax, reducing the learning curve and enabling integration with other BI tools like QuickSight.

## 📂 5. Data Quality Strategy

**Decision**: Implement a **Post-Transformation Validation** step.

**Rationale**:
- **Integrity**: By validating data *after* the transformation (Silver/Gold) but *before* it is marked as "production-ready," we prevent corrupted or non-compliant data from reaching the end-users.
- **Automation**: The checks are integrated into the orchestration layer, ensuring no human intervention is required for monitoring basic data health.