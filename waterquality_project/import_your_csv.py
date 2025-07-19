#!/usr/bin/env python3
"""
Helper script to import your own CSV file with water quality stations.

Usage:
1. Place your CSV file in the project root directory
2. Update the filename below
3. Run: docker compose exec django python manage.py import_stations your_file.csv

Expected CSV format:
StationNumber,StationType,MeasurementStartDate,MeasurementEndDate,Number ofSamples,StationStatus
ST001,River Monitoring,2023-01-01,2024-12-31,150,Active
ST002,Lake Monitoring,2023-02-15,2024-11-30,89,Active
...

Date formats supported:
- YYYY-MM-DD (e.g., 2023-01-01)
- DD/MM/YYYY (e.g., 01/01/2023)
"""

import os

# Update this to your CSV filename
YOUR_CSV_FILE = "NIWIS_WQMN_19-Jul-2025.csv"  # Change this to your actual filename

def check_file_exists():
    """Check if the CSV file exists and provide instructions."""
    if os.path.exists(YOUR_CSV_FILE):
        print(f"✅ Found CSV file: {YOUR_CSV_FILE}")
        print(f"Run: docker compose exec django python manage.py import_stations {YOUR_CSV_FILE}")
    else:
        print(f"❌ CSV file not found: {YOUR_CSV_FILE}")
        print("Please:")
        print("1. Place your CSV file in the project root directory")
        print("2. Update the YOUR_CSV_FILE variable in this script")
        print("3. Ensure your CSV has the correct headers:")
        print("   StationNumber,StationType,MeasurementStartDate,MeasurementEndDate,Number ofSamples,StationStatus")

if __name__ == "__main__":
    check_file_exists() 