# 📋 Water Quality Station Import Guide

## 🎯 **How to Import Your Own CSV File**

### **Step 1: Prepare Your CSV File**

**Option A: Standard Format**
Your CSV file should have these exact headers:
```csv
StationNumber,StationType,MeasurementStartDate,MeasurementEndDate,Number ofSamples,StationStatus
```

**Option B: DWS Surface Water Monitoring Network Format** ✅ **RECOMMENDED**
For official DWS data, use these headers:
```csv
Station,Name,Type,Open,Closed,Start Date,End Date,% Reliable Data
```

**Example:**
```csv
ST001,River Monitoring,2023-01-01,2024-12-31,150,Active
ST002,Lake Monitoring,2023-02-15,2024-11-30,89,Active
ST003,Reservoir Monitoring,2023-03-01,2024-10-15,67,Inactive
```

### **Step 2: Place Your CSV File**

1. Copy your CSV file to the project root directory
2. Update the filename in `import_your_csv.py`:
   ```python
   YOUR_CSV_FILE = "your_actual_filename.csv"
   ```

### **Step 3: Import with Automatic Coordinates**

**Option A: DWS Import (Recommended for DWS data)**
```bash
docker compose exec django python manage.py import_dws_stations your_file.csv --assign-coordinates
```

**Option B: Enhanced Import (For standard format)**
```bash
docker compose exec django python manage.py import_stations_enhanced your_file.csv --assign-coordinates
```

**Option C: Basic Import**
```bash
docker compose exec django python manage.py import_stations your_file.csv
```

### **Step 4: Update Coordinates (if needed)**

If you imported without coordinates or want to spread stations out:
```bash
docker compose exec django python manage.py update_coordinates
```

---

## 🗺️ **Coordinate Assignment System**

### **Automatic Coordinate Assignment**

The system automatically assigns coordinates based on station type:

| Station Type | Assigned Locations |
|--------------|-------------------|
| River | Johannesburg, Cape Town, Durban, Pretoria, Bloemfontein |
| Lake | Johannesburg, Cape Town, Durban |
| Reservoir | Johannesburg, Cape Town, Durban |
| Stream | Johannesburg, Cape Town, Durban |
| Coastal | Cape Town, Durban, Port Elizabeth |
| Well | Johannesburg, Cape Town, Durban |
| Spring | Johannesburg, Cape Town, Durban |
| Estuary | Cape Town, Durban |
| Pond | Johannesburg, Cape Town, Durban |
| Canal | Johannesburg, Cape Town, Durban |

### **Customizing Coordinates**

To customize coordinates for your specific locations:

1. Edit `watergis/management/commands/import_stations_enhanced.py`
2. Update the `coordinates_map` in the `get_default_coordinates` method
3. Add your specific coordinates for each station type

---

## 📊 **Date Format Support**

The import system supports these date formats:
- `YYYY-MM-DD` (e.g., 2023-01-01)
- `DD/MM/YYYY` (e.g., 01/01/2023)
- `MM/DD/YYYY` (e.g., 01/01/2023 - US format)
- `DD-MM-YYYY` (e.g., 01-01-2023)
- `YYYY/MM/DD` (e.g., 2023/01/01)
- `DD/MM/YY` (e.g., 01/01/23)
- `MM/DD/YY` (e.g., 01/01/23 - US format)
- `DD-MMM-YYYY` (e.g., 30-Nov-2007)
- `DD-MMMM-YYYY` (e.g., 18-September-1995)

**Month abbreviations supported:**
- Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep/Sept, Oct, Nov, Dec
- January, February, March, April, May, June, July, August, September, October, November, December

---

## 🔧 **Available Commands**

```bash
# Import DWS stations (Recommended for DWS data)
docker compose exec django python manage.py import_dws_stations your_file.csv --assign-coordinates

# Import stations with automatic coordinates (Standard format)
docker compose exec django python manage.py import_stations_enhanced your_file.csv --assign-coordinates

# Import stations without coordinates
docker compose exec django python manage.py import_stations your_file.csv

# Update coordinates for existing stations
docker compose exec django python manage.py update_coordinates

# Add sample water quality data
docker compose exec django python manage.py add_sample_data

# Clear all sample data
docker compose exec django python manage.py clear_sample_data --confirm

# Check your CSV file
python import_your_csv.py

# Import DWA water quality data (Excel/CSV)
docker compose exec django python manage.py import_water_quality_data your_file.xlsx --file-type excel --create-stations
```

---

## 🎯 **Quick Start for Your Data**

1. **Place your CSV file** in the project root
2. **Update** `import_your_csv.py` with your filename
3. **Run**: `docker compose exec django python manage.py import_stations_enhanced your_file.csv --assign-coordinates`
4. **Add sample data**: `docker compose exec django python manage.py add_sample_data`
5. **View dashboard**: http://localhost:8000/

---

## 🚨 **Troubleshooting**

### **CSV File Not Found**
- Ensure your CSV file is in the project root directory
- Check the filename spelling in `import_your_csv.py`

### **No Stations on Map**
- Run: `docker compose exec django python manage.py update_coordinates`
- Check that stations have non-zero coordinates

### **Import Errors**
- Verify CSV headers match exactly
- Check date formats
- Ensure StationNumber is not empty

---

## 📈 **After Import**

1. **View stations** in Django admin: http://localhost:8000/admin/
2. **Check dashboard**: http://localhost:8000/
3. **Add sample data** for visualization
4. **Customize coordinates** if needed

---

**Need help?** Check the Django admin interface to see your imported data and verify coordinates are assigned correctly. 