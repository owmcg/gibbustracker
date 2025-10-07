// Map functionality for Gibraltar Bus Tracker
let map = null;
let markers = {};

function initializeMap() {
    if (typeof L === 'undefined') {
        console.warn('Leaflet not loaded, map functionality disabled');
        return;
    }
    
    // Initialize map centered on Gibraltar
    map = L.map('map').setView([36.1408, -5.3536], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    
    console.log('Map initialized');
}

function addBusMarker(routeId, bus) {
    if (!map || !bus.estimated_location) return;
    
    const location = bus.estimated_location;
    if (!location.lat || !location.lng) return;
    
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
        .addTo(map);
    
    // Add popup
    const popupContent = `
        <div class="bus-popup">
            <h4>Route ${routeId} - Bus ${bus.bus_id}</h4>
            <p><strong>Location:</strong> ${location.name}</p>
            <p><strong>Last Update:</strong> ${bus.last_seen || 'Unknown'}</p>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    markers[`${routeId}-${bus.bus_id}`] = marker;
}

function clearMapMarkers() {
    Object.values(markers).forEach(marker => {
        if (map && map.hasLayer(marker)) {
            map.removeLayer(marker);
        }
    });
    markers = {};
}

function updateMapWithBusData(busData) {
    if (!map) return;
    
    clearMapMarkers();
    
    Object.entries(busData).forEach(([routeId, routeData]) => {
        if (routeData.status === 'active' && routeData.buses) {
            routeData.buses.forEach(bus => {
                addBusMarker(routeId, bus);
            });
        }
    });
}