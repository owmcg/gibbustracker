"""
Modern Gibraltar Bus Tracker - Backend Server
Flask API server that provides enhanced bus tracking data
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import requests
import re
import json
import time
from datetime import datetime, timedelta
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import os

app = Flask(__name__, template_folder='web', static_folder='web', static_url_path='')
CORS(app)

class EnhancedGibraltarBusAPI:
    def __init__(self):
        self.base_url = "https://track.bus.gi"
        self.routes = ['1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
        self.last_update = {}
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing bus data"""
        conn = sqlite3.connect('bus_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bus_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id TEXT NOT NULL,
                bus_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS route_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id TEXT NOT NULL,
                avg_buses INTEGER DEFAULT 0,
                last_active TEXT,
                total_updates INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_bus_data(self, route_id):
        """Get real-time bus data for a specific route with caching"""
        # Check cache first (cache for 30 seconds)
        cache_key = f"route_{route_id}"
        now = datetime.now()
        
        if cache_key in self.cache and cache_key in self.last_update:
            if (now - self.last_update[cache_key]).seconds < 30:
                return self.cache[cache_key]
        
        url = f"{self.base_url}/busTracker.php?id={route_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            result = {
                'route_id': route_id,
                'status': 'unknown',
                'timestamp': None,
                'buses': [],
                'last_checked': now.isoformat(),
                'url': url
            }
            
            # Check if buses are available
            if "Bus Location is Currently Unavailable" in content:
                result['status'] = 'no_buses_active'
            else:
                # Extract timestamp
                timestamp_match = re.search(r'Last Updated: ([^-]+)', content)
                if timestamp_match:
                    result['timestamp'] = timestamp_match.group(1).strip()
                    result['status'] = 'active'
                
                # Extract bus positions
                bus_pattern = rf"src='R{route_id}/c(\d+[a-z]*)\.png'"
                bus_matches = re.findall(bus_pattern, content)
                
                for bus_id in bus_matches:
                    bus_data = {
                        'bus_id': bus_id,
                        'route_id': route_id,
                        'position_image': f"R{route_id}/c{bus_id}.png",
                        'estimated_location': self.estimate_location(route_id, bus_id),
                        'last_seen': result['timestamp']
                    }
                    result['buses'].append(bus_data)
            
            # Store in database
            self.store_bus_data(result)
            
            # Update cache
            self.cache[cache_key] = result
            self.last_update[cache_key] = now
            
            return result
            
        except Exception as e:
            return {
                'route_id': route_id,
                'status': 'error',
                'error': str(e),
                'timestamp': None,
                'buses': [],
                'last_checked': now.isoformat()
            }
    
    def estimate_location(self, route_id, bus_id):
        """Estimate bus location based on image filename and route data"""
        # This is a placeholder - in a real implementation, you'd map
        # bus image positions to actual GPS coordinates
        route_stops = self.get_route_stops(route_id)
        
        # Simple estimation based on bus_id patterns
        try:
            bus_num = int(re.search(r'\d+', bus_id).group())
            stop_index = bus_num % len(route_stops)
            return route_stops[stop_index]
        except:
            return route_stops[0] if route_stops else {"name": "Unknown", "lat": 36.1408, "lng": -5.3536}
    
    def get_route_stops(self, route_id):
        """Get predefined stops for a route (placeholder data)"""
        # Placeholder Gibraltar bus stops - in reality, you'd have detailed stop data
        gibraltar_stops = {
            '1': [
                {"name": "Main Street", "lat": 36.1408, "lng": -5.3536},
                {"name": "Casemates Square", "lat": 36.1425, "lng": -5.3515},
                {"name": "Europa Point", "lat": 36.1089, "lng": -5.3453}
            ],
            '2': [
                {"name": "Winston Churchill Avenue", "lat": 36.1515, "lng": -5.3489},
                {"name": "Rosia Bay", "lat": 36.1198, "lng": -5.3611},
                {"name": "Eastern Beach", "lat": 36.1456, "lng": -5.3429}
            ],
            '3': [
                {"name": "Upper Rock", "lat": 36.1363, "lng": -5.3433},
                {"name": "Cable Car Station", "lat": 36.1382, "lng": -5.3446},
                {"name": "Alameda Gardens", "lat": 36.1398, "lng": -5.3502}
            ]
        }
        
        # Default stops for routes not specifically defined
        default_stops = [
            {"name": "Gibraltar Center", "lat": 36.1408, "lng": -5.3536},
            {"name": "North District", "lat": 36.1500, "lng": -5.3500},
            {"name": "South District", "lat": 36.1200, "lng": -5.3600}
        ]
        
        return gibraltar_stops.get(route_id, default_stops)
    
    def store_bus_data(self, bus_data):
        """Store bus data in database for analytics"""
        try:
            conn = sqlite3.connect('bus_data.db')
            cursor = conn.cursor()
            
            for bus in bus_data['buses']:
                cursor.execute('''
                    INSERT INTO bus_positions 
                    (route_id, bus_id, timestamp, status, recorded_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    bus_data['route_id'],
                    bus['bus_id'],
                    bus_data['timestamp'],
                    bus_data['status'],
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
    
    def get_all_routes_data(self):
        """Get data for all routes"""
        results = {}
        for route in self.routes:
            results[route] = self.get_bus_data(route)
            time.sleep(0.5)  # Small delay to be respectful
        return results
    
    def calculate_eta(self, from_stop, to_stop, route_id):
        """Calculate estimated time of arrival considering traffic"""
        # Placeholder ETA calculation
        # In reality, you'd use routing APIs and current traffic data
        base_time = 5  # Base 5 minutes between stops
        traffic_factor = 1.2  # 20% delay for traffic
        
        return {
            'eta_minutes': int(base_time * traffic_factor),
            'confidence': 'medium',
            'factors': ['traffic', 'route_distance']
        }

# Initialize the API
bus_api = EnhancedGibraltarBusAPI()

# API Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/buses')
def get_all_buses():
    """Get all bus data"""
    try:
        data = bus_api.get_all_routes_data()
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/buses/<route_id>')
def get_route_buses(route_id):
    """Get buses for a specific route"""
    try:
        if route_id not in bus_api.routes:
            return jsonify({'success': False, 'error': 'Invalid route ID'}), 400
        
        data = bus_api.get_bus_data(route_id)
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/routes')
def get_routes():
    """Get all available routes"""
    return jsonify({
        'success': True,
        'routes': bus_api.routes,
        'total': len(bus_api.routes)
    })

@app.route('/api/stops/<route_id>')
def get_route_stops(route_id):
    """Get stops for a specific route"""
    try:
        stops = bus_api.get_route_stops(route_id)
        return jsonify({
            'success': True,
            'route_id': route_id,
            'stops': stops
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/eta')
def calculate_eta():
    """Calculate estimated time of arrival"""
    from_stop = request.args.get('from')
    to_stop = request.args.get('to')
    route_id = request.args.get('route')
    
    if not all([from_stop, to_stop, route_id]):
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400
    
    try:
        eta = bus_api.calculate_eta(from_stop, to_stop, route_id)
        return jsonify({
            'success': True,
            'eta': eta,
            'route_id': route_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status')
def get_system_status():
    """Get system status and statistics"""
    try:
        conn = sqlite3.connect('bus_data.db')
        cursor = conn.cursor()
        
        # Get total records
        cursor.execute('SELECT COUNT(*) FROM bus_positions')
        total_records = cursor.fetchone()[0]
        
        # Get records from last hour
        hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM bus_positions WHERE recorded_at > ?', (hour_ago,))
        recent_records = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'status': 'operational',
            'statistics': {
                'total_records': total_records,
                'recent_records': recent_records,
                'supported_routes': len(bus_api.routes),
                'last_update': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Background task to update bus data
def update_bus_data():
    """Background task to regularly update bus data"""
    print("Updating bus data...")
    try:
        bus_api.get_all_routes_data()
        print("Bus data updated successfully")
    except Exception as e:
        print(f"Error updating bus data: {e}")

# Initialize scheduler for background updates
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_bus_data, trigger="interval", seconds=60)  # Update every minute
scheduler.start()

if __name__ == '__main__':
    print("Starting Gibraltar Bus Tracker Server...")
    print("API Endpoints:")
    print("  GET /api/buses - All bus data")
    print("  GET /api/buses/<route_id> - Specific route")
    print("  GET /api/routes - Available routes")
    print("  GET /api/stops/<route_id> - Route stops")
    print("  GET /api/eta - Calculate arrival times")
    print("  GET /api/status - System status")
    print("\nWeb Interface: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)