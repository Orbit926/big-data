import pandas as pd
import os

def simulate_glue_transform(source_raw_path, destination_processed_path):
    """
    Simulates an AWS Glue ETL job.
    Reads CSV from the Raw zone and transforms it into Parquet in the Processed zone.
    
    Args:
        source_raw_path (str): Path to the simulated S3 Raw bucket.
        destination_processed_path (str): Path to the simulated S3 Processed bucket.
    """
    print(f"⚙️ Starting transformation process (Simulated AWS Glue)...")
    
    # Check if source directory exists
    if not os.path.exists(source_raw_path):
        print(f"❌ Error: Source Raw directory {source_raw_path} not found.")
        return

    # Find the first CSV file in the raw directory
    csv_files = [f for f in os.listdir(source_raw_path) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"⚠️ No CSV files found in {source_raw_path} to transform.")
        return

    source_file = os.path.join(source_raw_path, csv_files[0])
    print(f"📖 Reading: {source_file}")

    try:
        # 1. Load the data
        df = pd.read_csv(source_file)
        
        # 2. Perform transformations (Simulated ETL logic)
        # TODO: Replace with real Glue/PySpark transformations for large scale data
        print("🛠️ Applying transformations (Cleaning, Type Casting)...")
        
        # Example transformations:
        # - Standardize column names to lowercase
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # - Ensure date columns are datetime objects
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        # - Add a processing timestamp
        df['processed_at'] = pd.Timestamp.now()

        # 3. Prepare destination
        os.makedirs(destination_processed_path, exist_ok=True)
        output_file = os.path.join(destination_processed_path, csv_files[0].replace('.csv', '.parquet'))

        # 4. Write to Parquet
        print(f"💾 Writing Parquet to: {output_file}")
        df.to_parquet(output_file, index=False, engine='pyarrow')
        
        print(f"✅ Transformation successful!")
        print(f"📍 Simulated S3 Path: s3://sea-around-us-processed/{os.path.basename(output_file)}")

    except Exception as e:
        print(f"❌ Transformation failed: {str(e)}")

if __name__ == "__main__":
    # Configuration for simulation
    RAW_ZONE = "data-eng-project-team01/data/raw"
    PROCESSED_ZONE = "data-eng-project-team01/data/processed"
    
    simulate_glue_transform(RAW_ZONE, PROCESSED_ZONE)