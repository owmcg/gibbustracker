"""
Comprehensive test suite for Gibraltar Bus API
Tests both the API client and Flask server endpoints
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from unittest.mock import Mock, patch
import json

# Sample HTML responses based on actual Gibraltar Bus Tracker behavior
MOCK_RESPONSES = {
    'route_2_active': '''
<html><body>
Last Updated: 07/10/2025 21:48:28 - Route 2
<img src='R2/c22a.png'>
<img src='R2/c6a.png'>
</body></html>
''',
    'route_1_inactive': '''
<html><body>
Bus Location is Currently Unavailable
</body></html>
''',
    'route_8_active': '''
<html><body>
Last Updated: 07/10/2025 21:48:31 - Route 8
<img src='R8/c10a.png'>
</body></html>
''',
    'route_3_inactive': '''
<html><body>
Bus Location is Currently Unavailable
</body></html>
''',
    'route_7_double_quotes': '''
<html><body>
Last Updated: 07/10/2025 22:00:00 - Route 7
<img src="R7/c15a.png">
<img src="R7/c20b.png">
</body></html>
'''
}


def mock_get(url, *args, **kwargs):
    """Mock requests.get to return predetermined responses"""
    response = Mock()
    response.status_code = 200
    
    # Determine which response to return based on route
    if 'id=2' in url:
        response.text = MOCK_RESPONSES['route_2_active']
    elif 'id=1' in url:
        response.text = MOCK_RESPONSES['route_1_inactive']
    elif 'id=8' in url:
        response.text = MOCK_RESPONSES['route_8_active']
    elif 'id=3' in url:
        response.text = MOCK_RESPONSES['route_3_inactive']
    elif 'id=7' in url:
        response.text = MOCK_RESPONSES['route_7_double_quotes']
    else:
        response.text = MOCK_RESPONSES['route_1_inactive']
    
    response.raise_for_status = Mock()
    return response


class TestGibraltarBusAPI(unittest.TestCase):
    """Test the Gibraltar Bus API client"""
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_bus_data_active_route(self, mock_request):
        """Test fetching data for an active route"""
        from gibraltar_bus_api import GibraltarBusAPI
        
        api = GibraltarBusAPI()
        result = api.get_bus_data('2')
        
        self.assertEqual(result['status'], 'active')
        self.assertEqual(result['route_id'], '2')
        self.assertEqual(len(result['buses']), 2)
        self.assertEqual(result['timestamp'], '07/10/2025 21:48:28')
        
        # Check bus details
        bus_ids = [bus['bus_id'] for bus in result['buses']]
        self.assertIn('22a', bus_ids)
        self.assertIn('6a', bus_ids)
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_bus_data_inactive_route(self, mock_request):
        """Test fetching data for an inactive route"""
        from gibraltar_bus_api import GibraltarBusAPI
        
        api = GibraltarBusAPI()
        result = api.get_bus_data('1')
        
        self.assertEqual(result['status'], 'no_buses_active')
        self.assertEqual(result['route_id'], '1')
        self.assertEqual(len(result['buses']), 0)
        self.assertIsNone(result['timestamp'])
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_bus_data_single_bus(self, mock_request):
        """Test fetching data for a route with one bus"""
        from gibraltar_bus_api import GibraltarBusAPI
        
        api = GibraltarBusAPI()
        result = api.get_bus_data('8')
        
        self.assertEqual(result['status'], 'active')
        self.assertEqual(len(result['buses']), 1)
        self.assertEqual(result['buses'][0]['bus_id'], '10a')
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_bus_data_double_quotes(self, mock_request):
        """Test fetching data with double quotes in HTML (regression test)"""
        from gibraltar_bus_api import GibraltarBusAPI
        
        api = GibraltarBusAPI()
        result = api.get_bus_data('7')
        
        self.assertEqual(result['status'], 'active')
        self.assertEqual(len(result['buses']), 2)
        
        # Check bus details
        bus_ids = [bus['bus_id'] for bus in result['buses']]
        self.assertIn('15a', bus_ids)
        self.assertIn('20b', bus_ids)


class TestFlaskServer(unittest.TestCase):
    """Test the Flask server endpoints"""
    
    @patch('requests.Session.get', side_effect=mock_get)
    def setUp(self, mock_request):
        """Set up test client"""
        # Prevent background scheduler from starting
        import server
        try:
            server.scheduler.shutdown(wait=False)
        except:
            pass  # Scheduler not running, which is fine for tests
        
        from server import app
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_routes(self, mock_request):
        """Test /api/routes endpoint"""
        response = self.app.get('/api/routes')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['routes']), 9)
        self.assertIn('1', data['routes'])
        self.assertIn('2', data['routes'])
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_specific_route_active(self, mock_request):
        """Test /api/buses/<route_id> for active route"""
        response = self.app.get('/api/buses/2')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'active')
        self.assertEqual(len(data['data']['buses']), 2)
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_specific_route_inactive(self, mock_request):
        """Test /api/buses/<route_id> for inactive route"""
        response = self.app.get('/api/buses/1')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['status'], 'no_buses_active')
        self.assertEqual(len(data['data']['buses']), 0)
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_invalid_route(self, mock_request):
        """Test /api/buses/<route_id> with invalid route"""
        response = self.app.get('/api/buses/99')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    @patch('requests.Session.get', side_effect=mock_get)
    def test_get_all_buses(self, mock_request):
        """Test /api/buses endpoint"""
        response = self.app.get('/api/buses')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], dict)
        
        # Verify we get data for all routes
        self.assertIn('1', data['data'])
        self.assertIn('2', data['data'])
        self.assertIn('8', data['data'])


class TestAPIErrorHandling(unittest.TestCase):
    """Test error handling in the API"""
    
    def test_network_error_handling(self):
        """Test handling of network errors"""
        from gibraltar_bus_api import GibraltarBusAPI
        
        def mock_get_error(*args, **kwargs):
            import requests
            raise requests.exceptions.ConnectionError("Network error")
        
        with patch('requests.Session.get', side_effect=mock_get_error):
            api = GibraltarBusAPI()
            result = api.get_bus_data('2')
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('error', result)
            self.assertEqual(len(result['buses']), 0)
    
    def test_timeout_error_handling(self):
        """Test handling of timeout errors"""
        from gibraltar_bus_api import GibraltarBusAPI
        
        def mock_get_timeout(*args, **kwargs):
            import requests
            raise requests.exceptions.Timeout("Request timeout")
        
        with patch('requests.Session.get', side_effect=mock_get_timeout):
            api = GibraltarBusAPI()
            result = api.get_bus_data('2')
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('error', result)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
