# Data

This directory contains all datasets used by the MOVE search engine.

## Structure

```
data/
├── raw/         → Original datasets (JSON, CSV) — do not modify
└── processed/   → Cleaned and transformed data ready for ingestion
```

## Guidelines

- **raw/**: Drop source files here. No transformations. Treat as read-only after ingestion.
- **processed/**: Output of ETL scripts. These files are consumed by the `search_engine` app.
- File naming: use `snake_case` with a version suffix when possible (e.g. `destinations_v1.json`).
