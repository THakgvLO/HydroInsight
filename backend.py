# HydroInsight - South African Water Quality Monitoring API
# Flask backend server for water quality data

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load water quality data from JSON file
def load_stations_data():
    try:
        with open('water_quality_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback data if JSON file is not found
        return [
            {
                "id": 1,
                "name": "Cape Town - V&A Waterfront",
                "latitude": -33.9083,
                "longitude": 18.4216,
                "province": "Western Cape",
                "waterbody": "Atlantic Ocean",
                "ph": 8.1,
                "turbidity": 2.3,
                "temperature": 16.5,
                "dissolved_oxygen": 7.8,
                "conductivity": 1250,
                "last_sample": "2024-12-15",
                "status": "Good"
            }
        ]

STATIONS_DATA = load_stations_data()

@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Return all water quality stations"""
    return jsonify(STATIONS_DATA)

@app.route('/api/stations/<int:station_id>', methods=['GET'])
def get_station(station_id):
    """Return a specific station by ID"""
    station = next((s for s in STATIONS_DATA if s['id'] == station_id), None)
    if station:
        return jsonify(station)
    return jsonify({'error': 'Station not found'}), 404

@app.route('/api/stations/province/<province>', methods=['GET'])
def get_stations_by_province(province):
    """Return stations filtered by province"""
    filtered_stations = [s for s in STATIONS_DATA if s['province'] == province]
    return jsonify(filtered_stations)

@app.route('/api/stations/status/<status>', methods=['GET'])
def get_stations_by_status(status):
    """Return stations filtered by status"""
    filtered_stations = [s for s in STATIONS_DATA if s['status'] == status]
    return jsonify(filtered_stations)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Return basic statistics about the stations"""
    total_stations = len(STATIONS_DATA)
    good_stations = len([s for s in STATIONS_DATA if s['status'] == 'Good'])
    fair_stations = len([s for s in STATIONS_DATA if s['status'] == 'Fair'])
    poor_stations = len([s for s in STATIONS_DATA if s['status'] == 'Poor'])
    
    avg_ph = sum(s['ph'] for s in STATIONS_DATA) / total_stations
    avg_temperature = sum(s['temperature'] for s in STATIONS_DATA) / total_stations
    avg_turbidity = sum(s['turbidity'] for s in STATIONS_DATA) / total_stations
    
    return jsonify({
        'total_stations': total_stations,
        'status_distribution': {
            'good': good_stations,
            'fair': fair_stations,
            'poor': poor_stations
        },
        'averages': {
            'ph': round(avg_ph, 2),
            'temperature': round(avg_temperature, 2),
            'turbidity': round(avg_turbidity, 2)
        }
    })

@app.route('/api/provinces', methods=['GET'])
def get_provinces():
    """Return list of all provinces with stations"""
    provinces = list(set(s['province'] for s in STATIONS_DATA))
    return jsonify(sorted(provinces))

@app.route('/')
def home():
    """API information endpoint"""
    return jsonify({
        'message': 'HydroInsight - South African Water Quality Monitoring API',
        'version': '1.0.0',
        'endpoints': {
            '/api/stations': 'Get all stations',
            '/api/stations/<id>': 'Get specific station by ID',
            '/api/stations/province/<province>': 'Get stations by province',
            '/api/stations/status/<status>': 'Get stations by status',
            '/api/statistics': 'Get basic statistics',
            '/api/provinces': 'Get list of provinces'
        },
        'total_stations': len(STATIONS_DATA)
    })

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (HTML, CSS, JS)"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    print(f"HydroInsight API Server Starting...")
    print(f"Loaded {len(STATIONS_DATA)} water quality monitoring stations")
    print(f"Available provinces: {list(set(s['province'] for s in STATIONS_DATA))}")
    app.run(debug=True, host='0.0.0.0', port=5000)