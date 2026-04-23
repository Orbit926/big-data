# Data Quality Rules & Requirements

This document defines the quality standards that our data pipeline must satisfy before data is considered "production-ready" in the Curated zone.

## 📋 1. Mandatory Columns & Schema Integrity
- **Rule 1.1**: All records must contain a value for `region`, `species`, and `catch_amount`.
- **Rule 1.2**: The `date` column must follow the ISO 8601 format (`YYYY-MM-DD`).
- **Rule 1.3**: Data types must be strictly enforced (e.g., `catch_amount` must be a float/numeric).

## 📋 2. Data Completeness & Uniqueness
- **Rule 2.1**: No duplicate rows are allowed in the Processed/Curated layers.
- **Rule 2.2**: The dataset must not be empty (minimum of 1 row required for a successful run).
- **Rule 2.3**: All `region` values must belong to a pre-defined list of known global oceanic regions.

## 📋 3. Business Logic & Range Constraints
- **Rule 3.1**: `catch_amount` must be a non-negative value ($\ge 0$).
- **Rule 3.2**: `effort_hours` must be a non-negative value ($\ge 0$).
- **Rule 3.3**: The `date` of the catch cannot be in the future.

## 📋 4. Technical Integrity
- **Rule 4.1**: File format must be Apache Parquet for the Processed/Curated zones.
- **Rule 4.2**: Files must be partitioned by `year` and `region` to optimize Athena performance.