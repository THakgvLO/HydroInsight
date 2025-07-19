// Enhanced Water Quality Dashboard
class WaterQualityDashboard {
    constructor() {
        this.map = null;
        this.charts = {};
        this.currentStation = null;
        this.dataAggregation = 'daily'; // daily, weekly, monthly
        this.init();
    }

    async init() {
        await this.initMap();
        await this.loadStations();
        this.initCharts();
        this.setupEventListeners();
    }

    async initMap() {
        // Initialize Leaflet map
        this.map = L.map('map').setView([-28.2, 25.7], 6); // South Africa center
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add custom CSS for better map styling
        const style = document.createElement('style');
        style.textContent = `
            .station-popup {
                max-width: 300px;
                font-family: Arial, sans-serif;
            }
            .station-popup h3 {
                margin: 0 0 10px 0;
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
            }
            .station-popup .metric {
                display: flex;
                justify-content: space-between;
                margin: 5px 0;
                padding: 3px 0;
            }
            .station-popup .metric-label {
                font-weight: bold;
                color: #34495e;
            }
            .station-popup .metric-value {
                color: #7f8c8d;
            }
            .station-popup .view-data-btn {
                background: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 10px;
                width: 100%;
            }
            .station-popup .view-data-btn:hover {
                background: #2980b9;
            }
        `;
        document.head.appendChild(style);
    }

    async loadStations() {
        try {
            const response = await fetch('/api/stations/');
            const stations = await response.json();
            
            // Clear existing markers
            this.map.eachLayer((layer) => {
                if (layer instanceof L.Marker) {
                    this.map.removeLayer(layer);
                }
            });

            // Add markers for each station
            stations.forEach(station => {
                if (station.location && station.location.coordinates) {
                    const [lng, lat] = station.location.coordinates;
                    
                    // Create custom icon based on station status
                    const icon = this.createStationIcon(station);
                    
                    const marker = L.marker([lat, lng], { icon })
                        .addTo(this.map)
                        .bindPopup(this.createStationPopup(station));
                    
                    // Store marker reference
                    marker.stationData = station;
                    
                    // Add click event
                    marker.on('click', () => {
                        this.selectStation(station);
                    });
                }
            });

            // Fit map to show all stations
            if (stations.length > 0) {
                const group = new L.featureGroup(stations.map(s => {
                    if (s.location && s.location.coordinates) {
                        const [lng, lat] = s.location.coordinates;
                        return L.marker([lat, lng]);
                    }
                }).filter(Boolean));
                this.map.fitBounds(group.getBounds().pad(0.1));
            }

        } catch (error) {
            console.error('Error loading stations:', error);
        }
    }

    createStationIcon(station) {
        // Create custom icon based on station status and sample count
        const sampleCount = station.number_of_samples || 0;
        let color = '#95a5a6'; // Default gray
        
        if (station.status === 'Active') {
            if (sampleCount > 1000) color = '#27ae60'; // Green for active with many samples
            else if (sampleCount > 100) color = '#f39c12'; // Orange for active with some samples
            else color = '#e74c3c'; // Red for active with few samples
        } else if (station.status === 'Inactive') {
            color = '#9b59b6'; // Purple for inactive
        } else {
            color = '#95a5a6'; // Gray for offline
        }

        return L.divIcon({
            className: 'custom-station-icon',
            html: `<div style="
                width: 12px; 
                height: 12px; 
                background-color: ${color}; 
                border: 2px solid white; 
                border-radius: 50%; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [12, 12],
            iconAnchor: [6, 6]
        });
    }

    createStationPopup(station) {
        const lastSample = station.last_sample_date || 'No data';
        const sampleCount = station.number_of_samples || 0;
        
        return `
            <div class="station-popup">
                <h3>${station.name}</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value">${station.status || 'Unknown'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Samples:</span>
                    <span class="metric-value">${sampleCount.toLocaleString()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Sample:</span>
                    <span class="metric-value">${lastSample}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Type:</span>
                    <span class="metric-value">${station.station_type || 'Unknown'}</span>
                </div>
                <button class="view-data-btn" onclick="dashboard.selectStation('${station.id}')">
                    View Data
                </button>
            </div>
        `;
    }

    async selectStation(stationId) {
        if (typeof stationId === 'string') {
            // Find station by ID
            const response = await fetch(`/api/stations/${stationId}/`);
            this.currentStation = await response.json();
        } else {
            this.currentStation = stationId;
        }

        if (this.currentStation) {
            this.updateStationInfo();
            await this.loadStationData();
        }
    }

    updateStationInfo() {
        const infoDiv = document.getElementById('station-info');
        if (infoDiv && this.currentStation) {
            infoDiv.innerHTML = `
                <h3>${this.currentStation.name}</h3>
                <p><strong>Status:</strong> ${this.currentStation.status || 'Unknown'}</p>
                <p><strong>Type:</strong> ${this.currentStation.station_type || 'Unknown'}</p>
                <p><strong>Total Samples:</strong> ${(this.currentStation.number_of_samples || 0).toLocaleString()}</p>
                <p><strong>Description:</strong> ${this.currentStation.description || 'No description available'}</p>
            `;
        }
    }

    async loadStationData() {
        if (!this.currentStation) return;

        try {
            const response = await fetch(`/api/stations/${this.currentStation.id}/samples/?limit=1000`);
            const samples = await response.json();
            
            if (samples.length > 0) {
                this.updateCharts(samples);
            } else {
                this.showNoDataMessage();
            }
        } catch (error) {
            console.error('Error loading station data:', error);
            this.showNoDataMessage();
        }
    }

    initCharts() {
        // Initialize Chart.js charts with better configuration
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#3498db',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    type: 'category',
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        maxTicksLimit: 10,
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        };

        // pH Chart
        const phCtx = document.getElementById('ph-chart');
        if (phCtx) {
            this.charts.ph = new Chart(phCtx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'pH',
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    ...chartOptions,
                    plugins: {
                        ...chartOptions.plugins,
                        title: {
                            display: true,
                            text: 'pH Levels Over Time',
                            font: { size: 16, weight: 'bold' }
                        }
                    }
                }
            });
        }

        // Turbidity Chart
        const turbidityCtx = document.getElementById('turbidity-chart');
        if (turbidityCtx) {
            this.charts.turbidity = new Chart(turbidityCtx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Turbidity (NTU)',
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    ...chartOptions,
                    plugins: {
                        ...chartOptions.plugins,
                        title: {
                            display: true,
                            text: 'Turbidity Over Time',
                            font: { size: 16, weight: 'bold' }
                        }
                    }
                }
            });
        }

        // Dissolved Oxygen Chart
        const doCtx = document.getElementById('dissolved-oxygen-chart');
        if (doCtx) {
            this.charts.dissolvedOxygen = new Chart(doCtx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Dissolved Oxygen (mg/L)',
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    ...chartOptions,
                    plugins: {
                        ...chartOptions.plugins,
                        title: {
                            display: true,
                            text: 'Dissolved Oxygen Over Time',
                            font: { size: 16, weight: 'bold' }
                        }
                    }
                }
            });
        }

        // Temperature Chart
        const tempCtx = document.getElementById('temperature-chart');
        if (tempCtx) {
            this.charts.temperature = new Chart(tempCtx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Temperature (°C)',
                        borderColor: '#9b59b6',
                        backgroundColor: 'rgba(155, 89, 182, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    ...chartOptions,
                    plugins: {
                        ...chartOptions.plugins,
                        title: {
                            display: true,
                            text: 'Temperature Over Time',
                            font: { size: 16, weight: 'bold' }
                        }
                    }
                }
            });
        }
    }

    updateCharts(samples) {
        // Process and aggregate data
        const processedData = this.processDataForCharts(samples);
        
        // Update each chart
        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart && processedData[chartKey]) {
                chart.data.labels = processedData[chartKey].labels;
                chart.data.datasets[0].data = processedData[chartKey].data;
                chart.update('none'); // Update without animation for better performance
            }
        });
    }

    processDataForCharts(samples) {
        // Sort samples by timestamp
        const sortedSamples = samples.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
        
        // Aggregate data based on current aggregation setting
        const aggregatedData = this.aggregateData(sortedSamples);
        
        return {
            ph: {
                labels: aggregatedData.labels,
                data: aggregatedData.ph
            },
            turbidity: {
                labels: aggregatedData.labels,
                data: aggregatedData.turbidity
            },
            dissolvedOxygen: {
                labels: aggregatedData.labels,
                data: aggregatedData.dissolved_oxygen
            },
            temperature: {
                labels: aggregatedData.labels,
                data: aggregatedData.temperature
            }
        };
    }

    aggregateData(samples) {
        const aggregationMap = new Map();
        
        samples.forEach(sample => {
            const date = new Date(sample.timestamp);
            let key;
            
            switch (this.dataAggregation) {
                case 'daily':
                    key = date.toISOString().split('T')[0];
                    break;
                case 'weekly':
                    const weekStart = new Date(date);
                    weekStart.setDate(date.getDate() - date.getDay());
                    key = weekStart.toISOString().split('T')[0];
                    break;
                case 'monthly':
                    key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                    break;
                default:
                    key = date.toISOString().split('T')[0];
            }
            
            if (!aggregationMap.has(key)) {
                aggregationMap.set(key, {
                    ph: [],
                    turbidity: [],
                    dissolved_oxygen: [],
                    temperature: []
                });
            }
            
            const data = aggregationMap.get(key);
            if (sample.ph !== null && !isNaN(sample.ph)) data.ph.push(sample.ph);
            if (sample.turbidity !== null && !isNaN(sample.turbidity)) data.turbidity.push(sample.turbidity);
            if (sample.dissolved_oxygen !== null && !isNaN(sample.dissolved_oxygen)) data.dissolved_oxygen.push(sample.dissolved_oxygen);
            if (sample.temperature !== null && !isNaN(sample.temperature)) data.temperature.push(sample.temperature);
        });
        
        // Calculate averages for each period
        const labels = [];
        const ph = [];
        const turbidity = [];
        const dissolved_oxygen = [];
        const temperature = [];
        
        Array.from(aggregationMap.keys()).sort().forEach(key => {
            const data = aggregationMap.get(key);
            labels.push(key);
            
            ph.push(data.ph.length > 0 ? data.ph.reduce((a, b) => a + b) / data.ph.length : null);
            turbidity.push(data.turbidity.length > 0 ? data.turbidity.reduce((a, b) => a + b) / data.turbidity.length : null);
            dissolved_oxygen.push(data.dissolved_oxygen.length > 0 ? data.dissolved_oxygen.reduce((a, b) => a + b) / data.dissolved_oxygen.length : null);
            temperature.push(data.temperature.length > 0 ? data.temperature.reduce((a, b) => a + b) / data.temperature.length : null);
        });
        
        return { labels, ph, turbidity, dissolved_oxygen, temperature };
    }

    showNoDataMessage() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.data.labels = [];
                chart.data.datasets[0].data = [];
                chart.update();
            }
        });
    }

    setupEventListeners() {
        // Aggregation selector
        const aggregationSelect = document.getElementById('aggregation-select');
        if (aggregationSelect) {
            aggregationSelect.addEventListener('change', (e) => {
                this.dataAggregation = e.target.value;
                if (this.currentStation) {
                    this.loadStationData();
                }
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadStations();
                if (this.currentStation) {
                    this.loadStationData();
                }
            });
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new WaterQualityDashboard();
}); 