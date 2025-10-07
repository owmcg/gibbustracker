import requests
import re
import json
from bs4 import BeautifulSoup
import time
from datetime import datetime

class GibraltarBusScraper:
    def __init__(self):
        self.base_url = "https://track.bus.gi"
        self.session = requests.Session()
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Available routes based on the website
        self.routes = ['1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S']
    
    def get_route_data(self, route_id):
        """Fetch data for a specific route"""
        try:
            url = f"{self.base_url}/displayRoute.php?id={route_id}&sys=1"
            print(f"Fetching data for Route {route_id}: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            print(f"Response status: {response.status_code}")
            print(f"Content type: {response.headers.get('content-type', 'Unknown')}")
            print(f"Content length: {len(response.text)} characters")
            
            return {
                'route_id': route_id,
                'url': url,
                'status_code': response.status_code,
                'content': response.text,
                'headers': dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching route {route_id}: {e}")
            return None
    
    def analyze_page_content(self, route_data):
        """Analyze the page content to find bus location data"""
        if not route_data:
            return None
            
        content = route_data['content']
        route_id = route_data['route_id']
        
        print(f"\n=== Analyzing Route {route_id} ===")
        
        # Look for JavaScript variables that might contain bus data
        js_patterns = [
            r'var\s+\w+\s*=\s*\[.*?\];',  # JavaScript arrays
            r'var\s+\w+\s*=\s*\{.*?\};',  # JavaScript objects
            r'\[\s*-?\d+\.\d+\s*,\s*-?\d+\.\d+\s*\]',  # Coordinate arrays
            r'lat\s*:\s*-?\d+\.\d+',  # Latitude values
            r'lng\s*:\s*-?\d+\.\d+',  # Longitude values
            r'longitude\s*:\s*-?\d+\.\d+',
            r'latitude\s*:\s*-?\d+\.\d+'
        ]
        
        findings = {}
        
        for i, pattern in enumerate(js_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                findings[f'pattern_{i+1}'] = matches[:5]  # Limit to first 5 matches
        
        # Look for potential API endpoints
        api_patterns = [
            r'fetch\([\'"`]([^\'"`]+)[\'"`]\)',
            r'xhr\.open\([\'"`]\w+[\'"`],\s*[\'"`]([^\'"`]+)[\'"`]',
            r'\.ajax\(\s*\{\s*url\s*:\s*[\'"`]([^\'"`]+)[\'"`]',
            r'https?://[^\s\'"<>]+\.php[^\s\'"<>]*'
        ]
        
        for i, pattern in enumerate(api_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                findings[f'api_pattern_{i+1}'] = matches[:3]
        
        # Check for embedded coordinates
        coord_pattern = r'(-?\d+\.\d{4,})\s*,\s*(-?\d+\.\d{4,})'
        coord_matches = re.findall(coord_pattern, content)
        if coord_matches:
            findings['coordinates'] = coord_matches[:10]
        
        # Look for image paths that might indicate bus positions
        img_pattern = r'src=[\'"`]([^\'"`]*(?:bus|marker|icon)[^\'"`]*)[\'"`]'
        img_matches = re.findall(img_pattern, content, re.IGNORECASE)
        if img_matches:
            findings['bus_images'] = img_matches[:5]
        
        return findings
    
    def extract_scripts_and_network_calls(self, route_data):
        """Extract all script tags and potential network calls"""
        if not route_data:
            return None
            
        soup = BeautifulSoup(route_data['content'], 'html.parser')
        
        # Extract all script tags
        scripts = []
        for script in soup.find_all('script'):
            if script.string:
                scripts.append(script.string.strip())
        
        # Look for potential AJAX endpoints in scripts
        ajax_endpoints = []
        for script in scripts:
            # Common AJAX patterns
            ajax_patterns = [
                r'[\'"`]([^\'"`]*\.php[^\'"`]*)[\'"`]',
                r'url\s*:\s*[\'"`]([^\'"`]+)[\'"`]',
                r'fetch\([\'"`]([^\'"`]+)[\'"`]\)'
            ]
            
            for pattern in ajax_patterns:
                matches = re.findall(pattern, script)
                ajax_endpoints.extend(matches)
        
        return {
            'scripts': scripts,
            'potential_endpoints': list(set(ajax_endpoints))
        }
    
    def scan_all_routes(self):
        """Scan all available routes"""
        results = {}
        
        print("Starting Gibraltar Bus Tracker scan...")
        print(f"Available routes: {', '.join(self.routes)}")
        print("-" * 50)
        
        for route_id in self.routes:
            print(f"\nScanning Route {route_id}...")
            
            # Get route data
            route_data = self.get_route_data(route_id)
            if route_data:
                # Analyze content
                analysis = self.analyze_page_content(route_data)
                scripts_data = self.extract_scripts_and_network_calls(route_data)
                
                results[route_id] = {
                    'basic_info': {
                        'url': route_data['url'],
                        'status': route_data['status_code'],
                        'content_length': len(route_data['content'])
                    },
                    'analysis': analysis,
                    'scripts': scripts_data
                }
                
                # Print findings for this route
                if analysis:
                    print(f"Found {len(analysis)} types of patterns")
                    for key, value in analysis.items():
                        if value:
                            print(f"  {key}: {len(value)} matches")
            
            # Be respectful to the server
            time.sleep(1)
        
        return results
    
    def save_results(self, results):
        """Save results to a JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gibraltar_bus_scan_{timestamp}.json"
        
        # Convert results to a more JSON-friendly format
        json_results = {}
        for route_id, data in results.items():
            json_results[route_id] = data
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {filename}")
        return filename

def main():
    scraper = GibraltarBusScraper()
    
    print("Gibraltar Bus Tracker Data Extraction")
    print("=" * 40)
    
    # Scan all routes
    results = scraper.scan_all_routes()
    
    # Save results
    filename = scraper.save_results(results)
    
    # Print summary
    print("\n" + "=" * 40)
    print("SCAN SUMMARY")
    print("=" * 40)
    
    for route_id, data in results.items():
        if data:
            print(f"Route {route_id}:")
            print(f"  Status: {data['basic_info']['status']}")
            print(f"  Content Length: {data['basic_info']['content_length']} chars")
            
            if data['analysis']:
                interesting_findings = []
                for key, value in data['analysis'].items():
                    if value and len(value) > 0:
                        interesting_findings.append(f"{key}: {len(value)} items")
                
                if interesting_findings:
                    print(f"  Findings: {', '.join(interesting_findings)}")
            print()
    
    print(f"Detailed results saved to: {filename}")
    print("\nNext steps:")
    print("1. Review the JSON file for potential API endpoints")
    print("2. Look for coordinate patterns that might indicate bus positions")
    print("3. Check for JavaScript functions that update bus locations")

if __name__ == "__main__":
    main()