#!/usr/bin/env python3
"""
AACT Data Download Script
Downloads and prepares the AACT (Aggregate Analysis of ClinicalTrials.gov) dataset
"""

import requests
import os
import zipfile
import pandas as pd
import sqlite3
from datetime import datetime
import time

class AACTDataDownloader:
    def __init__(self, data_dir="aact_data"):
        self.data_dir = data_dir
        self.base_url = "https://aact.ctti-clinicaltrials.org/static/exported_files/current/"
        
        # Key tables for antibody analysis
        self.key_tables = [
            'studies',
            'interventions', 
            'conditions',
            'adverse_events',
            'outcomes',
            'sponsors',
            'facilities'
        ]
    
    def create_data_directory(self):
        """Create the data directory structure"""
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"Created data directory: {self.data_dir}")
    
    def download_table(self, table_name):
        """Download a specific table from AACT"""
        url = f"{self.base_url}{table_name}.csv"
        
        try:
            print(f"Downloading {table_name}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            file_path = os.path.join(self.data_dir, f"{table_name}.csv")
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded {table_name}.csv ({os.path.getsize(file_path) / 1024 / 1024:.1f} MB)")
            return True
            
        except Exception as e:
            print(f"Error downloading {table_name}: {e}")
            return False
    
    def download_all_tables(self):
        """Download all key tables"""
        print("Starting AACT data download...")
        print("This may take several minutes depending on your internet connection.")
        
        self.create_data_directory()
        
        successful_downloads = []
        failed_downloads = []
        
        for table in self.key_tables:
            if self.download_table(table):
                successful_downloads.append(table)
            else:
                failed_downloads.append(table)
            
            # Be respectful to the server
            time.sleep(1)
        
        print(f"\nDownload Summary:")
        print(f"Successful: {len(successful_downloads)} tables")
        print(f"Failed: {len(failed_downloads)} tables")
        
        if failed_downloads:
            print(f"Failed tables: {failed_downloads}")
        
        return successful_downloads
    
    def create_sqlite_database(self):
        """Create SQLite database from downloaded CSV files"""
        print("Creating SQLite database...")
        
        db_path = os.path.join(self.data_dir, "aact.db")
        conn = sqlite3.connect(db_path)
        
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            table_name = csv_file.replace('.csv', '')
            file_path = os.path.join(self.data_dir, csv_file)
            
            try:
                print(f"Loading {table_name} into database...")
                
                # Read CSV in chunks to handle large files
                chunk_size = 10000
                first_chunk = True
                
                for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
                    chunk.to_sql(table_name, conn, if_exists='replace' if first_chunk else 'append', index=False)
                    first_chunk = False
                
                print(f"Loaded {table_name} successfully")
                
            except Exception as e:
                print(f"Error loading {table_name}: {e}")
        
        conn.close()
        print(f"SQLite database created: {db_path}")
    
    def create_sample_dataset(self):
        """Create a smaller sample dataset for testing"""
        print("Creating sample dataset for testing...")
        
        sample_dir = os.path.join(self.data_dir, "sample")
        os.makedirs(sample_dir, exist_ok=True)
        
        # Create sample studies
        sample_studies = pd.DataFrame({
            'nct_id': [f'NCT{str(i).zfill(8)}' for i in range(1000)],
            'official_title': [
                f'Study of {"Anti-" if i % 2 == 0 else ""}{["CD20", "HER2", "PD-1", "VEGF", "TNF-alpha"][i % 5]} {"Monoclonal Antibody" if i % 3 == 0 else "Antibody"} in {"Cancer" if i % 2 == 0 else "Autoimmune Disease"}'
                for i in range(1000)
            ],
            'brief_title': [f'Antibody Study {i}' for i in range(1000)],
            'phase': ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4'] * 250,
            'enrollment': [np.random.randint(20, 2000) for _ in range(1000)],
            'start_date': pd.date_range('2010-01-01', periods=1000),
            'completion_date': pd.date_range('2012-01-01', periods=1000),
            'status': ['Completed', 'Recruiting', 'Terminated'] * 333 + ['Completed']
        })
        
        sample_studies.to_csv(os.path.join(sample_dir, "studies.csv"), index=False)
        
        # Create sample interventions
        sample_interventions = pd.DataFrame({
            'nct_id': [f'NCT{str(i).zfill(8)}' for i in range(1000)],
            'intervention_type': ['Drug'] * 1000,
            'intervention_name': [
                np.random.choice(['Rituximab', 'Trastuzumab', 'Pembrolizumab', 'Bevacizumab', 'Adalimumab'])
                for _ in range(1000)
            ]
        })
        
        sample_interventions.to_csv(os.path.join(sample_dir, "interventions.csv"), index=False)
        
        # Create sample conditions
        sample_conditions = pd.DataFrame({
            'nct_id': [f'NCT{str(i).zfill(8)}' for i in range(1000)],
            'condition': [
                np.random.choice(['Cancer', 'Autoimmune Disease', 'Infectious Disease'])
                for _ in range(1000)
            ]
        })
        
        sample_conditions.to_csv(os.path.join(sample_dir, "conditions.csv"), index=False)
        
        print(f"Sample dataset created in {sample_dir}")
    
    def verify_download(self):
        """Verify the downloaded data"""
        print("Verifying downloaded data...")
        
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            file_path = os.path.join(self.data_dir, csv_file)
            try:
                df = pd.read_csv(file_path, nrows=5)  # Just check first 5 rows
                print(f"✓ {csv_file}: {len(df.columns)} columns, sample data available")
            except Exception as e:
                print(f"✗ {csv_file}: Error reading file - {e}")
    
    def get_data_info(self):
        """Get information about the downloaded data"""
        print("Data Information:")
        
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        
        total_size = 0
        for csv_file in csv_files:
            file_path = os.path.join(self.data_dir, csv_file)
            size_mb = os.path.getsize(file_path) / 1024 / 1024
            total_size += size_mb
            
            try:
                df = pd.read_csv(file_path, nrows=1)
                print(f"  {csv_file}: {size_mb:.1f} MB, {len(df.columns)} columns")
            except:
                print(f"  {csv_file}: {size_mb:.1f} MB, columns unknown")
        
        print(f"Total size: {total_size:.1f} MB")

def main():
    """Main function to download AACT data"""
    print("AACT Data Downloader")
    print("=" * 50)
    
    downloader = AACTDataDownloader()
    
    # Check if data already exists
    if os.path.exists(downloader.data_dir) and os.listdir(downloader.data_dir):
        print("Data directory already exists with files.")
        response = input("Do you want to re-download? (y/n): ")
        if response.lower() != 'y':
            downloader.verify_download()
            downloader.get_data_info()
            return
    
    # Download options
    print("\nDownload options:")
    print("1. Download all AACT tables (large, ~1GB+)")
    print("2. Create sample dataset (small, for testing)")
    print("3. Download specific tables only")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        print("\nDownloading all AACT tables...")
        successful = downloader.download_all_tables()
        
        if successful:
            print("\nCreating SQLite database...")
            downloader.create_sqlite_database()
        
        downloader.verify_download()
        downloader.get_data_info()
        
    elif choice == '2':
        print("\nCreating sample dataset...")
        downloader.create_sample_dataset()
        
    elif choice == '3':
        print("\nAvailable tables:")
        for i, table in enumerate(downloader.key_tables, 1):
            print(f"{i}. {table}")
        
        table_choice = input("Enter table numbers (comma-separated): ")
        selected_tables = [downloader.key_tables[int(x)-1] for x in table_choice.split(',')]
        
        for table in selected_tables:
            downloader.download_table(table)
        
        downloader.verify_download()
        downloader.get_data_info()
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    print("\nDownload completed!")
    print("You can now run the antibody analysis scripts.")

if __name__ == "__main__":
    import numpy as np
    main()