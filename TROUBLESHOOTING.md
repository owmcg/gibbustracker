# Bus API Troubleshooting Guide

## Issue: Buses Not Being Fetched Properly

This guide helps diagnose and fix issues when buses aren't being detected.

## Recent Fixes

### 1. **Regex Pattern Bug Fixed** ✅
- **Problem**: The regex pattern only matched single quotes (`'`), missing buses in HTML with double quotes (`"`)
- **Solution**: Updated pattern to handle both quote styles and be case-insensitive
- **Pattern**: `src=['\"]R{route_id}/c(\d+[a-z]*)\.png['\"]` with `re.IGNORECASE`

### 2. **Logging Added** ✅
- Added detailed logging to help debug fetching issues
- Logs show: route fetches, bus counts, errors, and cache hits

### 3. **Diagnostic Endpoint Added** ✅
- New endpoint: `GET /api/diagnostic/<route_id>`
- Shows detailed analysis of HTML response
- Compares different regex patterns
- Displays HTML preview for debugging

## How to Diagnose Issues

### Step 1: Check Server Logs
```bash
# Run the server and check logs
python server.py

# Look for log messages like:
# - "Route 2: Found 2 buses - Status: active"
# - "Route 1: No buses currently active"
# - "Error fetching route X: ..."
```

### Step 2: Use Diagnostic Endpoint
```bash
# Test a specific route
curl http://localhost:5000/api/diagnostic/2

# Check the response:
{
  "diagnostic": {
    "buses_found_robust": 2,          # Should match actual buses
    "has_unavailable_message": false, # True if no buses active
    "has_timestamp": true,            # True if buses are active
    "html_preview": "..."             # Shows actual HTML received
  }
}
```

### Step 3: Test with Mock Data
```bash
# Run the test suite
python test_api.py

# All tests should pass
```

## Common Issues and Solutions

### Issue 1: No Buses Detected (But They Exist)
**Symptoms**: 
- API returns `buses: []` 
- Diagnostic shows `buses_found_robust: 0` but `has_unavailable_message: false`

**Causes**:
1. HTML format changed on server
2. New quote style in HTML
3. Bus ID pattern changed

**Solution**:
1. Check diagnostic endpoint for HTML preview
2. Verify bus image pattern in HTML
3. Update regex pattern if needed

### Issue 2: Network/Connection Errors
**Symptoms**: 
- `status: 'error'` 
- Error message: "Failed to resolve 'track.bus.gi'"

**Causes**:
1. DNS resolution issues
2. Firewall blocking requests
3. Server is down

**Solution**:
1. Test connectivity: `curl https://track.bus.gi/busTracker.php?id=2`
2. Check firewall settings
3. Verify server is accessible

### Issue 3: All Routes Show "No Buses Active"
**Symptoms**: 
- All routes return `status: 'no_buses_active'`
- This might be correct if no buses are running

**Solution**:
1. Check the actual Gibraltar Bus Tracker website
2. Verify bus operating hours
3. Use diagnostic endpoint to see actual HTML

## Testing the Fix

### Run Automated Tests
```bash
python test_api.py
```

### Test with Mock Server
```bash
python -c "
import sys
sys.path.insert(0, '.')
from unittest.mock import Mock, patch

def mock_get(url, *args, **kwargs):
    response = Mock()
    response.status_code = 200
    response.text = '''<html><body>
Last Updated: 07/10/2025 21:48:28 - Route 2
<img src=\"R2/c22a.png\">
</body></html>'''
    response.raise_for_status = Mock()
    return response

with patch('requests.Session.get', side_effect=mock_get):
    from gibraltar_bus_api import GibraltarBusAPI
    api = GibraltarBusAPI()
    result = api.get_bus_data('2')
    print(f'Status: {result[\"status\"]}, Buses: {len(result[\"buses\"])}')
"
```

### Expected Output
```
Status: active, Buses: 1
```

## API Improvements Summary

1. **Robust Pattern Matching** ✅
   - Handles both `'` and `"` quotes
   - Case-insensitive matching
   - More reliable bus detection

2. **Better Error Handling** ✅
   - Detailed error messages
   - Request/response logging
   - Helpful diagnostic info

3. **Diagnostic Tools** ✅
   - `/api/diagnostic/<route_id>` endpoint
   - Shows what patterns match
   - HTML preview for debugging

4. **Comprehensive Testing** ✅
   - Unit tests for all scenarios
   - Mock data testing
   - Regression tests

## Support

If buses still aren't being fetched:
1. Run diagnostic endpoint: `GET /api/diagnostic/<route_id>`
2. Check server logs for errors
3. Verify connectivity to track.bus.gi
4. Compare HTML preview with expected format
