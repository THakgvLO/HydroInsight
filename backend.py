# Simple Python Backend for Water Quality Stations
# This is a basic Flask server that serves the station data

from flask import Flask, jsonify
import json

app = Flask(__name__)

# Sample water quality stations data
STATIONS_DATA = [
    {
        "id": 1,
        "name": "Riverbank Station",
        "latitude": -1.2921,
        "longitude": 36.8219,
        "ph": 7.2,
        "turbidity": 3.1,
        "last_sample": "2024-07-20"
    },
    {
        "id": 2,
        "name": "Lakeside Station",
        "latitude": -1.3000,
        "longitude": 36.8000,
        "ph": 6.8,
        "turbidity": 2.5,
        "last_sample": "2024-07-19"
    },
    {
        "id": 3,
        "name": "Upland Station",
        "latitude": -1.3100,
        "longitude": 36.8500,
        "ph": 7.5,
        "turbidity": 1.8,
        "last_sample": "2024-07-18"
    }
]

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

@app.route('/', methods=['GET'])
def home():
    """Simple home endpoint"""
    return jsonify({
        'message': 'Water Quality Stations API',
        'endpoints': {
            '/api/stations': 'Get all stations',
            '/api/stations/<id>': 'Get specific station'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)