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
        
        // Try to load from API first (if Flask server is running)
        let response;
        try {
            response = await fetch('http://localhost:5000/api/stations');
            if (response.ok) {
                stations = await response.json();
                console.log('Loaded data from Flask API server');
            } else {
                throw new Error('API not available');
            }
        } catch (apiError) {
            console.log('Flask API not available, trying direct JSON file...');
            // Fallback to direct JSON file
            response = await fetch('water_quality_data.json');
            stations = await response.json();
            console.log('Loaded data directly from JSON file');
        }
        
        filteredStations = [...stations];
        isDataLoaded = true;
        console.log('Loaded', stations.length, 'water quality stations from NIWIS');
        console.log('Data source: September 18, 2025 - Prescriptive Data Analytics');
        
        // Update province filter options dynamically
        updateProvinceFilter();
        
        return stations;
    } catch (error) {
        console.error('Error loading water quality data:', error);
        // Show helpful error message to user
        document.getElementById('stationInfo').innerHTML = `
            <div style="color: red; padding: 20px; background: #fff5f5; border-radius: 5px;">
                <h3>Data Loading Error</h3>
                <p>Unable to load water quality data. This could be due to:</p>
                <ul>
                    <li><strong>CORS restrictions</strong> - Try running the Flask server: <code>python backend.py</code></li>
                    <li><strong>Missing JSON file</strong> - Ensure water_quality_data.json is in the project directory</li>
                    <li><strong>File access issues</strong> - Check file permissions</li>
                </ul>
                <p><strong>Solution:</strong> Run <code>python backend.py</code> in the terminal, then refresh this page.</p>
            </div>
        `;
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
    const chartType = document.getElementById('chartTypeSelect').value;
    
    if (chart) {
        chart.destroy();
    }
    
    let chartData, chartOptions;
    
    switch (chartType) {
        case 'province':
            chartData = createProvinceChart(selectedParameter, parameterLabel);
            break;
        case 'status':
            chartData = createStatusChart(selectedParameter, parameterLabel);
            break;
        case 'stationType':
            chartData = createStationTypeChart(selectedParameter, parameterLabel);
            break;
        case 'distribution':
            chartData = createDistributionChart(selectedParameter, parameterLabel);
            break;
        default:
            chartData = createProvinceChart(selectedParameter, parameterLabel);
    }
    
    chart = new Chart(ctx, chartData);
}

// Create chart by province averages
function createProvinceChart(parameter, parameterLabel) {
    const provinceData = {};
    
    filteredStations.forEach(station => {
        const province = station.province;
        const value = station[parameter];
        
        if (!provinceData[province]) {
            provinceData[province] = [];
        }
        provinceData[province].push(value);
    });
    
    const provinces = Object.keys(provinceData);
    const labels = provinces.length > 0 ? provinces : ['Overall'];
    const data = provinces.length > 0 ? 
        provinces.map(province => {
            const values = provinceData[province];
            return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(2);
        }) : [0];
    
    const colors = [
        '#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0',
        '#00BCD4', '#8BC34A', '#FF5722', '#795548', '#607D8B'
    ];
    
    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Average ${parameterLabel}`,
                data: data,
                backgroundColor: labels.map((_, index) => colors[index % colors.length]),
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: parameter !== 'ph',
                    title: { display: true, text: `Average ${parameterLabel}` }
                },
                x: { ticks: { maxRotation: 45, minRotation: 0 } }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Average ${parameterLabel} by Province (${filteredStations.length} stations)`,
                    font: { size: 16 }
                },
                legend: { display: true, position: 'top' }
            }
        }
    };
}

// Create chart by quality status
function createStatusChart(parameter, parameterLabel) {
    const statusData = { 'Good': [], 'Fair': [], 'Poor': [] };
    
    filteredStations.forEach(station => {
        const status = station.quality_status;
        const value = station[parameter];
        if (statusData[status]) {
            statusData[status].push(value);
        }
    });
    
    const labels = Object.keys(statusData);
    const data = labels.map(status => {
        const values = statusData[status];
        return values.length > 0 ? (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(2) : 0;
    });
    
    const colors = ['#28a745', '#ffc107', '#dc3545'];
    
    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Average ${parameterLabel}`,
                data: data,
                backgroundColor: colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: parameter !== 'ph',
                    title: { display: true, text: `Average ${parameterLabel}` }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Average ${parameterLabel} by Quality Status (${filteredStations.length} stations)`,
                    font: { size: 16 }
                },
                legend: { display: true, position: 'top' }
            }
        }
    };
}

// Create chart by station type
function createStationTypeChart(parameter, parameterLabel) {
    const typeData = {};
    
    filteredStations.forEach(station => {
        const type = station.station_type;
        const value = station[parameter];
        
        if (!typeData[type]) {
            typeData[type] = [];
        }
        typeData[type].push(value);
    });
    
    const types = Object.keys(typeData);
    const labels = types.length > 0 ? types : ['Unknown'];
    const data = types.length > 0 ? 
        types.map(type => {
            const values = typeData[type];
            return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(2);
        }) : [0];
    
    const colors = [
        '#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0',
        '#00BCD4', '#8BC34A', '#FF5722', '#795548', '#607D8B'
    ];
    
    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Average ${parameterLabel}`,
                data: data,
                backgroundColor: labels.map((_, index) => colors[index % colors.length]),
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: parameter !== 'ph',
                    title: { display: true, text: `Average ${parameterLabel}` }
                },
                x: { ticks: { maxRotation: 45, minRotation: 0 } }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Average ${parameterLabel} by Station Type (${filteredStations.length} stations)`,
                    font: { size: 16 }
                },
                legend: { display: true, position: 'top' }
            }
        }
    };
}

// Create value distribution chart
function createDistributionChart(parameter, parameterLabel) {
    const values = filteredStations.map(station => station[parameter]);
    
    // Create ranges for distribution
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min;
    const numBins = 10;
    const binSize = range / numBins;
    
    const bins = Array(numBins).fill(0);
    const binLabels = [];
    
    for (let i = 0; i < numBins; i++) {
        const binStart = min + (i * binSize);
        const binEnd = min + ((i + 1) * binSize);
        binLabels.push(`${binStart.toFixed(1)}-${binEnd.toFixed(1)}`);
        
        values.forEach(value => {
            if (value >= binStart && value < binEnd) {
                bins[i]++;
            }
        });
    }
    
    return {
        type: 'bar',
        data: {
            labels: binLabels,
            datasets: [{
                label: `Number of Stations`,
                data: bins,
                backgroundColor: '#2196F3',
                borderColor: '#1976D2',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Number of Stations' }
                },
                x: {
                    title: { display: true, text: parameterLabel },
                    ticks: { maxRotation: 45, minRotation: 0 }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `${parameterLabel} Distribution (${filteredStations.length} stations)`,
                    font: { size: 16 }
                },
                legend: { display: true, position: 'top' }
            }
        }
    };
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
    document.getElementById('chartTypeSelect').addEventListener('change', createChart);
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