// HydroInsight - South African Water Quality Monitoring
// Main JavaScript Application - NIWIS Data from September 18, 2025

let stations = [];
let filteredStations = [];
let map;
let chart;
let markers = [];
let isDataLoaded = false;
let maxMarkersToShow = 1000; // Limit markers for performance

// Load water quality data
async function loadWaterQualityData() {
    try {
        console.log('Loading NIWIS Water Quality Monitoring Network data...');
        const response = await fetch('water_quality_data.json');
        stations = await response.json();
        filteredStations = [...stations];
        isDataLoaded = true;
        console.log('Loaded', stations.length, 'water quality stations from NIWIS');
        console.log('Data source: September 18, 2025 - Prescriptive Data Analytics');
        
        // Update province filter options dynamically
        updateProvinceFilter();
        
        return stations;
    } catch (error) {
        console.error('Error loading water quality data:', error);
        // Show error message to user
        document.getElementById('stationInfo').innerHTML = 
            '<div style="color: red;">Error loading water quality data. Please ensure water_quality_data.json is available.</div>';
        return [];
    }
}

// Update province filter options based on loaded data
function updateProvinceFilter() {
    const provinceFilter = document.getElementById('stationFilter');
    const currentValue = provinceFilter.value;
    
    // Clear existing options except "All Provinces"
    provinceFilter.innerHTML = '<option value="all">All Provinces</option>';
    
    // Get unique provinces from data
    const provinces = [...new Set(stations.map(s => s.province))].sort();
    
    provinces.forEach(province => {
        const option = document.createElement('option');
        option.value = province;
        option.textContent = province;
        provinceFilter.appendChild(option);
    });
    
    // Restore previous selection if it still exists
    if (provinces.includes(currentValue)) {
        provinceFilter.value = currentValue;
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
    
    // Limit markers for performance
    const stationsToShow = filteredStations.slice(0, maxMarkersToShow);
    
    console.log(`Showing ${stationsToShow.length} markers (filtered from ${filteredStations.length} stations)`);
    
    // Add markers for filtered stations
    stationsToShow.forEach(station => {
        const markerColor = getStatusColor(station.quality_status);
        const marker = L.circleMarker([station.latitude, station.longitude], {
            radius: 6,
            fillColor: markerColor,
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        }).addTo(map);
        
        marker.bindPopup(createPopupContent(station));
        marker.on('click', () => showStationDetails(station));
        markers.push(marker);
    });
    
    // Show warning if markers are limited
    if (filteredStations.length > maxMarkersToShow) {
        const warning = L.control({position: 'bottomleft'});
        warning.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'marker-warning');
            div.innerHTML = `<div style="background: rgba(255,255,255,0.9); padding: 5px; border-radius: 3px; font-size: 12px;">
                Showing ${maxMarkersToShow} of ${filteredStations.length} stations. Use filters to narrow results.
            </div>`;
            return div;
        };
        warning.addTo(map);
    }
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
            <span class="popup-label">Station Number:</span>
            <span class="popup-value">${station.station_number}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Type:</span>
            <span class="popup-value">${station.station_type}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Province:</span>
            <span class="popup-value">${station.province}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Status:</span>
            <span class="popup-value">${station.station_status}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Quality:</span>
            <span class="popup-value status-${station.quality_status.toLowerCase()}">${station.quality_status}</span>
        </div>
        <div class="popup-parameter">
            <span class="popup-label">Samples:</span>
            <span class="popup-value">${station.number_of_samples}</span>
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
                <strong>Station Number:</strong> ${station.station_number}<br>
                <strong>Type:</strong> ${station.station_type}<br>
                <strong>Province:</strong> ${station.province}<br>
                <strong>Coordinates:</strong> ${station.latitude.toFixed(4)}, ${station.longitude.toFixed(4)}<br>
                <strong>Station Status:</strong> ${station.station_status}<br>
                <strong>Quality Status:</strong> <span class="status-${station.quality_status.toLowerCase()}">${station.quality_status}</span><br>
                <strong>Samples:</strong> ${station.number_of_samples}
            </div>
            <div>
                <strong>pH Level:</strong> ${station.ph}<br>
                <strong>Temperature:</strong> ${station.temperature}°C<br>
                <strong>Turbidity:</strong> ${station.turbidity} NTU<br>
                <strong>Dissolved Oxygen:</strong> ${station.dissolved_oxygen} mg/L<br>
                <strong>Conductivity:</strong> ${station.conductivity} μS/cm<br>
                <strong>Total Dissolved Solids:</strong> ${station.total_dissolved_solids} mg/L<br>
                <strong>Nitrate:</strong> ${station.nitrate} mg/L<br>
                <strong>Phosphate:</strong> ${station.phosphate} mg/L<br>
                <strong>Last Sample:</strong> ${station.last_sample}
            </div>
        </div>
        <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; font-size: 0.9em; color: #6c757d;">
            <strong>Data Source:</strong> ${station.data_source}<br>
            <strong>Data Date:</strong> ${station.data_date} | <strong>Analytics Type:</strong> ${station.analytics_type}
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
    const activeStations = filteredStations.filter(s => s.station_status === 'Active').length;
    const goodStations = filteredStations.filter(s => s.quality_status === 'Good').length;
    const fairStations = filteredStations.filter(s => s.quality_status === 'Fair').length;
    const poorStations = filteredStations.filter(s => s.quality_status === 'Poor').length;
    
    const avgPh = totalStations > 0 ? (filteredStations.reduce((sum, s) => sum + s.ph, 0) / totalStations).toFixed(1) : '0';
    const avgTemp = totalStations > 0 ? (filteredStations.reduce((sum, s) => sum + s.temperature, 0) / totalStations).toFixed(1) : '0';
    const avgTurbidity = totalStations > 0 ? (filteredStations.reduce((sum, s) => sum + s.turbidity, 0) / totalStations).toFixed(1) : '0';
    
    document.getElementById('totalStations').textContent = totalStations.toLocaleString();
    document.getElementById('activeStations').textContent = activeStations.toLocaleString();
    document.getElementById('goodStations').textContent = goodStations.toLocaleString();
    document.getElementById('fairStations').textContent = fairStations.toLocaleString();
    document.getElementById('poorStations').textContent = poorStations.toLocaleString();
    document.getElementById('avgPh').textContent = avgPh;
    document.getElementById('avgTemp').textContent = avgTemp + '°C';
    document.getElementById('avgTurbidity').textContent = avgTurbidity + ' NTU';
}

// Filter stations based on selected criteria
function filterStations() {
    const provinceFilter = document.getElementById('stationFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const stationTypeFilter = document.getElementById('stationTypeFilter').value;
    
    filteredStations = stations.filter(station => {
        const provinceMatch = provinceFilter === 'all' || station.province === provinceFilter;
        const statusMatch = statusFilter === 'all' || station.quality_status === statusFilter;
        const typeMatch = stationTypeFilter === 'all' || station.station_type === stationTypeFilter;
        return provinceMatch && statusMatch && typeMatch;
    });
    
    console.log(`Filtered to ${filteredStations.length} stations`);
    updateMapMarkers();
    createChart();
    updateStatistics();
}

// Event listeners
function setupEventListeners() {
    document.getElementById('stationFilter').addEventListener('change', filterStations);
    document.getElementById('statusFilter').addEventListener('change', filterStations);
    document.getElementById('stationTypeFilter').addEventListener('change', filterStations);
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