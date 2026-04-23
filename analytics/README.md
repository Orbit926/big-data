# 📊 Analytics & Business Intelligence

This module contains the analytical layer of the pipeline, including SQL queries for data exploration and performance benchmarks for the storage formats used.

## 🎯 Objective

The goal of this layer is to extract actionable insights from the processed and curated datasets. Using **Amazon Athena**, we can query the Parquet files directly in S3 using standard SQL.

## 🔍 Contents

- **`queries.sql`**: A collection of production-ready SQL queries designed for the `sea_around_us_curated` database. These queries focus on:
    - Productivity analysis (Catch by region/species).
    - Temporal trends (Annual fishing effort).
    - Efficiency metrics (Catch per unit of effort).
- **`benchmark.md`**: A performance comparison between the original **CSV** format and the optimized **Apache Parquet** format, justifying our architectural decisions.

## 🛠️ Technology Stack

- **Engine**: Amazon Athena (Serverless SQL)
- **Storage**: Amazon S3 (Parquet format)
- **Visualization (Planned)**: Amazon QuickSight for dashboards.

## 🚀 How to Use

To run the queries, you can use the AWS CLI or the Amazon Athena Console, pointing to the `data/processed` directory as the data source.