// API utility functions for Gibraltar Bus Tracker
const API = {
    baseURL: '/api',
    
    async request(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    async getBuses() {
        return this.request('/buses');
    },
    
    async getRoute(routeId) {
        return this.request(`/buses/${routeId}`);
    },
    
    async getRoutes() {
        return this.request('/routes');
    },
    
    async getStatus() {
        return this.request('/status');
    }
};