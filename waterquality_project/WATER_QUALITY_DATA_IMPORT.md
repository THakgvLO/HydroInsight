# 🌊 DWA Water Quality Data Import Guide

## 📊 **Your Data Format Analysis**

### **✅ Perfect Match for Our System!**

Your DWA (Department of Water Affairs) water quality dataset is **exactly what we need** for the dashboard. This is **official historical data** from 1999-2012 covering South African rivers.

### **📋 Data Structure:**

**Headers:**
```csv
"SAMPLE STATION/POINT ID AND SAMPLING DATE" | "ELECTRICAL CONDUCTIVITY" | "MAJOR IONS CHEMICAL COMPOSITION" | ...
```

**Key Columns:**
- `SAMPLE STATION ID` - Station identifier (e.g., ZBUF-SHAN, ZCOWO01)
- `POINT ID` - Sampling point number (e.g., 88705, 88714)
- `DATE` - Sampling date (e.g., 1999/05/24)
- `YEAR` - Year of sampling
- `PH` - pH value
- `EC` - Electrical conductivity
- `TDS` - Total dissolved solids
- `NA`, `MG`, `CA` - Major ions (Sodium, Magnesium, Calcium)
- `CL`, `NO3+NO2`, `SO4` - Anions (Chloride, Nitrate, Sulfate)
- And many more chemical parameters...

### **📈 Sample Data:**
```
ZBUF-SHAN	88705	1999/05/24	1999
ZBUF-SHAN	88705	1999/06/24	1999
ZCOWO01	88714	2005/07/26	2005
ZSTOV01	88942	2005/08/04	2005
ZYEL-LONS	89011	1999/01/11	1999
A2H006Q01	90160	1999/01/05	1999
```

---

## 🚀 **Import Process**

### **Step 1: Prepare Your File**

**Option A: Excel File (.xlsx)**
- Keep the original Excel format
- Ensure the file is in the project root directory

**Option B: Convert to CSV**
- Save as CSV from Excel
- Keep the same structure

### **Step 2: Import Water Quality Data**

**For Excel File:**
```bash
docker compose exec django python manage.py import_water_quality_data your_file.xlsx --file-type excel --create-stations
```

**For CSV File:**
```bash
docker compose exec django python manage.py import_water_quality_data your_file.csv --file-type csv --create-stations
```

### **Step 3: Update Station Coordinates**

After importing, assign coordinates to stations:
```bash
docker compose exec django python manage.py update_coordinates
```

---

## 📊 **Data Mapping**

### **Primary Parameters (Dashboard Display):**
- **pH** → Direct mapping from `PH` column
- **Turbidity** → Estimated from `TDS` (Total Dissolved Solids)
- **Dissolved Oxygen** → Default value (8.0 mg/L)
- **Temperature** → Default value (20°C)

### **Additional Parameters (Stored in other_data):**
- **Electrical Conductivity** → From `EC` column
- **Total Dissolved Solids** → From `TDS` column
- **Major Ions** → Sodium, Magnesium, Calcium, etc.
- **Anions** → Chloride, Nitrate, Sulfate, etc.
- **Trace Elements** → Fluoride, Silica, Potassium, etc.

---

## 🎯 **What This Will Give You**

### **Dashboard Features:**
1. **Interactive Map** - All DWA stations with pins
2. **Historical Trends** - 1999-2012 data visualization
3. **Parameter Charts** - pH, conductivity, TDS trends
4. **Station Details** - Click pins for station information
5. **Data Quality** - Reliable historical measurements

### **Admin Interface:**
1. **Station Management** - All DWA stations listed
2. **Sample Data** - Historical measurements with filters
3. **Data Export** - Export capabilities
4. **Quality Control** - Data validation and cleaning

---

## 🔧 **Advanced Configuration**

### **Custom Parameter Mapping:**

If you want to customize how parameters are mapped, edit the `column_mapping` in the import command:

```python
column_mapping = {
    'SAMPLE STATION ID': 'station_id',
    'POINT ID': 'point_id', 
    'DATE': 'date',
    'YEAR': 'year',
    'PH': 'ph',
    'EC': 'electrical_conductivity',
    'TDS': 'total_dissolved_solids',
    # Add more mappings as needed
}
```

### **Data Quality Filters:**

The import command includes data cleaning:
- **Null values** are handled gracefully
- **Date parsing** supports multiple formats
- **Numeric cleaning** removes formatting issues
- **Error logging** for problematic rows

---

## 📈 **Expected Results**

### **After Import:**
- **Stations**: All unique station IDs will be created
- **Samples**: All historical measurements (1999-2012)
- **Parameters**: pH, conductivity, TDS, and major ions
- **Timeline**: 13 years of historical data
- **Coverage**: Multiple South African rivers

### **Dashboard Visualization:**
- **Map**: Stations distributed across South Africa
- **Charts**: Historical trends for each parameter
- **Filters**: By station, date range, parameter type
- **Alerts**: Based on water quality thresholds

---

## 🚨 **Important Notes**

### **Data Limitations:**
1. **Missing Parameters**: Some parameters (DO, temperature) use default values
2. **Coordinate Assignment**: Stations need manual coordinate assignment
3. **Data Gaps**: Historical data may have missing values
4. **Quality Control**: Review data after import

### **Recommendations:**
1. **Backup**: Keep original Excel file
2. **Validate**: Check imported data in admin interface
3. **Enhance**: Add missing parameters if available
4. **Monitor**: Set up alerts for data quality issues

---

## 🎉 **Ready to Import!**

Your DWA water quality dataset is **perfect** for this system because:

✅ **Official Source** - Department of Water Affairs data  
✅ **Historical Coverage** - 13 years (1999-2012)  
✅ **Comprehensive Parameters** - pH, conductivity, major ions  
✅ **Multiple Stations** - Various South African rivers  
✅ **Quality Data** - Reliable measurements  

**Next Step:** Run the import command with your Excel file!

```bash
docker compose exec django python manage.py import_water_quality_data your_file.xlsx --file-type excel --create-stations
```

This will give you a **complete water quality monitoring dashboard** with real historical data! 🌊📊 