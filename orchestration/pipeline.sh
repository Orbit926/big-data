#!/bin/bash

# 🚀 Sea Around Us Data Pipeline Orchestrator
# This script automates the execution of the ingestion, transformation, and quality check steps.

# Set colors for output
GREEN='\033[0;3rogrammable;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}    🚀 Starting Sea Around Us Pipeline Execution    ${NC}"
echo -e "${ 
    BLUE}======================================================${NC}"
echo ""

# Define paths
# In a real AWS environment, these would be Airflow DAGs or Step Functions
INGEST_SCRIPT="data-eng-project-team01/pipeline/ingest.py"
TRANSFORM_SCRIPT="data-eng-project-team01/pipeline/transform.py"
DQ_CHECKS_SCRIPT="data-eng-project-team01/data_quality/checks.py"

# Exit on error
set -e

# 1. INGESTION STEP
echo -e "${GREEN}[1/3] 📥 Running Ingestion (Simulated S3 Upload)...${NC}"
python3 "$INGEST_SCRIPT"
echo -e "${GREEN}✅ Ingestion completed successfully.${NC}"
echo ""

# 2. TRANSFORMATION STEP
echo -e "${GREEN}[2/3] ⚙️ Running Transformation (Simulated AWS Glue)...${NC}"
python3 "$TRANSFORM_SCRIPT"
echo -e "${GREEN}✅ Transformation completed successfully.${NC}"
echo ""

# 3. DATA QUALITY STEP
echo -e "${GREEN}[3/3] 🔍 Running Data Quality Checks...${NC}"
python3 "$DQ_CHECKS_SCRIPT"
echo -e "${GREEN}✅ Data Quality checks completed successfully.${NC}"
echo ""

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}    🎉 Pipeline Execution Finished Successfully!   ${NC}"
echo -e "${BLUE}======================================================${NC}"