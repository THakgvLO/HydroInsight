# HydroInsight 🌊

**South African Water Quality Monitoring Platform**

HydroInsight is a comprehensive web application that provides real-time visualization of South African water quality monitoring stations through interactive maps and data analytics. Built for the public, environmental scientists, researchers, and water management professionals across South Africa's nine provinces.

![HydroInsight Demo](https://img.shields.io/badge/Status-Live-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)

## 🌟 Features

- **🇿🇦 South African Focus**: Monitoring stations across all 9 provinces
- **Interactive Map Visualization**: Real-time display using Leaflet.js with accurate SA coordinates
- **Advanced Filtering**: Filter by province, water quality status, or specific parameters
- **Multi-Parameter Analytics**: pH, turbidity, temperature, dissolved oxygen, and conductivity
- **Status-Based Color Coding**: Visual indicators (Good/Fair/Poor) for quick assessment
- **Responsive Design**: Modern, clean UI optimized for all devices
- **RESTful API**: Comprehensive Flask backend with multiple endpoints
- **Real-time Statistics**: Live dashboard with key metrics and averages

## 🗺️ Monitoring Stations

The application monitors water quality stations across South Africa:

| Station | Province | Waterbody | pH | Temperature | Status | Last Sample |
|---------|----------|-----------|----|-----------|---------|-----------| 
| Cape Town - V&A Waterfront | Western Cape | Atlantic Ocean | 8.1 | 16.5°C | Good | 2024-12-15 |
| Johannesburg - Vaal River | Gauteng | Vaal River | 7.4 | 22.1°C | Fair | 2024-12-14 |
| Durban - Umgeni River | KwaZulu-Natal | Umgeni River | 7.8 | 24.3°C | Good | 2024-12-13 |
| Bloemfontein - Modder River | Free State | Modder River | 7.1 | 20.7°C | Fair | 2024-12-12 |
| Port Elizabeth - Sundays River | Eastern Cape | Sundays River | 7.6 | 18.9°C | Good | 2024-12-11 |

## 🚀 Getting Started

Clone the repository and open `index.html` in your browser to see the application in action.

## 🛠️ Tech Stack

### Frontend
- **HTML5** - Semantic markup structure
- **CSS3** - Modern styling with responsive design
- **JavaScript (ES6+)** - Interactive functionality
- **Leaflet.js** - Interactive mapping with OpenStreetMap tiles
- **Chart.js** - Data visualization and analytics

### Backend
- **Python 3.8+** - Server-side logic
- **Flask 2.3.3** - Lightweight web framework
- **RESTful API** - JSON endpoints for data access

### Development
- **Git** - Version control and collaboration
- **Local Development** - No build process required

## 📁 Project Structure

```
HydroInsight/
├── index.html              # Main application page
├── style.css               # Modern CSS styling with responsive design
├── script.js               # Frontend JavaScript with interactive features
├── water_quality_data.json # South African water quality monitoring data
├── backend.py              # Flask API server with multiple endpoints
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🏃‍♂️ Quick Start

### Option 1: Frontend Only (Recommended for GitHub Pages)
1. Clone the repository:
   ```bash
   git clone https://github.com/THakgvLO/HydroInsight.git
   cd HydroInsight
   ```
2. Open `index.html` in your web browser
3. The application works with embedded sample data

### Option 2: Full Stack (Local Development)
1. Clone and navigate to the repository:
   ```bash
   git clone https://github.com/THakgvLO/HydroInsight.git
   cd HydroInsight
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask backend:
   ```bash
   python backend.py
   ```
4. Open `index.html` in your browser or visit `http://localhost:5000`

## 📊 API Endpoints

The Flask backend provides the following RESTful endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/api/stations` | GET | Retrieve all water quality stations |
| `/api/stations/<id>` | GET | Retrieve specific station by ID |

### Example API Response
```json
{
  "id": 1,
  "name": "Riverbank Station",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "ph": 7.2,
  "turbidity": 3.1,
  "last_sample": "2024-07-20"
}
```

## 🎯 Use Cases

- **Environmental Monitoring**: Track water quality across multiple locations
- **Research & Analytics**: Visualize trends in pH levels and turbidity
- **Public Health**: Monitor drinking water sources
- **Academic Projects**: Educational tool for GIS and environmental science
- **Municipal Management**: Support water infrastructure decisions

## 🔧 Development

### Adding New Stations
To add new monitoring stations, update the `stations` array in `script.js`:

```javascript
const stations = [
    {
        id: 4,
        name: "New Station Name",
        latitude: -1.2500,
        longitude: 36.9000,
        ph: 7.0,
        turbidity: 2.0,
        last_sample: "2024-07-21"
    }
    // ... existing stations
];
```

## 📈 Future Enhancements

- [ ] Real-time data integration from IoT sensors
- [ ] Historical data trends and time-series analysis
- [ ] Export functionality for reports
- [ ] Mobile application development
- [ ] User authentication and data management
- [ ] Integration with external water quality databases

## 🐛 Issues & Support

Found a bug or have a feature request? Please [open an issue](https://github.com/THakgvLO/HydroInsight/issues) on GitHub.

## 👨‍💻 Author

**Thakgalo Sehlola**
- GitHub: [@THakgvLO](https://github.com/THakgvLO)
- LinkedIn: [thakgalo-sehlola](https://linkedin.com/in/thakgalo-sehlola)
---
