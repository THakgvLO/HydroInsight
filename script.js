// HydroInsight - South African Water Quality Monitoring
// Main JavaScript Application

let stations = [];
let filteredStations = [];
let map;
let chart;
let markers = [];

// Load water quality data
async function loadWaterQualityData() {
    try {
        const response = await fetch('water_quality_data.json');
        stations = await response.json();
        filteredStations = [...stations];
        console.log('Loaded', stations.length, 'water quality stations');
        return stations;
    } catch (error) {
        console.error('Error loading water quality data:', error);
        // Fallback to sample data if JSON file is not available
        stations = [
            {
                id: 1,
                name: "Cape Town - V&A Waterfront",
                latitude: -33.9083,
                longitude: 18.4216,
                province: "Western Cape",
                waterbody: "Atlantic Ocean",
                ph: 8.1,
                turbidity: 2.3,
                temperature: 16.5,
                dissolved_oxygen: 7.8,
                conductivity: 1250,
                last_sample: "2024-12-15",
                status: "Good"
            }
        ];
        filteredStations = [...stations];
        return stations;
    }
}

// Initialize the map
function initMap() {
    // Create map centered on South Africa
    map = L.map('map').setView([-29.0000, 24.0000], 5);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    updateMapMarkers();
}

// Update map markers based on filtered stations
function updateMapMarkers() {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Add markers for filtered stations
    filteredStations.forEach(station => {
        const markerColor = getStatusColor(station.status);
        const marker = L.circleMarker([station.latitude, station.longitude], {
            radius: 8,
            fillColor: markerColor,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
        
        marker.bindPopup(createPopupContent(station));
        marker.on('click', () => showStationDetails(station));
        markers.push(marker);
    });
}

// Get color based on status
function getStatusColor(status) {
    switch (status) {
        case 'Good': return '#28a745';
        case 'Fair': return '#ffc107';
        case 'Poor': return '#dc3545';
        default: return '#6c757d';
    }
}

// Create popup content
function createPopupContent(station) {
    return `
        <div class="popup-header">${station.name}</div>
        <div class="popup-parameter">
            <span class="popup-label">Province:</span>
            <span class="popup-value">${station.province}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Waterbody:</span>
            <span class="popup-value">${station.waterbody}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">pH:</span>
            <span class="popup-value">${station.ph}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Temperature:</span>
            <span class="popup-value">${station.temperature}°C</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Status:</span>
            <span class="popup-value status-${station.status.toLowerCase()}">${station.status}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Last Sample:</span>
            <span class="popup-value">${station.last_sample}</span>
        </div>
    `;
}

// Show station details
function showStationDetails(station) {
    const stationInfo = document.getElementById('stationInfo');
    stationInfo.innerHTML = `
        <h3>${station.name}</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
            <div>
                <strong>Location:</strong> ${station.province}<br>
                <strong>Waterbody:</strong> ${station.waterbody}<br>
                <strong>Coordinates:</strong> ${station.latitude.toFixed(4)}, ${station.longitude.toFixed(4)}<br>
                <strong>Status:</strong> <span class="status-${station.status.toLowerCase()}">${station.status}</span>
            </div>
            <div>
                <strong>pH Level:</strong> ${station.ph}<br>
                <strong>Temperature:</strong> ${station.temperature}°C<br>
                <strong>Turbidity:</strong> ${station.turbidity} NTU<br>
                <strong>Dissolved Oxygen:</strong> ${station.dissolved_oxygen} mg/L<br>
                <strong>Conductivity:</strong> ${station.conductivity} μS/cm<br>
                <strong>Last Sample:</strong> ${station.last_sample}
            </div>
        </div>
    `;
}

// Create/update chart
function createChart() {
    const ctx = document.getElementById('chart').getContext('2d');
    const selectedParameter = document.getElementById('parameterSelect').value;
    const parameterLabel = document.getElementById('parameterSelect').selectedOptions[0].text;
    
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: filteredStations.map(station => station.name.split(' - ')[0]), // Use city name only
            datasets: [{
                label: parameterLabel,
                data: filteredStations.map(station => station[selectedParameter]),
                backgroundColor: filteredStations.map(station => 
                    selectedParameter === 'status' ? getStatusColor(station.status) : '#2196F3'
                ),
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: selectedParameter !== 'ph',
                    title: {
                        display: true,
                        text: parameterLabel
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 0
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Water Quality: ${parameterLabel}`,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

// Update statistics
function updateStatistics() {
    const totalStations = filteredStations.length;
    const goodStations = filteredStations.filter(s => s.status === 'Good').length;
    const avgPh = (filteredStations.reduce((sum, s) => sum + s.ph, 0) / totalStations).toFixed(1);
    const avgTemp = (filteredStations.reduce((sum, s) => sum + s.temperature, 0) / totalStations).toFixed(1);
    
    document.getElementById('totalStations').textContent = totalStations;
    document.getElementById('goodStations').textContent = goodStations;
    document.getElementById('avgPh').textContent = avgPh;
    document.getElementById('avgTemp').textContent = avgTemp + '°C';
}

// Filter stations based on selected criteria
function filterStations() {
    const provinceFilter = document.getElementById('stationFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    
    filteredStations = stations.filter(station => {
        const provinceMatch = provinceFilter === 'all' || station.province === provinceFilter;
        const statusMatch = statusFilter === 'all' || station.status === statusFilter;
        return provinceMatch && statusMatch;
    });
    
    updateMapMarkers();
    createChart();
    updateStatistics();
}

// Event listeners
function setupEventListeners() {
    document.getElementById('stationFilter').addEventListener('change', filterStations);
    document.getElementById('statusFilter').addEventListener('change', filterStations);
    document.getElementById('parameterSelect').addEventListener('change', createChart);
}

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Initializing HydroInsight...');
    
    // Load data first
    await loadWaterQualityData();
    
    // Initialize components
    initMap();
    createChart();
    updateStatistics();
    setupEventListeners();
    
    console.log('HydroInsight initialized successfully');
});