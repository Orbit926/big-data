# 🔍 Data Quality Strategy

This module implements the validation layer of our data pipeline. Our goal is to ensure that any data moving from the **Raw** zone to the **Processed/Curated** zones meets our strict business and technical requirements.

## 🎯 Strategy Overview

We follow a **Post-Transformation Validation** approach. This means that once the ETL process (simulated by AWS Glue) has transformed the data into Parquet format, we run a suite of automated checks to verify the integrity of the new dataset.

### 🏗️ Workflow Integration

1.  **Transform**: The `pipeline/transform.py` script processes CSV $\rightarrow$ Parint.
2.  **Validate**: The `data_quality/checks.py` script is triggered.
3.  **Promote/Reject**: 
    - If all checks **PASS**, the data is considered "production-ready" and can be used for downstream Analytics (Athena/QuickSight).
    - If any check **FAILS**, the pipeline execution is halted, and an alert is triggered (simulated via console output).

## 🛠️ Implementation Details

- **Tooling**: Python 3.x with `pandas` and `pyarrow`.
- **Logic**: Uses `assert` statements to enforce rules defined in `rules.md`.
- **Checks include**:
    - Null value detection in critical columns.
    - Range validation (e.g., non-negative catch amounts).
    - Uniqueness checks (duplicate detection).
    - Schema completeness.

## 🚀 How to Run

To run the quality checks manually on a processed file:

```bash
python data_quality/checks.py