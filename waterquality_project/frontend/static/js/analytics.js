// Analytics Dashboard JavaScript
class AnalyticsDashboard {
    constructor() {
        this.charts = {};
        this.data = null;
        this.init();
    }

    async init() {
        await this.loadAnalyticsData();
        this.setupEventListeners();
        this.renderDashboard();
    }

    async loadAnalyticsData() {
        try {
            console.log('Loading analytics data...');
            const response = await fetch('/api/analytics/dashboard/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.data = await response.json();
            console.log('Analytics data loaded:', this.data);
        } catch (error) {
            console.error('Error loading analytics data:', error);
            this.showError('Failed to load analytics data');
        }
    }

    setupEventListeners() {
        // Report generation
        document.getElementById('generate-report-btn').addEventListener('click', () => {
            this.generateReport();
        });

        // Export data
        document.getElementById('export-data-btn').addEventListener('click', () => {
            this.exportData();
        });

        // Auto-refresh every 5 minutes
        setInterval(() => {
            this.loadAnalyticsData().then(() => {
                this.renderDashboard();
            });
        }, 5 * 60 * 1000);
    }

    renderDashboard() {
        if (!this.data) return;

        this.renderOverviewCards();
        this.renderSampleTrendsChart();
        this.renderParameterAveragesChart();
        this.renderTopStations();
        this.renderProblematicStations();
        this.renderGeographicChart();
        this.renderRecentAlerts();
    }

    renderOverviewCards() {
        const overview = this.data.system_overview;
        if (!overview) return;

        // Update overview cards
        this.updateCard('total-stations', overview.total_stations);
        this.updateCard('active-stations', overview.active_stations);
        this.updateCard('total-samples', overview.total_samples);
        this.updateCard('avg-quality-score', `${overview.avg_quality_score.toFixed(1)}%`);
        this.updateCard('critical-alerts', overview.critical_alerts);
        this.updateCard('data-completeness', `${overview.data_completeness.toFixed(1)}%`);
    }

    updateCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    renderSampleTrendsChart() {
        const ctx = document.getElementById('sampleTrendsChart');
        console.log('Rendering sample trends chart, ctx:', ctx, 'data:', this.data.daily_samples);
        if (!ctx || !this.data.daily_samples) return;

        // Destroy existing chart
        if (this.charts.sampleTrends) {
            this.charts.sampleTrends.destroy();
        }

        const chartData = {
            labels: this.data.daily_samples.map(item => item.date),
            datasets: [{
                label: 'Daily Samples',
                data: this.data.daily_samples.map(item => item.count),
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        };

        this.charts.sampleTrends = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }

    renderParameterAveragesChart() {
        const ctx = document.getElementById('parameterAveragesChart');
        console.log('Rendering parameter averages chart, ctx:', ctx, 'data:', this.data.parameter_averages);
        if (!ctx || !this.data.parameter_averages) return;

        // Destroy existing chart
        if (this.charts.parameterAverages) {
            this.charts.parameterAverages.destroy();
        }

        const averages = this.data.parameter_averages;
        const chartData = {
            labels: ['pH', 'Turbidity', 'Dissolved Oxygen', 'Temperature'],
            datasets: [{
                label: 'Average Values',
                data: [
                    averages.avg_ph || 0,
                    averages.avg_turbidity || 0,
                    averages.avg_dissolved_oxygen || 0,
                    averages.avg_temperature || 0
                ],
                backgroundColor: [
                    'rgba(52, 152, 219, 0.8)',
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(46, 204, 113, 0.8)',
                    'rgba(155, 89, 182, 0.8)'
                ],
                borderColor: [
                    '#3498db',
                    '#e74c3c',
                    '#2ecc71',
                    '#9b59b6'
                ],
                borderWidth: 2
            }]
        };

        this.charts.parameterAverages = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    renderTopStations() {
        const container = document.getElementById('top-stations-list');
        if (!container || !this.data.top_stations) return;

        container.innerHTML = this.data.top_stations.map(station => `
            <div class="station-item">
                <span class="station-name">${station.station.name}</span>
                <span class="station-score">${station.quality_score.toFixed(1)}%</span>
            </div>
        `).join('');
    }

    renderProblematicStations() {
        const container = document.getElementById('problematic-stations-list');
        if (!container || !this.data.problematic_stations) return;

        container.innerHTML = this.data.problematic_stations.map(station => `
            <div class="station-item problematic">
                <span class="station-name">${station.station.name}</span>
                <span class="station-score problematic">${station.quality_score.toFixed(1)}%</span>
            </div>
        `).join('');
    }

    renderGeographicChart() {
        const ctx = document.getElementById('geographicChart');
        console.log('Rendering geographic chart, ctx:', ctx, 'data:', this.data.geographic_distribution);
        if (!ctx || !this.data.geographic_distribution) return;

        // Destroy existing chart
        if (this.charts.geographic) {
            this.charts.geographic.destroy();
        }

        const geoData = this.data.geographic_distribution;
        const chartData = {
            labels: geoData.map(item => item.province || item.station_type || 'Unknown'),
            datasets: [{
                label: 'Stations per Category',
                data: geoData.map(item => item.station_count),
                backgroundColor: [
                    'rgba(52, 152, 219, 0.8)',
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(46, 204, 113, 0.8)',
                    'rgba(155, 89, 182, 0.8)',
                    'rgba(241, 196, 15, 0.8)',
                    'rgba(230, 126, 34, 0.8)',
                    'rgba(26, 188, 156, 0.8)',
                    'rgba(142, 68, 173, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };

        this.charts.geographic = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    renderRecentAlerts() {
        const container = document.getElementById('recent-alerts-list');
        if (!container || !this.data.recent_alerts) return;

        container.innerHTML = this.data.recent_alerts.map(alert => `
            <div class="alert-item ${alert.resolved ? 'resolved' : ''}">
                <div class="alert-info">
                    <div class="alert-station">${alert.station_name}</div>
                    <div class="alert-message">${alert.message}</div>
                </div>
                <div class="alert-meta">
                    <div class="alert-severity ${alert.severity}">${alert.severity.toUpperCase()}</div>
                    <div class="alert-time">${new Date(alert.triggered_at).toLocaleDateString()}</div>
                </div>
            </div>
        `).join('');
    }

    async generateReport() {
        const reportType = document.getElementById('report-type').value;
        const output = document.getElementById('report-output');
        
        output.innerHTML = '<p>Generating report...</p>';
        
        try {
            const response = await fetch('/api/analytics/reports/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    report_type: reportType,
                    filters: {}
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const report = await response.json();
            this.displayReport(report);
        } catch (error) {
            console.error('Error generating report:', error);
            output.innerHTML = '<p style="color: #e74c3c;">Error generating report</p>';
        }
    }

    displayReport(report) {
        const output = document.getElementById('report-output');
        
        let html = '<h4>Report: ' + report.report_type.replace('_', ' ').toUpperCase() + '</h4>';
        html += '<p><strong>Generated:</strong> ' + new Date(report.generated_at).toLocaleString() + '</p>';
        
        if (report.report_type === 'system_overview') {
            html += this.formatSystemOverviewReport(report);
        } else if (report.report_type === 'quality_assessment') {
            html += this.formatQualityAssessmentReport(report);
        } else if (report.report_type === 'station_comparison') {
            html += this.formatStationComparisonReport(report);
        }
        
        output.innerHTML = html;
    }

    formatSystemOverviewReport(report) {
        let html = '<div class="report-section">';
        html += '<h5>System Statistics</h5>';
        html += '<ul>';
        html += '<li><strong>Total Stations:</strong> ' + report.total_stations + '</li>';
        html += '<li><strong>Total Samples:</strong> ' + report.total_samples + '</li>';
        html += '<li><strong>Total Alerts:</strong> ' + report.total_alerts + '</li>';
        html += '</ul>';
        
        if (report.parameter_statistics) {
            html += '<h5>Parameter Statistics</h5>';
            html += '<div style="overflow-x: auto; margin-top: 1rem;">';
            html += '<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; min-width: 500px;">';
            html += '<thead><tr style="background-color: #f8f9fa;">';
            html += '<th style="padding: 12px; text-align: left; border: 1px solid #ddd; font-weight: bold; width: 25%;">Parameter</th>';
            html += '<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-weight: bold; width: 25%;">Average</th>';
            html += '<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-weight: bold; width: 25%;">Min</th>';
            html += '<th style="padding: 12px; text-align: center; border: 1px solid #ddd; font-weight: bold; width: 25%;">Max</th>';
            html += '</tr></thead><tbody>';
            html += '<tr><td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 25%;">pH</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.ph_avg?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.ph_min?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.ph_max?.toFixed(2) || 'N/A') + '</td></tr>';
            html += '<tr><td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 25%;">Turbidity</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.turbidity_avg?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.turbidity_min?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.turbidity_max?.toFixed(2) || 'N/A') + '</td></tr>';
            html += '<tr><td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 25%;">Dissolved Oxygen</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.dissolved_oxygen_avg?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.dissolved_oxygen_min?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.dissolved_oxygen_max?.toFixed(2) || 'N/A') + '</td></tr>';
            html += '<tr><td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 25%;">Temperature</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.temperature_avg?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.temperature_min?.toFixed(2) || 'N/A') + '</td><td style="padding: 12px; text-align: center; border: 1px solid #ddd; width: 25%;">' + (report.parameter_statistics.temperature_max?.toFixed(2) || 'N/A') + '</td></tr>';
            html += '</tbody></table>';
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }

    formatQualityAssessmentReport(report) {
        let html = '<div class="report-section">';
        html += '<h5>Quality Assessment</h5>';
        html += '<p><strong>Total Samples:</strong> ' + report.total_samples + '</p>';
        
        if (report.quality_assessment) {
            html += '<h6>pH Quality Distribution</h6>';
            html += '<ul>';
            html += '<li>Excellent (6.5-8.5): ' + report.quality_assessment.ph.excellent + ' samples</li>';
            html += '<li>Good (6.0-9.0): ' + report.quality_assessment.ph.good + ' samples</li>';
            html += '<li>Poor (<6.0 or >9.0): ' + report.quality_assessment.ph.poor + ' samples</li>';
            html += '</ul>';
            
            html += '<h6>Turbidity Quality Distribution</h6>';
            html += '<ul>';
            html += '<li>Excellent (≤5 NTU): ' + report.quality_assessment.turbidity.excellent + ' samples</li>';
            html += '<li>Good (5-10 NTU): ' + report.quality_assessment.turbidity.good + ' samples</li>';
            html += '<li>Poor (>10 NTU): ' + report.quality_assessment.turbidity.poor + ' samples</li>';
            html += '</ul>';
            
            html += '<h6>Dissolved Oxygen Quality Distribution</h6>';
            html += '<ul>';
            html += '<li>Excellent (≥6 mg/L): ' + report.quality_assessment.dissolved_oxygen.excellent + ' samples</li>';
            html += '<li>Good (4-6 mg/L): ' + report.quality_assessment.dissolved_oxygen.good + ' samples</li>';
            html += '<li>Poor (<4 mg/L): ' + report.quality_assessment.dissolved_oxygen.poor + ' samples</li>';
            html += '</ul>';
        }
        
        html += '</div>';
        return html;
    }

    formatStationComparisonReport(report) {
        let html = '<div class="report-section">';
        html += '<h5>Station Comparison</h5>';
        
        if (report.comparison_data && report.comparison_data.summary) {
            html += '<p><strong>Stations Compared:</strong> ' + report.comparison_data.summary.total_stations + '</p>';
            html += '<p><strong>Total Samples:</strong> ' + report.comparison_data.summary.total_samples + '</p>';
            html += '<p><strong>Average Quality Score:</strong> ' + report.comparison_data.summary.avg_quality_score.toFixed(1) + '%</p>';
        }
        
        html += '</div>';
        return html;
    }

    exportData() {
        if (!this.data) {
            this.showError('No data to export');
            return;
        }

        const dataStr = JSON.stringify(this.data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `hydronexus-analytics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    showError(message) {
        // Create a simple error notification
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #e74c3c;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            document.body.removeChild(errorDiv);
        }, 5000);
    }
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsDashboard();
}); 