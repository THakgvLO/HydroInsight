# 🌊 Water Quality Monitoring System Guide

## 📊 **Water Quality Categories**

### **Primary Categories (Recommended for your system):**

**1. Water Quality Monitoring Network** ✅ **RECOMMENDED**
- **Best for**: General water quality monitoring
- **Includes**: pH, turbidity, dissolved oxygen, temperature
- **Coverage**: Surface water bodies, rivers, lakes, reservoirs
- **Data**: Regular monitoring data with trends

**2. Surface Water Monitoring Network** ✅ **RECOMMENDED**
- **Best for**: Rivers, streams, lakes, dams
- **Includes**: Physical, chemical, biological parameters
- **Coverage**: All surface water bodies
- **Data**: Comprehensive water quality data

**3. Groundwater Quality** ✅ **RECOMMENDED**
- **Best for**: Wells, springs, boreholes
- **Includes**: Chemical composition, contamination levels
- **Coverage**: Underground water sources
- **Data**: Groundwater quality parameters

### **Secondary Categories (Specialized):**

**4. Drinking Water Quality Compliance**
- **Best for**: Municipal water supply monitoring
- **Focus**: Compliance with drinking water standards
- **Data**: Regulatory compliance data

**5. Resource Water Quality Objectives**
- **Best for**: Environmental protection monitoring
- **Focus**: Meeting environmental objectives
- **Data**: Ecological health indicators

**6. Waste Water Quality Compliance**
- **Best for**: Treatment plant monitoring
- **Focus**: Effluent quality standards
- **Data**: Treatment performance data

---

## 📈 **Data Sources for Water Quality Parameters**

### **Recommended Data Sources:**

**1. Department of Water and Sanitation (DWS)**
- **Website**: https://www.dws.gov.za/
- **Data**: National water quality monitoring data
- **Parameters**: pH, turbidity, dissolved oxygen, temperature
- **Format**: CSV, Excel, API

**2. South African Weather Service (SAWS)**
- **Website**: https://www.weathersa.co.za/
- **Data**: Water temperature, weather-related parameters
- **Parameters**: Temperature, rainfall, humidity

**3. Municipal Water Departments**
- **Data**: Local water quality monitoring
- **Parameters**: All standard parameters
- **Access**: Contact local municipalities

**4. Research Institutions**
- **Universities**: UCT, Wits, Stellenbosch
- **Data**: Research-based water quality data
- **Parameters**: Comprehensive datasets

**5. Environmental Monitoring Networks**
- **SANParks**: National parks monitoring
- **CapeNature**: Western Cape monitoring
- **Data**: Protected area water quality

### **Alternative Data Sources:**

**6. International Databases**
- **GEMStat**: Global water quality database
- **WHO**: Water quality guidelines and data
- **UNEP**: Environmental data

**7. Citizen Science Platforms**
- **Freshwater Watch**: Community monitoring
- **Water Rangers**: Mobile app data collection

---

## 🔧 **System Configuration Recommendations**

### **For Your CSV Import:**

**Recommended Station Types:**
```csv
StationNumber,StationType,MeasurementStartDate,MeasurementEndDate,Number ofSamples,StationStatus
WQ001,Surface Water Monitoring,30-Nov-2007,18-Sept-2025,150,Active
WQ002,River Monitoring,15-Jan-2020,25-Dec-2025,89,Active
WQ003,Lake Monitoring,01-Mar-2018,31-Dec-2025,67,Active
WQ004,Reservoir Monitoring,10-Apr-2019,30-Jun-2025,234,Active
WQ005,Well Monitoring,05-May-2021,15-Aug-2025,45,Active
```

**Water Quality Parameters to Include:**
- **pH** (6.5-8.5 range)
- **Turbidity** (0-50 NTU)
- **Dissolved Oxygen** (4-12 mg/L)
- **Temperature** (10-30°C)
- **Conductivity** (100-800 μS/cm)
- **Total Dissolved Solids** (50-500 mg/L)

---

## 🗺️ **Coordinate Distribution**

### **South African Water Bodies:**

**Major Rivers:**
- Orange River: (20.0, -28.5)
- Vaal River: (27.8, -26.8)
- Limpopo River: (31.5, -24.0)
- Breede River: (20.0, -34.0)
- Umgeni River: (30.9, -29.7)

**Major Dams/Reservoirs:**
- Gariep Dam: (25.5, -30.5)
- Vanderkloof Dam: (24.7, -30.0)
- Vaal Dam: (28.1, -26.9)
- Theewaterskloof: (19.2, -34.1)
- Midmar Dam: (30.2, -29.5)

**Coastal Areas:**
- Cape Town Coast: (18.4, -33.9)
- Durban Coast: (31.0, -29.9)
- Port Elizabeth: (25.6, -33.7)
- East London: (27.9, -33.0)

---

## 📋 **Admin Organization Features**

### **Enhanced Filtering Options:**

**Water Samples Page:**
- **Filter by**: Station Type, Status, Date Range
- **Search by**: Station Name, Station Type
- **Sort by**: Date, Station, Parameters
- **Group by**: Station Type, Status, Date

**Available Filters:**
- Station Type (River, Lake, Reservoir, etc.)
- Station Status (Active, Inactive)
- Date Range (Last 7 days, 30 days, 90 days, Custom)
- Parameter Ranges (pH, Turbidity, etc.)

---

## 🚀 **Implementation Steps**

### **1. Clear Sample Data (Done)**
```bash
docker compose exec django python manage.py clear_sample_data --confirm
```

### **2. Import Your Data**
```bash
docker compose exec django python manage.py import_stations_enhanced your_file.csv --assign-coordinates
```

### **3. Add Water Quality Data**
- **Option A**: Import from CSV with sample data
- **Option B**: Use API to add data programmatically
- **Option C**: Manual entry through admin interface

### **4. Configure Dashboard**
- Set map center to South Africa
- Configure parameter ranges
- Set up alerts and notifications

---

## 📞 **Data Acquisition Contacts**

**Department of Water and Sanitation:**
- **Email**: info@dws.gov.za
- **Phone**: +27 12 336 7500
- **Data Request**: https://www.dws.gov.za/iwqs/

**Municipal Contacts:**
- **Cape Town**: water@capetown.gov.za
- **Johannesburg**: water@joburg.org.za
- **Durban**: water@durban.gov.za

**Research Institutions:**
- **CSIR**: water@csir.co.za
- **WRC**: info@wrc.org.za

---

## 🎯 **Next Steps**

1. **Choose your primary monitoring category** (Surface Water Monitoring recommended)
2. **Prepare your CSV file** with the recommended format
3. **Import your stations** using the enhanced import command
4. **Add water quality data** from your preferred source
5. **Configure the dashboard** for your specific needs

**Need help?** Check the Django admin interface for data management and the dashboard for visualization. 