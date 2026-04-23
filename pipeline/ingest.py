import pandas as pd
import os
import shutil

def simulate_s3_ingestion(source_csv_path, destination_raw_path):
    """
    Simulates the process of uploading a CSV file from a local source 
    to an Amazon S3 Raw Bucket.
    
    Args:
        source_csv_path (str): Path to the local source CSV file.
        destination_raw_path (str): Path to the simulated S3 Raw bucket directory.
    """
    print(f"🚀 Starting ingestion process...")
    
    if not os.path.exists(source_csv_path):
        print(f"❌ Error: Source file {source_csv_path} not found.")
        return

    # Ensure the destination directory (simulated S3 bucket) exists
    os.makedirs(destination_raw_path, exist_drop=True)

    try:
        # In a real AWS scenario, we would use boto3 to upload to S3
        # Example: s3_client.upload_file(source_csv_path, bucket_name, object_name)
        # TODO: Replace this local copy with real S3 ingestion using boto3
        
        file_name = os.path.basename(source_csv_path)
        destination_file = os.path.join(destination_raw_path, file_name)
        
        shutil.copy2(source_csv_path, destination_file)
        
        print(f"✅ Successfully ingested {file_name} to {destination_raw_path}")
        print(f"📍 Simulated S3 Path: s3://sea-around-us-raw/{file_name}")
        
    except Exception as e:
        print(f"❌ Ingestion failed: {str(e)}")

if __name__ == "__main__":
    # Configuration for simulation
    # In production, these would be S3 URIs
    LOCAL_SOURCE = "data-eng-project-im/data_samples/sample.csv" 
    # Note: Using relative path for simulation context
    SIMULATED_S3_RAW = "data-eng-project-team01/data/raw"
    
    # Correcting path for the current project structure
    REAL_SOURCE = "data-eng-project-team01/data_samples/sample.csv"
    
    simulate_s3_ingestion(REAL_SOURCE, SIMULATED_S3_RAW)