// Gibraltar Bus Tracker - Main Application
class GibraltarBusTracker {
    constructor() {
        this.apiBase = '/api';
        this.busData = {};
        this.updateInterval = null;
        this.map = null;
        this.markers = {};
        
        this.init();
    }
    
    async init() {
        console.log('Initializing Gibraltar Bus Tracker...');
        
        // Show loading overlay
        this.showLoading(true);
        
        try {
            // Initialize components
            await this.initializeAPI();
            this.initializeEventListeners();
            this.initializeMap();
            
            // Load initial data
            await this.loadAllData();
            
            // Start auto-refresh
            this.startAutoRefresh();
            
            // Hide loading overlay
            this.showLoading(false);
            
            console.log('Gibraltar Bus Tracker initialized successfully');
        } catch (error) {
            console.error('Failed to initialize:', error);
            this.showError('Failed to initialize bus tracker');
            this.showLoading(false);
        }
    }
    
    async initializeAPI() {
        // Test API connection
        try {
            const response = await fetch(`${this.apiBase}/status`);
            const data = await response.json();
            
            if (data.success) {
                this.updateStatus('connected', 'Connected');
                console.log('API connection successful');
            } else {
                throw new Error('API returned error status');
            }
        } catch (error) {
            this.updateStatus('error', 'Connection Error');
            throw error;
        }
    }
    
    initializeEventListeners() {
        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadAllData();
        });
        
        // Route filter
        document.getElementById('routeFilter').addEventListener('change', (e) => {
            this.filterMapByRoute(e.target.value);
        });
        
        // Center map button
        document.getElementById('centerMapBtn').addEventListener('click', () => {
            this.centerMapOnGibraltar();
        });
        
        // Modal close
        document.getElementById('closeModal').addEventListener('click', () => {
            this.hideModal();
        });
        
        // Click outside modal to close
        document.getElementById('busModal').addEventListener('click', (e) => {
            if (e.target.id === 'busModal') {
                this.hideModal();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideModal();
            } else if (e.key === 'r' && e.ctrlKey) {
                e.preventDefault();
                this.loadAllData();
            }
        });
    }
    
    initializeMap() {
        // Initialize Leaflet map centered on Gibraltar
        this.map = L.map('map').setView([36.1408, -5.3536], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        // Add Gibraltar bounds
        const gibraltarBounds = [
            [36.100, -5.370],
            [36.160, -5.330]
        ];
        
        // Optional: Add a subtle boundary rectangle
        L.rectangle(gibraltarBounds, {
            color: '#e30613',
            weight: 2,
            fillOpacity: 0.1
        }).addTo(this.map);
        
        console.log('Map initialized');
    }
    
    async loadAllData() {
        try {
            this.updateStatus('loading', 'Loading...');
            
            // Load bus data
            const response = await fetch(`${this.apiBase}/buses`);
            const data = await response.json();
            
            if (data.success) {
                this.busData = data.data;
                this.updateUI();
                this.updateMap();
                this.updateStatus('connected', 'Live');
            } else {
                throw new Error(data.error || 'Failed to load bus data');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.updateStatus('error', 'Error');
            this.showError('Failed to load bus data');
        }
    }
    
    updateUI() {
        this.renderRouteCards();
        this.renderBusTable();
        this.updateAnalytics();
        this.updateRouteFilter();
    }
    
    renderRouteCards() {
        const container = document.getElementById('routeCards');
        container.innerHTML = '';
        
        Object.entries(this.busData).forEach(([routeId, routeData]) => {
            const card = this.createRouteCard(routeId, routeData);
            container.appendChild(card);
        });
    }
    
    createRouteCard(routeId, routeData) {
        const card = document.createElement('div');
        card.className = 'route-card';
        
        const statusClass = routeData.status === 'active' ? 'active' : 'inactive';
        const busCount = routeData.buses ? routeData.buses.length : 0;
        const lastUpdate = routeData.timestamp || 'No recent data';
        
        card.innerHTML = `
            <div class="route-card-header">
                <div class="route-number">Route ${routeId}</div>
                <div class="route-status ${statusClass}">${routeData.status}</div>
            </div>
            <div class="bus-count">${busCount}</div>
            <div class="bus-label">${busCount === 1 ? 'Bus' : 'Buses'} Active</div>
            <div class="last-update">Last Update: ${this.formatTime(lastUpdate)}</div>
        `;
        
        // Add click handler to show route details
        card.addEventListener('click', () => {
            this.showRouteDetails(routeId, routeData);
        });
        
        return card;
    }
    
    renderBusTable() {
        const tbody = document.getElementById('busTableBody');
        tbody.innerHTML = '';
        
        Object.entries(this.busData).forEach(([routeId, routeData]) => {
            if (routeData.buses && routeData.buses.length > 0) {
                routeData.buses.forEach(bus => {
                    const row = this.createBusTableRow(routeId, bus, routeData);
                    tbody.appendChild(row);
                });
            } else {
                // Show empty state for inactive routes
                const row = this.createEmptyBusRow(routeId, routeData);
                tbody.appendChild(row);
            }
        });
    }
    
    createBusTableRow(routeId, bus, routeData) {
        const row = document.createElement('tr');
        
        const estimatedLocation = bus.estimated_location || { name: 'Unknown' };
        const statusClass = routeData.status === 'active' ? 'active' : 'inactive';
        
        row.innerHTML = `
            <td><span class="route-number-small">Route ${routeId}</span></td>
            <td><span class="bus-id">${bus.bus_id}</span></td>
            <td><span class="bus-status ${statusClass}">${routeData.status}</span></td>
            <td>${this.formatTime(routeData.timestamp)}</td>
            <td>${estimatedLocation.name}</td>
            <td>
                <button class="btn btn-sm" onclick="busTracker.showBusDetails('${routeId}', '${bus.bus_id}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
            </td>
        `;
        
        return row;
    }
    
    createEmptyBusRow(routeId, routeData) {
        const row = document.createElement('tr');
        row.className = 'empty-row';
        
        row.innerHTML = `
            <td><span class="route-number-small">Route ${routeId}</span></td>
            <td colspan="5" class="text-muted">No buses currently active</td>
        `;
        
        return row;
    }
    
    updateAnalytics() {
        let totalBuses = 0;
        let activeRoutes = 0;
        let latestUpdate = null;
        
        Object.values(this.busData).forEach(routeData => {
            if (routeData.status === 'active') {
                activeRoutes++;
                totalBuses += routeData.buses ? routeData.buses.length : 0;
                
                if (routeData.timestamp && (!latestUpdate || new Date(routeData.timestamp) > new Date(latestUpdate))) {
                    latestUpdate = routeData.timestamp;
                }
            }
        });
        
        document.getElementById('totalBuses').textContent = totalBuses;
        document.getElementById('activeRoutes').textContent = activeRoutes;
        document.getElementById('lastUpdate').textContent = latestUpdate ? this.formatTime(latestUpdate) : '--';
        document.getElementById('systemStatus').textContent = activeRoutes > 0 ? 'Operational' : 'Limited';
    }
    
    updateRouteFilter() {
        const select = document.getElementById('routeFilter');
        const currentValue = select.value;
        
        // Clear existing options except "All Routes"
        select.innerHTML = '<option value="all">All Routes</option>';
        
        // Add route options
        Object.keys(this.busData).forEach(routeId => {
            const option = document.createElement('option');
            option.value = routeId;
            option.textContent = `Route ${routeId}`;
            select.appendChild(option);
        });
        
        // Restore previous selection
        select.value = currentValue;
    }
    
    updateMap() {
        // Clear existing markers
        Object.values(this.markers).forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = {};
        
        // Add new markers for active buses
        Object.entries(this.busData).forEach(([routeId, routeData]) => {
            if (routeData.status === 'active' && routeData.buses) {
                routeData.buses.forEach(bus => {
                    this.addBusMarker(routeId, bus);
                });
            }
        });
    }
    
    addBusMarker(routeId, bus) {
        const location = bus.estimated_location;
        if (!location || !location.lat || !location.lng) return;
        
        // Create custom bus icon
        const busIcon = L.divIcon({
            html: `<div class="bus-marker route-${routeId}">
                     <i class="fas fa-bus"></i>
                     <span>${routeId}</span>
                   </div>`,
            className: 'custom-div-icon',
            iconSize: [40, 40],
            iconAnchor: [20, 20]
        });
        
        const marker = L.marker([location.lat, location.lng], { icon: busIcon })
            .addTo(this.map);
        
        // Add popup with bus information
        const popupContent = `
            <div class="bus-popup">
                <h4>Route ${routeId} - Bus ${bus.bus_id}</h4>
                <p><strong>Location:</strong> ${location.name}</p>
                <p><strong>Last Update:</strong> ${this.formatTime(bus.last_seen)}</p>
                <button onclick="busTracker.showBusDetails('${routeId}', '${bus.bus_id}')" class="btn btn-sm">
                    View Details
                </button>
            </div>
        `;
        
        marker.bindPopup(popupContent);
        
        this.markers[`${routeId}-${bus.bus_id}`] = marker;
    }
    
    filterMapByRoute(routeId) {
        Object.entries(this.markers).forEach(([markerId, marker]) => {
            const [markerRouteId] = markerId.split('-');
            
            if (routeId === 'all' || markerRouteId === routeId) {
                marker.addTo(this.map);
            } else {
                this.map.removeLayer(marker);
            }
        });
    }
    
    centerMapOnGibraltar() {
        this.map.setView([36.1408, -5.3536], 13);
    }
    
    showBusDetails(routeId, busId) {
        const routeData = this.busData[routeId];
        const bus = routeData.buses.find(b => b.bus_id === busId);
        
        if (!bus) {
            this.showError('Bus not found');
            return;
        }
        
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Route ${routeId} - Bus ${busId}`;
        
        modalBody.innerHTML = `
            <div class="bus-detail-content">
                <div class="detail-section">
                    <h4>Current Status</h4>
                    <p><strong>Status:</strong> ${routeData.status}</p>
                    <p><strong>Last Update:</strong> ${this.formatTime(routeData.timestamp)}</p>
                    <p><strong>Location:</strong> ${bus.estimated_location?.name || 'Unknown'}</p>
                </div>
                
                <div class="detail-section">
                    <h4>Route Information</h4>
                    <p><strong>Route:</strong> ${routeId}</p>
                    <p><strong>Bus ID:</strong> ${busId}</p>
                    <p><strong>Service:</strong> ${this.getRouteDescription(routeId)}</p>
                </div>
                
                <div class="detail-section">
                    <h4>Technical Details</h4>
                    <p><strong>Data Source:</strong> Gibraltar Bus Tracker</p>
                    <p><strong>Position Image:</strong> ${bus.position_image || 'N/A'}</p>
                    <p><strong>Confidence:</strong> High</p>
                </div>
                
                <div class="detail-actions">
                    <button class="btn btn-primary" onclick="busTracker.trackBus('${routeId}', '${busId}')">
                        <i class="fas fa-map-marker-alt"></i> Track on Map
                    </button>
                    <button class="btn btn-secondary" onclick="busTracker.getETA('${routeId}', '${busId}')">
                        <i class="fas fa-clock"></i> Get ETA
                    </button>
                </div>
            </div>
        `;
        
        this.showModal();
    }
    
    showRouteDetails(routeId, routeData) {
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `Route ${routeId} Details`;
        
        const busCount = routeData.buses ? routeData.buses.length : 0;
        const busList = routeData.buses ? 
            routeData.buses.map(bus => `<li>Bus ${bus.bus_id} - ${bus.estimated_location?.name || 'Unknown location'}</li>`).join('') :
            '<li>No active buses</li>';
        
        modalBody.innerHTML = `
            <div class="route-detail-content">
                <div class="detail-section">
                    <h4>Route Status</h4>
                    <p><strong>Status:</strong> ${routeData.status}</p>
                    <p><strong>Active Buses:</strong> ${busCount}</p>
                    <p><strong>Last Update:</strong> ${this.formatTime(routeData.timestamp)}</p>
                </div>
                
                <div class="detail-section">
                    <h4>Active Buses</h4>
                    <ul class="bus-list">${busList}</ul>
                </div>
                
                <div class="detail-section">
                    <h4>Route Information</h4>
                    <p><strong>Description:</strong> ${this.getRouteDescription(routeId)}</p>
                    <p><strong>Typical Service:</strong> ${this.getServiceInfo(routeId)}</p>
                </div>
                
                <div class="detail-actions">
                    <button class="btn btn-primary" onclick="busTracker.focusRoute('${routeId}')">
                        <i class="fas fa-map"></i> View on Map
                    </button>
                    <button class="btn btn-secondary" onclick="busTracker.getRouteSchedule('${routeId}')">
                        <i class="fas fa-calendar"></i> View Schedule
                    </button>
                </div>
            </div>
        `;
        
        this.showModal();
    }
    
    trackBus(routeId, busId) {
        const marker = this.markers[`${routeId}-${busId}`];
        if (marker) {
            this.map.setView(marker.getLatLng(), 16);
            marker.openPopup();
            this.hideModal();
        } else {
            this.showError('Bus location not available on map');
        }
    }
    
    focusRoute(routeId) {
        // Set route filter and focus map
        document.getElementById('routeFilter').value = routeId;
        this.filterMapByRoute(routeId);
        
        // Find bounds of all buses in route
        const routeBuses = Object.entries(this.markers)
            .filter(([markerId]) => markerId.startsWith(routeId))
            .map(([, marker]) => marker);
        
        if (routeBuses.length > 0) {
            const group = new L.featureGroup(routeBuses);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
        
        this.hideModal();
    }
    
    getRouteDescription(routeId) {
        const descriptions = {
            '1': 'Main Street - Casemates - Europa Point',
            '2': 'Winston Churchill Ave - Rosia Bay - Eastern Beach',
            '3': 'Upper Rock - Cable Car - Alameda Gardens',
            '7': 'North District Service',
            '8': 'South District Service',
            '9': 'Express Route',
            'N1': 'Night Service Route 1',
            'N8E': 'Night Service Route 8 East',
            'N8S': 'Night Service Route 8 South'
        };
        
        return descriptions[routeId] || 'Gibraltar Bus Service';
    }
    
    getServiceInfo(routeId) {
        const services = {
            '1': 'Daily service, 15-30 min frequency',
            '2': 'Daily service, 20-40 min frequency',
            '3': 'Tourist route, hourly service',
            '7': 'Peak hours only',
            '8': 'Daily service, 30 min frequency',
            '9': 'Limited service',
            'N1': 'Night service, hourly',
            'N8E': 'Night service, limited',
            'N8S': 'Night service, limited'
        };
        
        return services[routeId] || 'Standard service';
    }
    
    async getETA(routeId, busId) {
        try {
            const response = await fetch(`${this.apiBase}/eta?route=${routeId}&from=current&to=next`);
            const data = await response.json();
            
            if (data.success) {
                alert(`Estimated arrival: ${data.eta.eta_minutes} minutes`);
            } else {
                this.showError('ETA calculation not available');
            }
        } catch (error) {
            this.showError('Failed to calculate ETA');
        }
    }
    
    showModal() {
        document.getElementById('busModal').style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    hideModal() {
        document.getElementById('busModal').style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
    
    showError(message) {
        // Simple error notification - in production, use a proper notification system
        alert(`Error: ${message}`);
    }
    
    updateStatus(status, text) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        statusDot.className = `status-dot ${status}`;
        statusText.textContent = text;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '--';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch {
            return timestamp;
        }
    }
    
    startAutoRefresh() {
        // Refresh data every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadAllData();
        }, 30000);
    }
    
    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.busTracker = new GibraltarBusTracker();
});

// Handle page visibility changes to pause/resume updates
document.addEventListener('visibilitychange', () => {
    if (window.busTracker) {
        if (document.hidden) {
            window.busTracker.stopAutoRefresh();
        } else {
            window.busTracker.startAutoRefresh();
        }
    }
});