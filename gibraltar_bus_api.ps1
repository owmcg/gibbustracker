# Gibraltar Bus Tracker API Client
# Based on reverse engineering the track.bus.gi website

class GibraltarBusAPI:
    def __init__(self):
        self.base_url = "https://track.bus.gi"
        self.routes = ['1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S']
    
    def get_bus_data(self, route_id):
        """
        Get real-time bus data for a specific route.
        
        Args:
            route_id (str): Route ID ('1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S')
            
        Returns:
            dict: Bus tracking data including status, timestamp, and bus positions
        """
        try:
            $url = "$($this.base_url)/busTracker.php?id=$route_id"
            $response = Invoke-WebRequest -Uri $url -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" -TimeoutSec 10
            
            $content = $response.Content
            
            # Parse the response
            $result = @{
                route_id = $route_id
                status = "unknown"
                timestamp = $null
                buses = @()
                raw_html = $content
            }
            
            # Check if buses are available
            if ($content -match "Bus Location is Currently Unavailable") {
                $result.status = "no_buses_active"
                return $result
            }
            
            # Extract timestamp
            if ($content -match "Last Updated: ([^-]+)") {
                $result.timestamp = $matches[1].Trim()
                $result.status = "active"
            }
            
            # Extract bus positions (image references indicate bus locations)
            $busPattern = "src='R$route_id/c(\d+[a-z]*)\.png'"
            $busMatches = [regex]::Matches($content, $busPattern)
            
            foreach ($match in $busMatches) {
                $busId = $match.Groups[1].Value
                $result.buses += @{
                    bus_id = $busId
                    image_reference = $match.Groups[0].Value
                }
            }
            
            return $result
            
        } catch {
            return @{
                route_id = $route_id
                status = "error"
                error = $_.Exception.Message
                timestamp = $null
                buses = @()
            }
        }
    }
    
    def get_all_routes_data(self):
        """Get data for all available routes"""
        $results = @{}
        
        foreach ($route in $this.routes) {
            Write-Host "Fetching data for Route $route..." -ForegroundColor Cyan
            $results[$route] = $this.get_bus_data($route)
            Start-Sleep -Seconds 1  # Be respectful to the server
        }
        
        return $results
    }
}

# Usage example and testing function
function Test-GibraltarBusAPI {
    Write-Host "Gibraltar Bus Tracker API Test" -ForegroundColor Green
    Write-Host "===============================" -ForegroundColor Green
    
    $api = [GibraltarBusAPI]::new()
    
    # Test all routes
    Write-Host "`nTesting all routes..." -ForegroundColor Yellow
    
    foreach ($route in $api.routes) {
        Write-Host "`nRoute $route:" -ForegroundColor Cyan
        
        try {
            $url = "$($api.base_url)/busTracker.php?id=$route"
            $response = Invoke-WebRequest -Uri $url -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" -TimeoutSec 10
            
            $content = $response.Content
            
            if ($content -match "Bus Location is Currently Unavailable") {
                Write-Host "  Status: No buses active" -ForegroundColor Gray
            } else {
                Write-Host "  Status: Active buses detected!" -ForegroundColor Green
                
                # Extract timestamp
                if ($content -match "Last Updated: ([^-]+)") {
                    Write-Host "  Last Updated: $($matches[1].Trim())" -ForegroundColor White
                }
                
                # Extract bus references
                $busPattern = "src='R$route/c(\d+[a-z]*)\.png'"
                $busMatches = [regex]::Matches($content, $busPattern)
                
                if ($busMatches.Count -gt 0) {
                    Write-Host "  Buses detected: $($busMatches.Count)" -ForegroundColor Yellow
                    foreach ($match in $busMatches) {
                        $busId = $match.Groups[1].Value
                        Write-Host "    - Bus ID: $busId" -ForegroundColor White
                    }
                }
            }
            
        } catch {
            Write-Host "  Status: Error - $($_.Exception.Message)" -ForegroundColor Red
        }
        
        Start-Sleep -Seconds 1
    }
    
    Write-Host "`n" -NoNewline
    Write-Host "API Test Complete!" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host "`nAPI Endpoint Discovery:"
    Write-Host "- Base URL: $($api.base_url)"
    Write-Host "- Bus Data Endpoint: {base_url}/busTracker.php?id={route_id}"
    Write-Host "- Available Routes: $($api.routes -join ', ')"
    Write-Host "- Update Frequency: Every 4 seconds (based on JavaScript)"
    Write-Host "`nData Format:"
    Write-Host "- Returns HTML with embedded bus position images"
    Write-Host "- Image names correspond to bus IDs/positions"
    Write-Host "- Timestamp included when buses are active"
}

# Run the test
Test-GibraltarBusAPI