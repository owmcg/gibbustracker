# Gibraltar Bus Tracker API Client - PowerShell Version
# Based on reverse engineering the track.bus.gi website

function Get-GibraltarBusData {
    param(
        [Parameter(Mandatory=$true)]
        [string]$RouteId
    )
    
    $baseUrl = "https://track.bus.gi"
    $url = "$baseUrl/busTracker.php?id=$RouteId"
    
    try {
        $response = Invoke-WebRequest -Uri $url -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" -TimeoutSec 10
        $content = $response.Content
        
        $result = @{
            route_id = $RouteId
            status = "unknown"
            timestamp = $null
            buses = @()
            raw_html = $content
            url = $url
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
        $busPattern = "src='R$RouteId/c(\d+[a-z]*)\.png'"
        $busMatches = [regex]::Matches($content, $busPattern)
        
        foreach ($match in $busMatches) {
            $busId = $match.Groups[1].Value
            $result.buses += @{
                bus_id = $busId
                image_reference = $match.Groups[0].Value
                full_image_url = "$baseUrl/R$RouteId/c$busId.png"
            }
        }
        
        return $result
        
    } catch {
        return @{
            route_id = $RouteId
            status = "error"
            error = $_.Exception.Message
            timestamp = $null
            buses = @()
            url = $url
        }
    }
}

function Get-AllGibraltarBusData {
    $routes = @('1', '2', '3', '7', '8', '9', 'N1', 'N8E', 'N8S')
    $results = @{}
    
    Write-Host "Fetching data for all Gibraltar bus routes..." -ForegroundColor Green
    
    foreach ($route in $routes) {
        Write-Host "Fetching Route $route..." -ForegroundColor Cyan
        $results[$route] = Get-GibraltarBusData -RouteId $route
        Start-Sleep -Seconds 1  # Be respectful to the server
    }
    
    return $results
}

function Show-GibraltarBusStatus {
    param(
        [hashtable]$BusData
    )
    
    Write-Host "`nGibraltar Bus Status Report" -ForegroundColor Green
    Write-Host "==========================" -ForegroundColor Green
    Write-Host "Generated: $(Get-Date)" -ForegroundColor Yellow
    
    $activeRoutes = 0
    $totalBuses = 0
    
    foreach ($route in $BusData.Keys | Sort-Object) {
        $data = $BusData[$route]
        Write-Host "`nRoute $route`:" -ForegroundColor Cyan
        
        switch ($data.status) {
            "active" {
                Write-Host "  Status: ACTIVE" -ForegroundColor Green
                Write-Host "  Last Updated: $($data.timestamp)" -ForegroundColor White
                Write-Host "  Buses: $($data.buses.Count)" -ForegroundColor Yellow
                
                foreach ($bus in $data.buses) {
                    Write-Host "    - Bus ID: $($bus.bus_id)" -ForegroundColor White
                }
                
                $activeRoutes++
                $totalBuses += $data.buses.Count
            }
            "no_buses_active" {
                Write-Host "  Status: NO BUSES ACTIVE" -ForegroundColor Gray
            }
            "error" {
                Write-Host "  Status: ERROR" -ForegroundColor Red
                Write-Host "  Error: $($data.error)" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "`n" -NoNewline
    Write-Host "Summary:" -ForegroundColor Green
    Write-Host "--------" -ForegroundColor Green
    Write-Host "Active Routes: $activeRoutes" -ForegroundColor Yellow
    Write-Host "Total Buses Tracked: $totalBuses" -ForegroundColor Yellow
}

function Export-GibraltarBusData {
    param(
        [hashtable]$BusData,
        [string]$FilePath = "gibraltar_bus_data_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    )
    
    $BusData | ConvertTo-Json -Depth 10 | Out-File -FilePath $FilePath -Encoding UTF8
    Write-Host "Bus data exported to: $FilePath" -ForegroundColor Green
}

# Test and demonstration function
function Test-GibraltarBusAPI {
    Write-Host "Gibraltar Bus Tracker API Test" -ForegroundColor Green
    Write-Host "===============================" -ForegroundColor Green
    
    # Test individual route
    Write-Host "`nTesting individual route (Route 2)..." -ForegroundColor Yellow
    $route2Data = Get-GibraltarBusData -RouteId "2"
    Write-Host "Route 2 Status: $($route2Data.status)" -ForegroundColor Cyan
    
    if ($route2Data.status -eq "active") {
        Write-Host "Buses found: $($route2Data.buses.Count)" -ForegroundColor Green
    }
    
    # Test all routes
    Write-Host "`nTesting all routes..." -ForegroundColor Yellow
    $allData = Get-AllGibraltarBusData
    
    # Show status report
    Show-GibraltarBusStatus -BusData $allData
    
    # Export data
    $exportFile = "gibraltar_bus_data_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    Export-GibraltarBusData -BusData $allData -FilePath $exportFile
    
    Write-Host "`n" -NoNewline
    Write-Host "API Information:" -ForegroundColor Green
    Write-Host "=================" -ForegroundColor Green
    Write-Host "Base URL: https://track.bus.gi" -ForegroundColor White
    Write-Host "Endpoint: /busTracker.php?id={route_id}" -ForegroundColor White
    Write-Host "Available Routes: 1, 2, 3, 7, 8, 9, N1, N8E, N8S" -ForegroundColor White
    Write-Host "Update Frequency: Every 4 seconds (client-side)" -ForegroundColor White
    Write-Host "Data Format: HTML with bus position images" -ForegroundColor White
    
    return $allData
}

# Main execution
Write-Host "Gibraltar Bus Tracker API Client" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Run the test
$busData = Test-GibraltarBusAPI

Write-Host "`n" -NoNewline
Write-Host "Next Steps:" -ForegroundColor Green
Write-Host "-----------" -ForegroundColor Green
Write-Host "1. Use Get-GibraltarBusData -RouteId 'X' for specific routes" -ForegroundColor White
Write-Host "2. Use Get-AllGibraltarBusData for all routes" -ForegroundColor White
Write-Host "3. Set up a scheduled task to monitor buses regularly" -ForegroundColor White
Write-Host "4. Parse bus image coordinates for exact GPS positions" -ForegroundColor White