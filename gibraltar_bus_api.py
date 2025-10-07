"""
Gibraltar Bus Tracker API Client - Python Version
Based on reverse engineering the track.bus.gi website

This module provides functions to access real-time Gibraltar bus tracking data.
"""

import requests
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class GibraltarBusAPI:
    """
    Gibraltar Bus Tracker API Client
    
    Provides access to real-time bus tracking data from Gibraltar's public transport system.
    """
    
    def __init__(self):
        self.base_url = "https://track.bus.gi"
        self.routes = ['1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_bus_data(self, route_id: str) -> Dict:
        """
        Get real-time bus data for a specific route.
        
        Args:
            route_id (str): Route ID ('1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S')
            
        Returns:
            dict: Bus tracking data including status, timestamp, and bus positions
        """
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
                'raw_html': content,
                'url': url
            }
            
            # Check if buses are available
            if "Bus Location is Currently Unavailable" in content:
                result['status'] = 'no_buses_active'
                return result
            
            # Extract timestamp
            timestamp_match = re.search(r'Last Updated: ([^-]+)', content)
            if timestamp_match:
                result['timestamp'] = timestamp_match.group(1).strip()
                result['status'] = 'active'
            
            # Extract bus positions (image references indicate bus locations)
            bus_pattern = rf"src='R{route_id}/c(\d+[a-z]*)\.png'"
            bus_matches = re.findall(bus_pattern, content)
            
            for bus_id in bus_matches:
                result['buses'].append({
                    'bus_id': bus_id,
                    'image_reference': f"R{route_id}/c{bus_id}.png",
                    'full_image_url': f"{self.base_url}/R{route_id}/c{bus_id}.png"
                })
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'route_id': route_id,
                'status': 'error',
                'error': str(e),
                'timestamp': None,
                'buses': [],
                'url': url
            }
    
    def get_all_routes_data(self) -> Dict[str, Dict]:
        """
        Get data for all available routes.
        
        Returns:
            dict: Dictionary with route IDs as keys and bus data as values
        """
        results = {}
        
        print("Fetching data for all Gibraltar bus routes...")
        
        for route in self.routes:
            print(f"Fetching Route {route}...")
            results[route] = self.get_bus_data(route)
            time.sleep(1)  # Be respectful to the server
        
        return results
    
    def show_status_report(self, bus_data: Dict[str, Dict]) -> None:
        """
        Display a formatted status report of all bus routes.
        
        Args:
            bus_data (dict): Bus data from get_all_routes_data()
        """
        print("\nGibraltar Bus Status Report")
        print("==========================")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        active_routes = 0
        total_buses = 0
        
        for route in sorted(bus_data.keys()):
            data = bus_data[route]
            print(f"\nRoute {route}:")
            
            if data['status'] == 'active':
                print(f"  Status: ACTIVE")
                print(f"  Last Updated: {data['timestamp']}")
                print(f"  Buses: {len(data['buses'])}")
                
                for bus in data['buses']:
                    print(f"    - Bus ID: {bus['bus_id']}")
                
                active_routes += 1
                total_buses += len(data['buses'])
                
            elif data['status'] == 'no_buses_active':
                print(f"  Status: NO BUSES ACTIVE")
                
            elif data['status'] == 'error':
                print(f"  Status: ERROR")
                print(f"  Error: {data['error']}")
        
        print(f"\nSummary:")
        print(f"--------")
        print(f"Active Routes: {active_routes}")
        print(f"Total Buses Tracked: {total_buses}")
    
    def export_data(self, bus_data: Dict[str, Dict], filename: Optional[str] = None) -> str:
        """
        Export bus data to a JSON file.
        
        Args:
            bus_data (dict): Bus data to export
            filename (str, optional): Output filename. If None, generates timestamp-based name.
            
        Returns:
            str: The filename used for export
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"gibraltar_bus_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(bus_data, f, indent=2, ensure_ascii=False)
        
        print(f"Bus data exported to: {filename}")
        return filename

def main():
    """
    Main function demonstrating the API usage.
    """
    print("Gibraltar Bus Tracker API Client")
    print("=================================")
    
    # Initialize API client
    api = GibraltarBusAPI()
    
    # Test individual route
    print("\nTesting individual route (Route 2)...")
    route2_data = api.get_bus_data("2")
    print(f"Route 2 Status: {route2_data['status']}")
    
    if route2_data['status'] == 'active':
        print(f"Buses found: {len(route2_data['buses'])}")
    
    # Test all routes
    print("\nTesting all routes...")
    all_data = api.get_all_routes_data()
    
    # Show status report
    api.show_status_report(all_data)
    
    # Export data
    export_file = api.export_data(all_data)
    
    print("\nAPI Information:")
    print("=================")
    print(f"Base URL: {api.base_url}")
    print("Endpoint: /busTracker.php?id={route_id}")
    print(f"Available Routes: {', '.join(api.routes)}")
    print("Update Frequency: Every 4 seconds (client-side)")
    print("Data Format: HTML with bus position images")
    
    print("\nNext Steps:")
    print("-----------")
    print("1. Use api.get_bus_data('route_id') for specific routes")
    print("2. Use api.get_all_routes_data() for all routes")
    print("3. Set up a scheduled task to monitor buses regularly")
    print("4. Parse bus image coordinates for exact GPS positions")
    
    return all_data

if __name__ == "__main__":
    main()