// Water Quality Stations App - Main JavaScript

// Sample data (in a real app, this would come from your backend)
const stations = [
    {
        id: 1,
        name: "Riverbank Station",
        latitude: -1.2921,
        longitude: 36.8219,
        ph: 7.2,
        turbidity: 3.1,
        last_sample: "2024-07-20"
    },
    {
        id: 2,
        name: "Lakeside Station", 
        latitude: -1.3000,
        longitude: 36.8000,
        ph: 6.8,
        turbidity: 2.5,
        last_sample: "2024-07-19"
    },
    {
        id: 3,
        name: "Upland Station",
        latitude: -1.3100,
        longitude: 36.8500,
        ph: 7.5,
        turbidity: 1.8,
        last_sample: "2024-07-18"
    }
];

// Initialize the map
function initMap() {
    // Create map centered on first station
    const map = L.map('map').setView([stations[0].latitude, stations[0].longitude], 12);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add markers for each station
    stations.forEach(station => {
        const marker = L.marker([station.latitude, station.longitude])
            .addTo(map)
            .bindPopup(`
                <b>${station.name}</b><br>
                pH: ${station.ph}<br>
                Turbidity: ${station.turbidity}<br>
                Last Sample: ${station.last_sample}
            `);
    });
    
    return map;
}

// Create the pH chart
function createChart() {
    const ctx = document.getElementById('chart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stations.map(station => station.name),
            datasets: [{
                label: 'pH Level',
                data: stations.map(station => station.ph),
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(75, 192, 192, 0.6)', 
                    'rgba(255, 206, 86, 0.6)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 14,
                    title: {
                        display: true,
                        text: 'pH Level'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Water Quality pH Measurements'
                }
            }
        }
    });
}

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    createChart();
});